import json
import os
from unittest.mock import patch, MagicMock
from src.course_get import handler

@patch("src.course_get.CourseDB")
def test_get_course_success( mock_course_db ):
    mock_course_db_instance = mock_course_db.return_value
    mock_course_db_instance.get_course.return_value = {
        "cursoId": "1", "titulo": "Curso de Python", "instructor": "Ana Pérez", "capacidad": 30
    }        
    
    event = {'pathParameters': {'cursoId': '1'}}
    response = handler(event, None)

    assert response['statusCode'] == 200

    body = json.loads(response['body'])
    assert 'titulo' in body
    assert body['titulo'] == 'Curso de Python'

    mock_logger.info.assert_called_with("Received event: %s", json.dumps(event))

@patch("src.course_get.CourseDB")
@patch("src.course_get.logger") 
def test_get_course_not_found(mock_logger, mock_course_db):
    mock_course_db_instance = mock_course_db.return_value
    mock_course_db_instance.get_course.return_value = None
    
    event = {'pathParameters': {'cursoId': '1'}}
    response = handler(event, None)

    assert response['statusCode'] == 404

    body = json.loads(response['body'])
    assert 'error' in body
    assert body['error'] == 'Curso no encontrado.'

    mock_logger.info.assert_called_with("Received event: %s", json.dumps(event))

@patch.dict(os.environ, {
    "DYNAMODB_TABLE": "CursosTable",
    "SLACK_WEBHOOK_URL": "https://mock-slack-webhook-url.com",
    "TEAMS_WEBHOOK_URL": "https://mock-teams-webhook-url.com"
})
@patch("src.notifications.requests.post")
@patch("src.course_get.CourseDB")
@patch("src.course_get.logger") 
def test_get_course_exception(mock_logger, mock_course_db, mock_requests_post):
    mock_course_db_instance = mock_course_db.return_value
    mock_course_db_instance.get_course.side_effect = Exception("Simulated exception")
    
    event = {'pathParameters': {'cursoId': '1'}}
    response = handler(event, None)

    assert response['statusCode'] == 500

    body = json.loads(response['body'])
    assert 'error' in body
    assert 'Simulated exception' in body['error']

    mock_logger.error.assert_called_once()
    # Verificar que se hayan enviado notificaciones de error
    assert mock_requests_post.call_count == 2