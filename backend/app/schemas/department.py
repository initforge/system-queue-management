from pydantic import BaseModel
from typing import Optional, List, Any

class DepartmentBase(BaseModel):
    name: str
    description: Optional[str] = None

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentUpdate(DepartmentBase):
    name: Optional[str] = None

class Department(DepartmentBase):
    id: int
    code: str
    is_active: bool = True

    class Config:
        from_attributes = True

class DepartmentResponse(Department):
    pass

class DepartmentWithServices(Department):
    services: List[Any] = []