from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

from ...core.database import get_db
from ...models import Department, Service, QRCode, User
from ...core.security import get_current_user

# Simple auth dependency for now
def require_manager_or_admin(current_user: User = Depends(get_current_user)):
    if current_user.role not in ['manager', 'admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    return current_user

router = APIRouter()

# Pydantic models
class DepartmentResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    code: str
    qr_code_token: str
    max_concurrent_customers: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}

class DepartmentCreate(BaseModel):
    name: str
    description: Optional[str] = None
    code: str
    max_concurrent_customers: int = 50

class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    max_concurrent_customers: Optional[int] = None
    is_active: Optional[bool] = None

class DepartmentWithServices(DepartmentResponse):
    services: List[dict]

@router.get("/", response_model=List[DepartmentResponse])
def get_departments(
    db: Session = Depends(get_db),
    include_inactive: bool = False
):
    query = select(Department)
    if not include_inactive:
        query = query.where(Department.is_active == True)
    
    result = db.execute(query.order_by(Department.name))
    departments = result.scalars().all()
    
    return [DepartmentResponse.model_validate(dept) for dept in departments]

@router.get("/{department_id}", response_model=DepartmentWithServices)
def get_department(
    department_id: int,
    db: Session = Depends(get_db)
):
    result = db.execute(
        select(Department)
        .options(selectinload(Department.services))
        .where(Department.id == department_id)
    )
    department = result.scalar_one_or_none()
    
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )
    
    return DepartmentWithServices(
        id=department.id,
        name=department.name,
        description=department.description,
        code=department.code,
        qr_code_token=department.qr_code_token,
        max_concurrent_customers=department.max_concurrent_customers,
        is_active=department.is_active,
        created_at=department.created_at,
        updated_at=department.updated_at,
        services=[
            {
                "id": service.id,
                "name": service.name,
                "description": service.description,
                "code": service.code,
                "estimated_duration": service.estimated_duration,
                "priority_level": service.priority_level,
                "is_active": service.is_active
            }
            for service in department.services
        ]
    )

@router.get("/code/{department_code}", response_model=DepartmentWithServices)
def get_department_by_code(
    department_code: str,
    db: Session = Depends(get_db)
):
    result = db.execute(
        select(Department)
        .options(selectinload(Department.services))
        .where(Department.code == department_code.upper())
    )
    department = result.scalar_one_or_none()
    
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )
    
    return DepartmentWithServices(
        id=department.id,
        name=department.name,
        description=department.description,
        code=department.code,
        qr_code_token=department.qr_code_token,
        max_concurrent_customers=department.max_concurrent_customers,
        is_active=department.is_active,
        created_at=department.created_at,
        updated_at=department.updated_at,
        services=[
            {
                "id": service.id,
                "name": service.name,
                "description": service.description,
                "code": service.code,
                "estimated_duration": service.estimated_duration,
                "priority_level": service.priority_level,
                "is_active": service.is_active
            }
            for service in department.services
            if service.is_active
        ]
    )

@router.post("/", response_model=DepartmentResponse)
def create_department(
    department_data: DepartmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin)
):
    # Check if department code already exists
    existing_dept = db.execute(
        select(Department).where(Department.code == department_data.code.upper())
    )
    if existing_dept.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Department code already exists"
        )
    
    # Create new department
    import uuid
    new_department = Department(
        name=department_data.name,
        description=department_data.description,
        code=department_data.code.upper(),
        qr_code_token=str(uuid.uuid4()),
        max_concurrent_customers=department_data.max_concurrent_customers
    )
    
    db.add(new_department)
    db.commit()
    db.refresh(new_department)
    
    # Create QR code entry
    qr_code = QRCode(
        department_id=new_department.id,
        token=new_department.qr_code_token,
        registration_url=f"http://192.168.1.16:3000/register/{new_department.code}",
        is_active=True
    )
    
    db.add(qr_code)
    db.commit()
    
    return DepartmentResponse.model_validate(new_department)

@router.put("/{department_id}", response_model=DepartmentResponse)
def update_department(
    department_id: int,
    department_data: DepartmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin)
):
    # Get department
    result = db.execute(
        select(Department).where(Department.id == department_id)
    )
    department = result.scalar_one_or_none()
    
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )
    
    # Update fields
    if department_data.name is not None:
        department.name = department_data.name
    if department_data.description is not None:
        department.description = department_data.description
    if department_data.max_concurrent_customers is not None:
        department.max_concurrent_customers = department_data.max_concurrent_customers
    if department_data.is_active is not None:
        department.is_active = department_data.is_active
    
    db.commit()
    db.refresh(department)
    
    return DepartmentResponse.model_validate(department)

@router.delete("/{department_id}")
def delete_department(
    department_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin)
):
    # Get department
    result = db.execute(
        select(Department).where(Department.id == department_id)
    )
    department = result.scalar_one_or_none()
    
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )
    
    # Soft delete (deactivate)
    department.is_active = False
    db.commit()
    
    return {"message": "Department deactivated successfully"}

@router.get("/{department_id}")
async def get_department_info(
    department_id: int,
    db: Session = Depends(get_db)
):
    """Get basic department information"""
    result = db.execute(select(Department).where(Department.id == department_id)).scalar_one_or_none()
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )
    
    return {
        "id": result.id,
        "name": result.name,
        "code": result.code,
        "description": result.description
    }
