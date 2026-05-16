from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.api.dependencies import get_db, get_current_user
from app.schemas.family import (
    FamilyCreate, FamilyUpdate, FamilyResponse, FamilyDetailResponse,
    FamilyMemberResponse, FamilyMembersListResponse, InvitationCreate,
    InvitationResponse, InvitationAccept, InvitationAcceptResponse
)
from app.models import User, Family, FamilyMember, Invitation
from app.utils.exceptions import NotFoundException, ForbiddenException, ConflictException
from app.utils.security import create_access_token, hash_password
from datetime import datetime, timedelta
import uuid

router = APIRouter()

# Helpers
def get_user_role_in_family(user_id: int, family_id: int, db: Session) -> str:
    member = db.query(FamilyMember).filter(
        and_(FamilyMember.family_id == family_id, FamilyMember.user_id == user_id)
    ).first()
    return member.role if member else None

@router.get("", response_model=dict)
def list_families(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    members = db.query(FamilyMember).filter(
        FamilyMember.user_id == current_user.id
    ).all()
    families = []
    for member in members:
        family = member.family
        member_count = db.query(FamilyMember).filter(
            and_(FamilyMember.family_id == family.id, FamilyMember.status == "active")
        ).count()
        families.append({
            "id": family.id,
            "name": family.name,
            "description": family.description,
            "currency": family.currency,
            "role": member.role,
            "member_count": member_count,
            "created_at": family.created_at
        })
    return {"families": families}

@router.get("/{family_id}", response_model=FamilyDetailResponse)
def get_family(
    family_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    family = db.query(Family).filter(Family.id == family_id).first()
    if not family:
        raise NotFoundException("Family not found")

    role = get_user_role_in_family(current_user.id, family_id, db)
    if not role:
        raise ForbiddenException("User not a member of this family")

    return FamilyDetailResponse.from_orm(family)

@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_family(
    payload: FamilyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "superadmin":
        raise ForbiddenException("Only superadmin can create families")

    family = Family(
        name=payload.name,
        description=payload.description,
        currency=payload.currency,
        created_by_user_id=current_user.id
    )
    db.add(family)
    db.flush()

    # Add owner as member
    if payload.owner_email:
        owner = db.query(User).filter(User.email == payload.owner_email).first()
        if owner:
            member = FamilyMember(
                family_id=family.id,
                user_id=owner.id,
                role="owner",
                status="active",
                joined_at=datetime.utcnow()
            )
            db.add(member)

            # Create invitation for notification
            invitation = Invitation(
                email=payload.owner_email,
                family_id=family.id,
                token=uuid.uuid4(),
                invited_by_user_id=current_user.id,
                expires_at=datetime.utcnow() + timedelta(days=30)
            )
            db.add(invitation)

    db.commit()
    return {"id": family.id, "name": family.name, "created_at": family.created_at}

@router.put("/{family_id}", response_model=FamilyDetailResponse)
def update_family(
    family_id: int,
    payload: FamilyUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    family = db.query(Family).filter(Family.id == family_id).first()
    if not family:
        raise NotFoundException("Family not found")

    if get_user_role_in_family(current_user.id, family_id, db) != "owner":
        raise ForbiddenException("Only owner can update family")

    if payload.name:
        family.name = payload.name
    if payload.description is not None:
        family.description = payload.description

    db.commit()
    return FamilyDetailResponse.from_orm(family)

@router.get("/{family_id}/members", response_model=FamilyMembersListResponse)
def get_family_members(
    family_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    family = db.query(Family).filter(Family.id == family_id).first()
    if not family:
        raise NotFoundException("Family not found")

    if not get_user_role_in_family(current_user.id, family_id, db):
        raise ForbiddenException("User not a member of this family")

    members = db.query(FamilyMember).filter(FamilyMember.family_id == family_id).all()
    result = []
    for member in members:
        user_info = member.user if member.user else None
        result.append({
            "id": member.id,
            "user_id": member.user_id,
            "email": user_info.email if user_info else member.email,
            "full_name": user_info.full_name if user_info else None,
            "role": member.role,
            "status": member.status,
            "joined_at": member.joined_at,
            "expires_at": None
        })

    return {"members": result}

@router.post("/{family_id}/members", response_model=InvitationResponse, status_code=status.HTTP_201_CREATED)
def invite_member(
    family_id: int,
    payload: InvitationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    family = db.query(Family).filter(Family.id == family_id).first()
    if not family:
        raise NotFoundException("Family not found")

    if get_user_role_in_family(current_user.id, family_id, db) != "owner":
        raise ForbiddenException("Only owner can invite members")

    existing = db.query(FamilyMember).filter(
        and_(FamilyMember.family_id == family_id, FamilyMember.user_id != None)
    ).join(User).filter(User.email == payload.email).first()

    if existing:
        raise ConflictException("Email already a member of this family")

    invitation = Invitation(
        email=payload.email,
        family_id=family_id,
        token=uuid.uuid4(),
        invited_by_user_id=current_user.id,
        expires_at=datetime.utcnow() + timedelta(days=30)
    )
    db.add(invitation)
    db.commit()

    return InvitationResponse.from_orm(invitation)

@router.delete("/{family_id}/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_member(
    family_id: int,
    member_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if get_user_role_in_family(current_user.id, family_id, db) != "owner":
        raise ForbiddenException("Only owner can remove members")

    member = db.query(FamilyMember).filter(
        and_(FamilyMember.id == member_id, FamilyMember.family_id == family_id)
    ).first()
    if not member:
        raise NotFoundException("Family member not found")

    db.delete(member)
    db.commit()

@router.post("/invitations/{token}/accept", response_model=InvitationAcceptResponse)
def accept_invitation(
    token: str,
    payload: InvitationAccept,
    db: Session = Depends(get_db)
):
    invitation = db.query(Invitation).filter(Invitation.token == token).first()
    if not invitation or invitation.status != "pending":
        raise ConflictException("Invalid or expired invitation")

    if invitation.expires_at < datetime.utcnow():
        raise ConflictException("Invitation has expired")

    user = db.query(User).filter(User.email == invitation.email).first()

    if not user:
        if not payload.password or not payload.full_name:
            raise ConflictException("Password and full_name required for new user")
        user = User(
            email=invitation.email,
            password_hash=hash_password(payload.password),
            full_name=payload.full_name,
            role="member"
        )
        db.add(user)
        db.flush()
    else:
        existing_member = db.query(FamilyMember).filter(
            and_(FamilyMember.family_id == invitation.family_id, FamilyMember.user_id == user.id)
        ).first()
        if existing_member:
            raise ConflictException("User already a member of this family")

    member = FamilyMember(
        family_id=invitation.family_id,
        user_id=user.id,
        role="member",
        status="active",
        joined_at=datetime.utcnow()
    )
    db.add(member)
    invitation.status = "accepted"
    db.commit()

    access_token = create_access_token({"sub": user.id})
    return {
        "success": True,
        "family_id": invitation.family_id,
        "family_name": invitation.family.name,
        "access_token": access_token,
        "user": {"id": user.id, "email": user.email, "full_name": user.full_name}
    }

@router.post("/invitations/{token}/decline", response_model=dict)
def decline_invitation(token: str, db: Session = Depends(get_db)):
    invitation = db.query(Invitation).filter(Invitation.token == token).first()
    if not invitation:
        raise NotFoundException("Invitation not found")

    invitation.status = "declined"
    db.commit()

    return {"success": True, "message": "Invitation declined"}
