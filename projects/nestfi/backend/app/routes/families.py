from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from uuid import UUID
import uuid as uuid_mod
from app.database import get_db
from app.models.user import User
from app.models.family import Family, FamilyMembership, RoleEnum, StatusEnum
from app.schemas.family import FamilySchema, FamilyListResponse
from app.dependencies import get_current_user
from app.utils.security import hash_password

router = APIRouter(prefix="/families", tags=["families"])


class CreateFamilyRequest(BaseModel):
    name: str


@router.get("", response_model=FamilyListResponse)
async def list_families(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    memberships = db.query(FamilyMembership).filter(
        FamilyMembership.user_id == current_user.id
    ).all()

    families = []
    for membership in memberships:
        family = db.query(Family).filter(Family.id == membership.family_id).first()
        if family:
            families.append(FamilySchema(
                id=family.id,
                name=family.name,
                owner_id=family.owner_id,
                role=membership.role.value,
                created_at=family.created_at
            ))

    return FamilyListResponse(families=families)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_family(
    request: CreateFamilyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user.is_superadmin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Superadmin only")

    family = Family(
        id=uuid_mod.uuid4(),
        name=request.name,
        owner_id=current_user.id,
    )
    db.add(family)

    membership = FamilyMembership(
        id=uuid_mod.uuid4(),
        family_id=family.id,
        user_id=current_user.id,
        role=RoleEnum.owner,
    )
    db.add(membership)
    db.commit()
    db.refresh(family)

    return {
        "id": str(family.id),
        "name": family.name,
        "owner_id": str(family.owner_id),
        "created_at": family.created_at,
    }


class RenameFamilyRequest(BaseModel):
    name: str


@router.get("/{family_id}")
async def get_family(
    family_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    family = db.query(Family).filter(Family.id == family_id).first()
    if not family:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Family not found")

    if not family.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Family is disabled")

    membership = db.query(FamilyMembership).filter(
        FamilyMembership.family_id == family_id,
        FamilyMembership.user_id == current_user.id
    ).first()

    if not membership:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a member")

    return {
        "id": str(family.id),
        "name": family.name,
        "owner_id": str(family.owner_id),
        "is_active": family.is_active,
        "member_count": db.query(FamilyMembership).filter(
            FamilyMembership.family_id == family_id
        ).count(),
        "account_count": 0,
        "created_at": family.created_at
    }


@router.put("/{family_id}")
async def rename_family(
    family_id: UUID,
    request: RenameFamilyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    family = db.query(Family).filter(Family.id == family_id).first()
    if not family:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Family not found")

    is_owner = db.query(FamilyMembership).filter(
        FamilyMembership.family_id == family_id,
        FamilyMembership.user_id == current_user.id,
        FamilyMembership.role == RoleEnum.owner,
    ).first()

    if not is_owner and not current_user.is_superadmin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Owner or superadmin only")

    family.name = request.name
    db.commit()
    db.refresh(family)

    return {
        "id": str(family.id),
        "name": family.name,
        "owner_id": str(family.owner_id),
        "created_at": family.created_at,
        "updated_at": family.updated_at,
    }


@router.get("/{family_id}/members")
async def list_family_members(
    family_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    caller_membership = db.query(FamilyMembership).filter(
        FamilyMembership.family_id == family_id,
        FamilyMembership.user_id == current_user.id,
    ).first()

    if not caller_membership and not current_user.is_superadmin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a member")

    memberships = db.query(FamilyMembership).filter(
        FamilyMembership.family_id == family_id,
        FamilyMembership.status == StatusEnum.active,
    ).all()

    members = []
    for m in memberships:
        user = db.query(User).filter(User.id == m.user_id).first()
        if user:
            members.append({
                "user_id": str(user.id),
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": m.role.value,
                "joined_at": m.joined_at,
            })

    return {"members": members}


class AddMemberRequest(BaseModel):
    email: str
    first_name: str
    last_name: str
    password: str


@router.post("/{family_id}/members", status_code=status.HTTP_201_CREATED)
async def add_member(
    family_id: UUID,
    request: AddMemberRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    is_owner = db.query(FamilyMembership).filter(
        FamilyMembership.family_id == family_id,
        FamilyMembership.user_id == current_user.id,
        FamilyMembership.role == RoleEnum.owner,
    ).first()
    if not is_owner:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Owner only")

    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        user = User(
            id=uuid_mod.uuid4(),
            email=request.email,
            first_name=request.first_name,
            last_name=request.last_name,
            password_hash=hash_password(request.password),
        )
        db.add(user)
        db.flush()

    existing = db.query(FamilyMembership).filter(
        FamilyMembership.family_id == family_id,
        FamilyMembership.user_id == user.id,
    ).first()
    if existing:
        if existing.status == StatusEnum.disabled:
            existing.status = StatusEnum.active
            db.commit()
        return {
            "user_id": str(user.id),
            "email": user.email,
            "role": existing.role.value,
            "family_id": str(family_id),
        }

    membership = FamilyMembership(
        id=uuid_mod.uuid4(),
        family_id=family_id,
        user_id=user.id,
        role=RoleEnum.member,
        status=StatusEnum.active,
    )
    db.add(membership)
    db.commit()

    return {
        "user_id": str(user.id),
        "email": user.email,
        "role": membership.role.value,
        "family_id": str(family_id),
    }


class UpdateMemberStatusRequest(BaseModel):
    status: str


@router.patch("/{family_id}/members/{user_id}")
async def update_member_status(
    family_id: UUID,
    user_id: UUID,
    request: UpdateMemberStatusRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    is_owner = db.query(FamilyMembership).filter(
        FamilyMembership.family_id == family_id,
        FamilyMembership.user_id == current_user.id,
        FamilyMembership.role == RoleEnum.owner,
    ).first()
    if not is_owner:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Owner only")

    if request.status not in ("active", "disabled"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Status must be 'active' or 'disabled'")

    membership = db.query(FamilyMembership).filter(
        FamilyMembership.family_id == family_id,
        FamilyMembership.user_id == user_id,
    ).first()
    if not membership:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")

    membership.status = StatusEnum(request.status)
    db.commit()
    db.refresh(membership)

    return {"user_id": str(user_id), "status": membership.status.value}
