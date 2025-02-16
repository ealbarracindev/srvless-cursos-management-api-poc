# tests/test_course_change_state.py
import json
import pytest
from unittest.mock import patch, MagicMock
from src.course_change_state import handler
from src.business_rules import validate_state_transition
from src.db import CourseDB

@pytest.fixture
def mock_dynamodb_table():
    """
    Fixture para configurar una tabla DynamoDB simulada utilizando MagicMock.
    """
    table = MagicMock()
    table.get_item.return_value = {
        'Item': {
            'cursoId': '1',
            'titulo': 'Curso de Python',
            'estado': 'Planeado'
        }
    }
    return table

@pytest.fixture
def db_instance(mock_dynamodb_table):
    """
    Fixture para configurar la instancia de CourseDB para usar la tabla simulada.
    """
    instance = MagicMock(spec=CourseDB)
    instance.table = mock_dynamodb_table
    instance.get_course.return_value = {
        'cursoId': '1',
        'titulo': 'Curso de Python',
        'estado': 'Planeado'
    }
    return instance

@pytest.fixture
def event():
    return {
        'pathParameters': {'cursoId': '1'},
        'body': json.dumps({"nuevo_estado": "En Curso"})
    }

@pytest.fixture
def context():
    return {}

@patch("src.course_change_state.CourseDB", autospec=True)
@patch("src.notifications.requests.post")
def test_change_state_success(mock_requests_post, mock_course_db_class, db_instance, event, context):
    mock_course_db_class.return_value = db_instance
    mock_requests_post.return_value = MagicMock(status_code=200)

    # Llamar al handler de la función Lambda
    response = handler(event, context)

    # Verificar que la respuesta sea exitosa
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['message'] == "Estado del curso actualizado exitosamente."

    # Verificar que se haya actualizado el estado del curso en DynamoDB
    db_instance.update_course_state.assert_called_once_with("1", "En Curso")


@patch("src.course_change_state.CourseDB", autospec=True)
@patch("src.notifications.requests.post")
def test_change_state_course_not_found(mock_requests_post, mock_course_db_class, db_instance, event, context):
    db_instance.get_course.return_value = None
    mock_course_db_class.return_value = db_instance
    mock_requests_post.return_value = MagicMock(status_code=200)

    # Llamar al handler de la función Lambda
    response = handler(event, context)

    # Verificar que la respuesta sea un error
    assert response['statusCode'] == 404
    body = json.loads(response['body'])
    assert 'error' in body
    assert body['error'] == "Curso no encontrado."

@patch("src.logs.logger.error")
@patch("src.db.CourseDB.get_course")
def test_unhandled_exception(mock_get_course, mock_logger_error, event, context):
    # Forzar que get_course arroje un error inesperado
    mock_get_course.side_effect = Exception("Error inesperado")

    response = handler(event, context)

    assert response['statusCode'] == 500
    body = json.loads(response['body'])
    assert 'error' in body
    assert body['error'] == "Error interno del servidor."

    # Validar que el logger registre el error
    mock_logger_error.assert_called_once_with("Error al cambiar el estado del curso: Error inesperado")

@patch("src.db.CourseDB.get_course")
@patch("src.business_rules.validate_state_transition")
def test_change_state_invalid_transition(mock_validate_state_transition, db_instance, event, context):
    db_instance.create_course({
        "cursoId": "1",
        "titulo": "Curso de Python",
        "descripcion": "Curso básico de Python",
        "instructor": "Ana Pérez",
        "capacidad": 30,
        "estado": "Completado"
    })

    mock_validate_state_transition.return_value = False

    response = handler(event, context)

    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert 'error' in body
    assert body['error'] == "Transición de estado no permitida."

    # Verificar que no se haya actualizado el estado del curso
    curso = db_instance.get_course("1")
    assert curso['estado'] == "Completado"

    # Validar que la función de transición fue llamada con los argumentos correctos
    mock_validate_state_transition.assert_called_once_with("Completado", "En Curso")

@patch("src.business_rules.validate_state_transition")
def test_change_state_invalid_current_state(mock_validate_state_transition, db_instance, event, context):
    db_instance.create_course({
        "cursoId": "1",
        "titulo": "Curso de Python",
        "descripcion": "Curso básico de Python",
        "instructor": "Ana Pérez",
        "capacidad": 30,
        "estado": None  # Estado inválido
    })

    response = handler(event, context)

    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert 'error' in body
    assert body['error'] == "Estado actual no válido."

@patch("src.db.CourseDB.get_course")
def test_change_state_missing_new_state(mock_course_db_class, event, context):
    mock_course_db_class.return_value = db_instance
    
    event['body'] = json.dumps({})

    response = handler(event, context)

    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert 'error' in body
    assert body['error'] == "'nuevo_estado'"

