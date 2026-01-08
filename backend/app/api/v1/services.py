from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional, Dict, Any
import enum

from ...core.database import get_db
from ...models import Service, Department, User
from ...core.security import get_current_user, require_manager_or_admin
from ...schemas.service import (
    ServiceCreate,
    ServiceResponse,
    ServiceUpdate,
    ServiceWithFormFields,
    FieldType  # Import FieldType
)

class TicketPriority(str, enum.Enum):
    NORMAL = "normal"
    HIGH = "high"
    ELDERLY = "elderly"
    DISABLED = "disabled"
    VIP = "vip"

router = APIRouter()
class ServiceFormFieldResponse(BaseModel):
    id: int
    field_name: str
    field_type: FieldType
    field_label: str
    placeholder: Optional[str]
    is_required: bool
    field_options: Optional[Dict[str, Any]]
    validation_rules: Optional[Dict[str, Any]]
    display_order: int
    
    model_config = {"from_attributes": True}

class ServiceResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    department_id: int
    department_name: str
    estimated_duration: int
    code: str
    priority_level: TicketPriority
    is_active: bool
    created_at: datetime
    updated_at: datetime
    form_fields: List[ServiceFormFieldResponse]
    
    model_config = {"from_attributes": True}

class ServiceCreate(BaseModel):
    name: str
    description: Optional[str] = None
    department_id: int
    estimated_duration: int = 15
    code: str
    priority_level: TicketPriority = TicketPriority.normal

class ServiceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    estimated_duration: Optional[int] = None
    priority_level: Optional[TicketPriority] = None
    is_active: Optional[bool] = None

class ServiceFormFieldCreate(BaseModel):
    field_name: str
    field_type: FieldType
    field_label: str
    placeholder: Optional[str] = None
    is_required: bool = False
    field_options: Optional[Dict[str, Any]] = None
    validation_rules: Optional[Dict[str, Any]] = None
    display_order: int = 0

@router.get("/", response_model=List[ServiceResponse])
def get_services(
    department_id: Optional[int] = None,
    include_inactive: bool = False,
    db: Session = Depends(get_db)
):
    """Get all services, optionally filtered by department"""
    query = (
        select(Service)
        .join(Service.department)
        .options(selectinload(Service.department))
    )
    
    if department_id:
        query = query.where(Service.department_id == department_id)
    
    if not include_inactive:
        query = query.where(Service.is_active == True)
    
    result = db.execute(query.order_by(Service.name))
    services = result.scalars().all()
    
    return [
        ServiceResponse(
            id=service.id,
            name=service.name,
            description=service.description,
            department_id=service.department_id,
            department_name=service.department.name,
            estimated_duration=service.estimated_duration,
            code=service.code,
            priority_level=service.priority_level,
            is_active=service.is_active,
            created_at=service.created_at,
            updated_at=service.updated_at,
            form_fields=[
                ServiceFormFieldResponse.model_validate(field)
                for field in sorted(service.form_fields, key=lambda x: x.display_order)
            ]
        )
        for service in services
    ]

@router.get("/{service_id}", response_model=ServiceResponse)
async def get_service(
    service_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Service)
        .options(
            selectinload(Service.department),
            selectinload(Service.form_fields)
        )
        .where(Service.id == service_id)
    )
    service = result.scalar_one_or_none()
    
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    
    return ServiceResponse(
        id=service.id,
        name=service.name,
        description=service.description,
        department_id=service.department_id,
        department_name=service.department.name,
        estimated_duration=service.estimated_duration,
        code=service.code,
        priority_level=service.priority_level,
        is_active=service.is_active,
        created_at=service.created_at,
        updated_at=service.updated_at,
        form_fields=[
            ServiceFormFieldResponse.model_validate(field)
            for field in sorted(service.form_fields, key=lambda x: x.display_order)
        ]
    )

@router.get("/department/{department_id}", response_model=List[ServiceResponse])
async def get_services_by_department(
    department_id: int,
    include_inactive: bool = False,
    db: AsyncSession = Depends(get_db)
):
    query = select(Service).options(
        selectinload(Service.department),
        selectinload(Service.form_fields)
    ).where(Service.department_id == department_id)
    
    if not include_inactive:
        query = query.where(Service.is_active == True)
    
    result = await db.execute(query.order_by(Service.name))
    services = result.scalars().all()
    
    return [
        ServiceResponse(
            id=service.id,
            name=service.name,
            description=service.description,
            department_id=service.department_id,
            department_name=service.department.name,
            estimated_duration=service.estimated_duration,
            code=service.code,
            priority_level=service.priority_level,
            is_active=service.is_active,
            created_at=service.created_at,
            updated_at=service.updated_at,
            form_fields=[
                ServiceFormFieldResponse.model_validate(field)
                for field in sorted(service.form_fields, key=lambda x: x.display_order)
            ]
        )
        for service in services
    ]

@router.post("/", response_model=ServiceResponse)
async def create_service(
    service_data: ServiceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if service code already exists
    existing_service = await db.execute(
        select(Service).where(Service.code == service_data.code.upper())
    )
    if existing_service.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Service code already exists"
        )
    
    # Check if department exists
    department_result = await db.execute(
        select(Department).where(Department.id == service_data.department_id)
    )
    department = department_result.scalar_one_or_none()
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )
    
    # Create new service
    new_service = Service(
        name=service_data.name,
        description=service_data.description,
        department_id=service_data.department_id,
        estimated_duration=service_data.estimated_duration,
        code=service_data.code.upper(),
        priority_level=service_data.priority_level
    )
    
    db.add(new_service)
    await db.commit()
    await db.refresh(new_service)
    
    # Load department for response
    await db.refresh(new_service, ["department"])
    
    return ServiceResponse(
        id=new_service.id,
        name=new_service.name,
        description=new_service.description,
        department_id=new_service.department_id,
        department_name=department.name,
        estimated_duration=new_service.estimated_duration,
        code=new_service.code,
        priority_level=new_service.priority_level,
        is_active=new_service.is_active,
        created_at=new_service.created_at,
        updated_at=new_service.updated_at,
        form_fields=[]
    )

@router.put("/{service_id}", response_model=ServiceResponse)
async def update_service(
    service_id: int,
    service_data: ServiceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Get service
    result = await db.execute(
        select(Service)
        .options(
            selectinload(Service.department),
            selectinload(Service.form_fields)
        )
        .where(Service.id == service_id)
    )
    service = result.scalar_one_or_none()
    
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    
    # Update fields
    if service_data.name is not None:
        service.name = service_data.name
    if service_data.description is not None:
        service.description = service_data.description
    if service_data.estimated_duration is not None:
        service.estimated_duration = service_data.estimated_duration
    if service_data.priority_level is not None:
        service.priority_level = service_data.priority_level
    if service_data.is_active is not None:
        service.is_active = service_data.is_active
    
    await db.commit()
    await db.refresh(service)
    
    return ServiceResponse(
        id=service.id,
        name=service.name,
        description=service.description,
        department_id=service.department_id,
        department_name=service.department.name,
        estimated_duration=service.estimated_duration,
        code=service.code,
        priority_level=service.priority_level,
        is_active=service.is_active,
        created_at=service.created_at,
        updated_at=service.updated_at,
        form_fields=[
            ServiceFormFieldResponse.model_validate(field)
            for field in sorted(service.form_fields, key=lambda x: x.display_order)
        ]
    )

@router.post("/{service_id}/form-fields", response_model=ServiceFormFieldResponse)
async def add_form_field(
    service_id: int,
    field_data: ServiceFormFieldCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if service exists
    service_result = await db.execute(
        select(Service).where(Service.id == service_id)
    )
    service = service_result.scalar_one_or_none()
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    
    # Create new form field
    new_field = ServiceFormField(
        service_id=service_id,
        field_name=field_data.field_name,
        field_type=field_data.field_type,
        field_label=field_data.field_label,
        placeholder=field_data.placeholder,
        is_required=field_data.is_required,
        field_options=field_data.field_options,
        validation_rules=field_data.validation_rules,
        display_order=field_data.display_order
    )
    
    db.add(new_field)
    await db.commit()
    await db.refresh(new_field)
    
    return ServiceFormFieldResponse.model_validate(new_field)

@router.delete("/{service_id}")
async def delete_service(
    service_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Get service
    result = await db.execute(
        select(Service).where(Service.id == service_id)
    )
    service = result.scalar_one_or_none()
    
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    
    # Soft delete (deactivate)
    service.is_active = False
    await db.commit()
    
    return {"message": "Service deactivated successfully"}
