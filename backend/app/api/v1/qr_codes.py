from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
import qrcode
from io import BytesIO
import base64

from ...core.database import get_db
from ...models import QRCode, Department, User
from ...core.security import get_current_user

router = APIRouter()

# Pydantic models
class QRCodeResponse(BaseModel):
    id: int
    department_id: int
    department_name: str
    token: str
    registration_url: str
    qr_code_image: str  # Base64 encoded image
    is_active: bool
    expires_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}

class QRCodeCreate(BaseModel):
    department_id: int
    expires_at: Optional[datetime] = None

def generate_qr_code(url: str) -> str:
    """Generate QR code image and return as base64 string"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return f"data:image/png;base64,{img_str}"

@router.get("/", response_model=List[QRCodeResponse])
async def get_qr_codes(
    department_id: Optional[int] = None,
    include_inactive: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(QRCode, Department).join(Department)
    
    if department_id:
        query = query.where(QRCode.department_id == department_id)
    
    if not include_inactive:
        query = query.where(QRCode.is_active == True)
    
    result = await db.execute(query.order_by(Department.name))
    qr_codes = result.all()
    
    return [
        QRCodeResponse(
            id=qr_code.id,
            department_id=qr_code.department_id,
            department_name=department.name,
            token=qr_code.token,
            registration_url=qr_code.registration_url,
            qr_code_image=generate_qr_code(qr_code.registration_url),
            is_active=qr_code.is_active,
            expires_at=qr_code.expires_at,
            created_at=qr_code.created_at,
            updated_at=qr_code.updated_at
        )
        for qr_code, department in qr_codes
    ]

@router.get("/{qr_code_id}", response_model=QRCodeResponse)
async def get_qr_code(
    qr_code_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(QRCode, Department)
        .join(Department)
        .where(QRCode.id == qr_code_id)
    )
    qr_code_data = result.first()
    
    if not qr_code_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="QR code not found"
        )
    
    qr_code, department = qr_code_data
    
    return QRCodeResponse(
        id=qr_code.id,
        department_id=qr_code.department_id,
        department_name=department.name,
        token=qr_code.token,
        registration_url=qr_code.registration_url,
        qr_code_image=generate_qr_code(qr_code.registration_url),
        is_active=qr_code.is_active,
        expires_at=qr_code.expires_at,
        created_at=qr_code.created_at,
        updated_at=qr_code.updated_at
    )

@router.get("/department/{department_id}", response_model=List[QRCodeResponse])
async def get_qr_codes_by_department(
    department_id: int,
    include_inactive: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(QRCode, Department).join(Department).where(QRCode.department_id == department_id)
    
    if not include_inactive:
        query = query.where(QRCode.is_active == True)
    
    result = await db.execute(query)
    qr_codes = result.all()
    
    return [
        QRCodeResponse(
            id=qr_code.id,
            department_id=qr_code.department_id,
            department_name=department.name,
            token=qr_code.token,
            registration_url=qr_code.registration_url,
            qr_code_image=generate_qr_code(qr_code.registration_url),
            is_active=qr_code.is_active,
            expires_at=qr_code.expires_at,
            created_at=qr_code.created_at,
            updated_at=qr_code.updated_at
        )
        for qr_code, department in qr_codes
    ]

@router.post("/", response_model=QRCodeResponse)
async def create_qr_code(
    qr_code_data: QRCodeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin)
):
    # Check if department exists
    department_result = await db.execute(
        select(Department).where(Department.id == qr_code_data.department_id)
    )
    department = department_result.scalar_one_or_none()
    
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )
    
    # Generate new token
    import uuid
    token = str(uuid.uuid4())
    
    # Create QR code
    new_qr_code = QRCode(
        department_id=qr_code_data.department_id,
        token=token,
        registration_url=f"http://192.168.1.16:3000/register/{department.code}",
        is_active=True,
        expires_at=qr_code_data.expires_at
    )
    
    db.add(new_qr_code)
    await db.commit()
    await db.refresh(new_qr_code)
    
    return QRCodeResponse(
        id=new_qr_code.id,
        department_id=new_qr_code.department_id,
        department_name=department.name,
        token=new_qr_code.token,
        registration_url=new_qr_code.registration_url,
        qr_code_image=generate_qr_code(new_qr_code.registration_url),
        is_active=new_qr_code.is_active,
        expires_at=new_qr_code.expires_at,
        created_at=new_qr_code.created_at,
        updated_at=new_qr_code.updated_at
    )

@router.put("/{qr_code_id}/regenerate", response_model=QRCodeResponse)
async def regenerate_qr_code(
    qr_code_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin)
):
    # Get QR code
    result = await db.execute(
        select(QRCode, Department)
        .join(Department)
        .where(QRCode.id == qr_code_id)
    )
    qr_code_data = result.first()
    
    if not qr_code_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="QR code not found"
        )
    
    qr_code, department = qr_code_data
    
    # Generate new token
    import uuid
    qr_code.token = str(uuid.uuid4())
    qr_code.registration_url = f"http://192.168.1.16:3000/register/{department.code}"
    
    await db.commit()
    await db.refresh(qr_code)
    
    return QRCodeResponse(
        id=qr_code.id,
        department_id=qr_code.department_id,
        department_name=department.name,
        token=qr_code.token,
        registration_url=qr_code.registration_url,
        qr_code_image=generate_qr_code(qr_code.registration_url),
        is_active=qr_code.is_active,
        expires_at=qr_code.expires_at,
        created_at=qr_code.created_at,
        updated_at=qr_code.updated_at
    )

@router.put("/{qr_code_id}/toggle")
async def toggle_qr_code(
    qr_code_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin)
):
    # Get QR code
    result = await db.execute(
        select(QRCode).where(QRCode.id == qr_code_id)
    )
    qr_code = result.scalar_one_or_none()
    
    if not qr_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="QR code not found"
        )
    
    # Toggle active status
    qr_code.is_active = not qr_code.is_active
    await db.commit()
    
    return {
        "message": f"QR code {'activated' if qr_code.is_active else 'deactivated'} successfully",
        "is_active": qr_code.is_active
    }

@router.delete("/{qr_code_id}")
async def delete_qr_code(
    qr_code_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin)
):
    # Get QR code
    result = await db.execute(
        select(QRCode).where(QRCode.id == qr_code_id)
    )
    qr_code = result.scalar_one_or_none()
    
    if not qr_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="QR code not found"
        )
    
    # Delete QR code
    await db.delete(qr_code)
    await db.commit()
    
    return {"message": "QR code deleted successfully"}
