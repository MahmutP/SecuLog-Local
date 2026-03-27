from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# --- Vulnerability Schemas ---
class VulnerabilityBase(BaseModel):
    title: str
    description: Optional[str] = None
    severity: str
    status: Optional[str] = "Open"
    poc: Optional[str] = None
    target_id: Optional[int] = None

class VulnerabilityCreate(VulnerabilityBase):
    pass

class Vulnerability(VulnerabilityBase):
    id: int
    project_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# --- Target Schemas ---
class TargetBase(BaseModel):
    name: str
    type: Optional[str] = None
    description: Optional[str] = None
    criticality: Optional[int] = 5

class TargetCreate(TargetBase):
    pass

class Target(TargetBase):
    id: int
    project_id: int
    created_at: datetime
    # vulnerabilities: List[Vulnerability] = []

    class Config:
        from_attributes = True

# --- Project Schemas ---
class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    id: int
    created_at: datetime
    # targets: List[Target] = []

    class Config:
        from_attributes = True
