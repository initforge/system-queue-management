"""
Department and Service management services
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from ..models.department import Department
from ..models.service import Service
from ..schemas.department import DepartmentCreate, DepartmentUpdate

def get_departments(db: Session, skip: int = 0, limit: int = 100, include_inactive: bool = False) -> List[Department]:
    query = db.query(Department)
    if not include_inactive:
        query = query.filter(Department.is_active == True)
    return query.offset(skip).limit(limit).all()

def get_department(db: Session, department_id: int) -> Optional[Department]:
    return db.query(Department).filter(Department.id == department_id).first()

def get_department_by_code(db: Session, code: str) -> Optional[Department]:
    return db.query(Department).filter(Department.code == code.upper()).first()

def create_department(db: Session, department_data: DepartmentCreate) -> Department:
    db_department = Department(
        name=department_data.name,
        description=department_data.description,
        code=department_data.code.upper(),
        max_concurrent_customers=department_data.max_concurrent_customers
    )
    db.add(db_department)
    db.commit()
    db.refresh(db_department)
    return db_department

def update_department(db: Session, department_id: int, department_data: DepartmentUpdate) -> Optional[Department]:
    department = db.query(Department).filter(Department.id == department_id).first()
    if not department:
        return None
        
    for field, value in department_data.dict(exclude_unset=True).items():
        setattr(department, field, value)
            
    db.commit()
    db.refresh(department)
    return department

def get_department_services(db: Session, department_id: int) -> List[Service]:
    return db.query(Service).filter(
        Service.department_id == department_id,
        Service.is_active == True
    ).all()

def create_service(db: Session, department_id: int, name: str, description: str, code: str, estimated_time: int) -> Service:
    db_service = Service(
        name=name,
        description=description,
        code=code.upper(),
        department_id=department_id,
        estimated_time=estimated_time
    )
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    return db_service