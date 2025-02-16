import pytest
from datetime import datetime, timedelta
from src.business_rules import is_course_expired, validate_state_transition

def test_is_course_expired():
    # Caso: Curso caducado
    fecha_creacion = (datetime.utcnow() - timedelta(days=31)).isoformat()
    assert is_course_expired(fecha_creacion) == True

    # Caso: Curso no caducado
    fecha_creacion = (datetime.utcnow() - timedelta(days=29)).isoformat()
    assert is_course_expired(fecha_creacion) == False

    # Caso: Curso caducado con un límite de 60 días
    fecha_creacion = (datetime.utcnow() - timedelta(days=61)).isoformat()
    assert is_course_expired(fecha_creacion, days_until_expiry=60) == True

    # Caso: Curso no caducado con un límite de 60 días
    fecha_creacion = (datetime.utcnow() - timedelta(days=59)).isoformat()
    assert is_course_expired(fecha_creacion, days_until_expiry=60) == False

def test_validate_state_transition():
    # Caso: Transición válida de "Planeado" a "En Curso"
    assert validate_state_transition("Planeado", "En Curso") == True

    # Caso: Transición inválida de "Planeado" a "Completado"
    assert validate_state_transition("Planeado", "Completado") == False

    # Caso: Transición válida de "En Curso" a "Completado"
    assert validate_state_transition("En Curso", "Completado") == True

    # Caso: Transición inválida de "Completado" a "Planeado"
    assert validate_state_transition("Completado", "Planeado") == False

    # Caso: Transición válida de "En Curso" a "Cancelado"
    assert validate_state_transition("En Curso", "Cancelado") == True

    # Caso: Transición inválida de "Cancelado" a "En Curso"
    assert validate_state_transition("Cancelado", "En Curso") == False