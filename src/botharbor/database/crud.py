"""CRUD operations for database models."""

from typing import Optional

from botharbor.database.database import get_session
from botharbor.database.models import Project


def get_all_projects() -> list[Project]:
    """Get all projects from the database."""
    session = get_session()
    try:
        return session.query(Project).order_by(Project.name).all()
    finally:
        session.close()


def get_project_by_id(project_id: int) -> Optional[Project]:
    """Get a project by its ID."""
    session = get_session()
    try:
        return session.query(Project).filter(Project.id == project_id).first()
    finally:
        session.close()


def create_project(
    name: str,
    folder_path: str,
    entrypoint: str,
    interpreter_path: str
) -> Project:
    """Create a new project."""
    session = get_session()
    try:
        project = Project(
            name=name,
            folder_path=folder_path,
            entrypoint=entrypoint,
            interpreter_path=interpreter_path
        )
        session.add(project)
        session.commit()
        session.refresh(project)
        return project
    finally:
        session.close()


def update_project(
    project_id: int,
    name: Optional[str] = None,
    folder_path: Optional[str] = None,
    entrypoint: Optional[str] = None,
    interpreter_path: Optional[str] = None
) -> Optional[Project]:
    """Update an existing project."""
    session = get_session()
    try:
        project = session.query(Project).filter(Project.id == project_id).first()
        if not project:
            return None
        
        if name is not None:
            project.name = name
        if folder_path is not None:
            project.folder_path = folder_path
        if entrypoint is not None:
            project.entrypoint = entrypoint
        if interpreter_path is not None:
            project.interpreter_path = interpreter_path
        
        session.commit()
        session.refresh(project)
        return project
    finally:
        session.close()


def delete_project(project_id: int) -> bool:
    """Delete a project by its ID."""
    session = get_session()
    try:
        project = session.query(Project).filter(Project.id == project_id).first()
        if not project:
            return False
        
        session.delete(project)
        session.commit()
        return True
    finally:
        session.close()
