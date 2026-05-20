from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func as sa_func
from uuid import UUID
import uuid as uuid_mod
from typing import Optional
from app.database import get_db
from app.models.user import User
from app.models.family import Family, FamilyMembership, RoleEnum, StatusEnum
from app.models.account import Account
from app.models.category import Category
from app.models.transaction import Transaction, TransactionEdit
from app.utils.security import hash_password
from app.dependencies import get_current_user

router = APIRouter(prefix="/admin", tags=["admin"])


class InviteOwnerRequest(BaseModel):
    email: str
    first_name: str
    last_name: str
    password: str


class FamilyStatusRequest(BaseModel):
    is_active: bool


class ChangeOwnerRequest(BaseModel):
    new_owner_user_id: str


class AdminAddMemberRequest(BaseModel):
    email: str
    first_name: str
    last_name: str
    password: str
    role: str = "member"


def _require_superadmin(user: User):
    if not user.is_superadmin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Superadmin only")


@router.get("/families")
async def list_all_families(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    _require_superadmin(current_user)

    member_counts = (
        db.query(FamilyMembership.family_id, sa_func.count(FamilyMembership.id).label("cnt"))
        .group_by(FamilyMembership.family_id)
        .all()
    )
    count_map = {str(row.family_id): row.cnt for row in member_counts}

    families = db.query(Family).all()
    return {
        "families": [
            {
                "id": str(f.id),
                "name": f.name,
                "owner_id": str(f.owner_id),
                "is_active": f.is_active,
                "member_count": count_map.get(str(f.id), 0),
                "created_at": f.created_at,
            }
            for f in families
        ]
    }


@router.get("/families/{family_id}")
async def get_family_detail(
    family_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_superadmin(current_user)

    family = db.query(Family).filter(Family.id == family_id).first()
    if not family:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Family not found")

    owner = db.query(User).filter(User.id == family.owner_id).first()

    memberships = db.query(FamilyMembership).filter(
        FamilyMembership.family_id == family_id,
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
                "status": m.status.value,
                "joined_at": m.joined_at,
            })

    return {
        "id": str(family.id),
        "name": family.name,
        "owner_id": str(family.owner_id),
        "owner_email": owner.email if owner else None,
        "owner_name": f"{owner.first_name} {owner.last_name}" if owner else None,
        "is_active": family.is_active,
        "created_at": family.created_at,
        "member_count": len(memberships),
        "members": members,
    }


@router.patch("/families/{family_id}/status")
async def update_family_status(
    family_id: UUID,
    request: FamilyStatusRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_superadmin(current_user)

    family = db.query(Family).filter(Family.id == family_id).first()
    if not family:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Family not found")

    family.is_active = request.is_active
    db.commit()
    db.refresh(family)

    return {"id": str(family.id), "is_active": family.is_active}


@router.put("/families/{family_id}/owner")
async def change_family_owner(
    family_id: UUID,
    request: ChangeOwnerRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_superadmin(current_user)

    family = db.query(Family).filter(Family.id == family_id).first()
    if not family:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Family not found")

    try:
        new_owner_uuid = uuid_mod.UUID(request.new_owner_user_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID format")

    if new_owner_uuid == family.owner_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is already the owner")

    new_owner_membership = db.query(FamilyMembership).filter(
        FamilyMembership.family_id == family_id,
        FamilyMembership.user_id == new_owner_uuid,
        FamilyMembership.status == StatusEnum.active,
    ).first()
    if not new_owner_membership:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New owner must be an active member of the family")

    old_owner_id = family.owner_id

    old_owner_membership = db.query(FamilyMembership).filter(
        FamilyMembership.family_id == family_id,
        FamilyMembership.user_id == old_owner_id,
    ).first()
    if old_owner_membership:
        old_owner_membership.role = RoleEnum.member

    new_owner_membership.role = RoleEnum.owner
    family.owner_id = new_owner_uuid
    db.commit()

    return {
        "family_id": str(family_id),
        "old_owner_id": str(old_owner_id),
        "new_owner_id": str(new_owner_uuid),
    }


@router.delete("/families/{family_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_family_member(
    family_id: UUID,
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_superadmin(current_user)

    family = db.query(Family).filter(Family.id == family_id).first()
    if not family:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Family not found")

    membership = db.query(FamilyMembership).filter(
        FamilyMembership.family_id == family_id,
        FamilyMembership.user_id == user_id,
    ).first()
    if not membership:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")

    if user_id == family.owner_id:
        other_active = db.query(FamilyMembership).filter(
            FamilyMembership.family_id == family_id,
            FamilyMembership.user_id != user_id,
            FamilyMembership.status == StatusEnum.active,
        ).first()
        if not other_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot remove owner without assigning a replacement first",
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must change owner before removing current owner",
        )

    db.delete(membership)
    db.commit()
    return None


@router.post("/families/{family_id}/members", status_code=status.HTTP_201_CREATED)
async def admin_add_member(
    family_id: UUID,
    request: AdminAddMemberRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_superadmin(current_user)

    family = db.query(Family).filter(Family.id == family_id).first()
    if not family:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Family not found")

    if request.role not in ("owner", "member"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role must be 'owner' or 'member'")

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

    role = RoleEnum(request.role)

    if existing:
        existing.role = role
        existing.status = StatusEnum.active
    else:
        db.add(FamilyMembership(
            id=uuid_mod.uuid4(),
            family_id=family_id,
            user_id=user.id,
            role=role,
            status=StatusEnum.active,
        ))

    if role == RoleEnum.owner:
        family.owner_id = user.id
        old_owner_membership = db.query(FamilyMembership).filter(
            FamilyMembership.family_id == family_id,
            FamilyMembership.user_id != user.id,
            FamilyMembership.role == RoleEnum.owner,
        ).first()
        if old_owner_membership:
            old_owner_membership.role = RoleEnum.member

    db.commit()

    return {
        "user_id": str(user.id),
        "email": user.email,
        "role": request.role,
        "family_id": str(family_id),
    }


@router.delete("/families/{family_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_family(
    family_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_superadmin(current_user)

    family = db.query(Family).filter(Family.id == family_id).first()
    if not family:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Family not found")

    accounts = db.query(Account).filter(Account.family_id == family_id).all()
    account_ids = [a.id for a in accounts]

    if account_ids:
        db.query(TransactionEdit).filter(
            TransactionEdit.transaction_id.in_(
                db.query(Transaction.id).filter(Transaction.account_id.in_(account_ids))
            )
        ).delete(synchronize_session=False)
        db.query(Transaction).filter(Transaction.account_id.in_(account_ids)).delete(synchronize_session=False)

    db.query(Account).filter(Account.family_id == family_id).delete(synchronize_session=False)
    db.query(Category).filter(Category.family_id == family_id).delete(synchronize_session=False)
    db.query(FamilyMembership).filter(FamilyMembership.family_id == family_id).delete(synchronize_session=False)
    db.delete(family)
    db.commit()
    return None


@router.post("/families/{family_id}/invite-owner", status_code=status.HTTP_201_CREATED)
async def invite_owner(
    family_id: UUID,
    request: InviteOwnerRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_superadmin(current_user)

    family = db.query(Family).filter(Family.id == family_id).first()
    if not family:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Family not found")

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
        existing.role = RoleEnum.owner
    else:
        db.add(FamilyMembership(
            id=uuid_mod.uuid4(),
            family_id=family_id,
            user_id=user.id,
            role=RoleEnum.owner,
        ))

    family.owner_id = user.id
    db.commit()

    return {
        "user_id": str(user.id),
        "email": user.email,
        "family_id": str(family_id),
        "role": "owner",
    }
