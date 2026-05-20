from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
import uuid as uuid_mod

from app.database import get_db
from app.models.user import User
from app.models.category import Category, CategoryTypeEnum
from app.models.family import Family, FamilyMembership, RoleEnum
from app.schemas.category import CategorySchema, CategoryListResponse, CategoryCreateRequest
from app.dependencies import get_current_user

router = APIRouter(prefix="/families", tags=["categories"])


@router.get("/{family_id}/categories", response_model=CategoryListResponse)
async def list_categories(
    family_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    family = db.query(Family).filter(Family.id == family_id).first()
    if family and not family.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Family is disabled")
    membership = db.query(FamilyMembership).filter(
        FamilyMembership.family_id == family_id,
        FamilyMembership.user_id == current_user.id,
    ).first()
    if not membership and not current_user.is_superadmin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a member")

    categories = db.query(Category).filter(Category.family_id == family_id).all()
    return CategoryListResponse(
        categories=[
            CategorySchema(
                id=c.id,
                name=c.name,
                type=c.type.value,
                is_default=c.is_default,
            )
            for c in categories
        ]
    )


@router.post("/{family_id}/categories", status_code=status.HTTP_201_CREATED)
async def create_category(
    family_id: UUID,
    request: CategoryCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    family = db.query(Family).filter(Family.id == family_id).first()
    if family and not family.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Family is disabled")
    membership = db.query(FamilyMembership).filter(
        FamilyMembership.family_id == family_id,
        FamilyMembership.user_id == current_user.id,
        FamilyMembership.role == RoleEnum.owner,
    ).first()
    if not membership and not current_user.is_superadmin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Owner only")

    try:
        cat_type = CategoryTypeEnum(request.type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid category type: {request.type}",
        )

    category = Category(
        id=uuid_mod.uuid4(),
        family_id=family_id,
        name=request.name,
        type=cat_type,
        is_default=False,
    )
    db.add(category)
    db.commit()
    db.refresh(category)

    return CategorySchema(
        id=category.id,
        name=category.name,
        type=category.type.value,
        is_default=category.is_default,
    )
