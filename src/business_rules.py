# src/utils/business_rules.py
from datetime import datetime, timedelta
from src.db import CourseDB

VALID_TRANSITIONS = {
    "Planeado": ["En Curso", "Cancelado"],
    "En Curso": ["Completado", "Cancelado"],
    "Completado": [],
    "Cancelado": []
}

MAX_STUDENTS = 50

def is_course_expired(fecha_creacion: str, days_until_expiry: int = 30) -> bool:
    """
    Verifica si un curso en estado "Planeado" ha caducado.

    :param fecha_creacion: Fecha de creación del curso en formato ISO.
    :param days_until_expiry: Días límite antes de la caducidad.
    :return: True si el curso ha caducado.
    """
    creation_date = datetime.fromisoformat(fecha_creacion)
    expiry_date = creation_date + timedelta(days=days_until_expiry)
    return datetime.utcnow() > expiry_date

def validate_state_transition(current_state, new_state):
    """Valida si la transición de estado es permitida."""
    return new_state in VALID_TRANSITIONS.get(current_state, [])

def validate_course_capacity(current_capacity):
    """Valida si el curso tiene espacio disponible."""
    return current_capacity < MAX_STUDENTS

def is_duplicate_course(titulo: str, instructor: str, db: CourseDB) -> bool:
    """
    Verifica si un curso con el mismo título e instructor ya existe.

    :param titulo: Título del curso.
    :param instructor: Nombre del instructor.
    :param db: Instancia de CourseDB.
    :return: True si el curso ya existe, False en caso contrario.
    """
    return db.get_course_by_title_and_instructor(titulo, instructor) is not None

def validate_prerequisites(prerequisites: list, completed_courses: list) -> bool:
    """
    Valida si los cursos previos han sido completados.
    
    :param prerequisites: Lista de IDs de cursos requeridos.
    :param completed_courses: Lista de IDs de cursos completados por el estudiante.
    :return: True si todos los requisitos están cumplidos.
    """
    return all(prereq in completed_courses for prereq in prerequisites)
