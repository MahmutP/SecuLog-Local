from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

import models, schemas
from database import engine, get_db

# Create DB tables inside Postgres automatically when starting
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="SecuLog-Local API")

# Configure CORS for local UI access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Projects Endpoints ---
@app.get("/api/projects", response_model=List[schemas.Project])
def read_projects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    projects = db.query(models.Project).offset(skip).limit(limit).all()
    return projects

@app.post("/api/projects", response_model=schemas.Project)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    db_project = models.Project(**project.model_dump())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@app.delete("/api/projects/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(db_project)
    db.commit()
    return {"ok": True}

# --- Targets Endpoints ---
@app.get("/api/targets", response_model=List[schemas.Target])
def read_targets(project_id: int = None, db: Session = Depends(get_db)):
    query = db.query(models.Target)
    if project_id:
        query = query.filter(models.Target.project_id == project_id)
    return query.all()

@app.post("/api/targets", response_model=schemas.Target)
def create_target(target: schemas.TargetCreate, project_id: int, db: Session = Depends(get_db)):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    db_target = models.Target(**target.model_dump(), project_id=project_id)
    db.add(db_target)
    db.commit()
    db.refresh(db_target)
    return db_target

# --- Vulnerabilities Endpoints ---
@app.get("/api/vulnerabilities", response_model=List[schemas.Vulnerability])
def read_vulnerabilities(project_id: int = None, target_id: int = None, db: Session = Depends(get_db)):
    query = db.query(models.Vulnerability)
    if project_id:
        query = query.filter(models.Vulnerability.project_id == project_id)
    if target_id:
        query = query.filter(models.Vulnerability.target_id == target_id)
    return query.all()

@app.post("/api/vulnerabilities", response_model=schemas.Vulnerability)
def create_vulnerability(vuln: schemas.VulnerabilityCreate, project_id: int, db: Session = Depends(get_db)):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if target exists and belongs to the project (if provided)
    if vuln.target_id:
        db_target = db.query(models.Target).filter(models.Target.id == vuln.target_id).first()
        if not db_target or db_target.project_id != project_id:
            raise HTTPException(status_code=400, detail="Target not found in this project")

    db_vuln = models.Vulnerability(**vuln.model_dump(), project_id=project_id)
    db.add(db_vuln)
    db.commit()
    db.refresh(db_vuln)
    return db_vuln

# --- Reporting Endpoints ---
@app.get("/api/reports/{project_id}")
def get_project_report(project_id: int, db: Session = Depends(get_db)):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    targets = db.query(models.Target).filter(models.Target.project_id == project_id).all()
    vulns = db.query(models.Vulnerability).filter(models.Vulnerability.project_id == project_id).all()
    
    stats = {
        "Critical": 0,
        "High": 0,
        "Medium": 0,
        "Low": 0,
        "Info": 0
    }
    
    open_vulns = [v for v in vulns if v.status == "Open"]
    for v in open_vulns:
        if v.severity in stats:
            stats[v.severity] += 1
            
    target_data = []
    for t in targets:
        t_vulns = [v for v in vulns if v.target_id == t.id]
        target_data.append({
            "id": t.id,
            "name": t.name,
            "type": t.type,
            "vulnerabilities": [{"id": v.id, "title": v.title, "severity": v.severity, "status": v.status} for v in t_vulns]
        })
        
    unassigned_vulns = [v for v in vulns if not v.target_id]
    if unassigned_vulns:
        target_data.append({
            "id": None,
            "name": "Genel Kapsam (Hedef Belirtilmemiş)",
            "type": "Genel",
            "vulnerabilities": [{"id": v.id, "title": v.title, "severity": v.severity, "status": v.status} for v in unassigned_vulns]
        })

    return {
        "project": {"id": db_project.id, "name": db_project.name, "description": db_project.description},
        "stats": stats,
        "total_targets": len(targets),
        "total_vulns": len(vulns),
        "open_vulns": len(open_vulns),
        "targets": target_data
    }
