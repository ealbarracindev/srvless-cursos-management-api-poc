import json
import os
from unittest.mock import patch, MagicMock
from src.course_get_list import handler

@patch.dict(os.environ, {"DYNAMODB_TABLE": "CursosTable"})
@patch("src.course_get_list.logger")  # Mockear el logger
@patch("src.course_get_list.CourseDB")
def test_get_courses_success(mock_course_db, mock_logger):
    mock_course_db_instance = mock_course_db.return_value
    # Definir datos simulados
    mock_course_db_instance.get_all_courses.return_value = [
        {"cursoId": "1", "titulo": "Curso de Python", "instructor": "Ana Pérez", "capacidad": 30},
        {"cursoId": "2", "titulo": "Curso de AWS", "instructor": "Luis Martínez", "capacidad": 25}
    ]

    event = {}
    response = handler(event, None)

    assert response['statusCode'] == 200

    body = json.loads(response['body'])
    assert len(body) == 2
    assert body[0]['titulo'] == 'Curso de Python'
    assert body[1]['titulo'] == 'Curso de AWS'

    mock_logger.info.assert_called_with("Received event: %s", json.dumps(event))

@patch.dict(os.environ, {
    "DYNAMODB_TABLE": "CursosTable",
    "SLACK_WEBHOOK_URL": "https://mock-slack-webhook-url.com",
    "TEAMS_WEBHOOK_URL": "https://mock-teams-webhook-url.com"
})
@patch("src.notifications.requests.post")  # Mock para requests.post
@patch("src.course_get_list.Notification")  # Mock para send_notification
@patch("src.course_get_list.CourseDB")  # Mock para CourseDB
def test_get_courses_error(mock_course_db, mock_notification, mock_requests_post, set_env_vars):
    # Configuración de los mocks
    mock_notification_instance = mock_notification.return_value
    mock_course_db_instance = mock_course_db.return_value
    mock_course_db_instance.get_all_courses.side_effect = Exception("DB error")

    mock_requests_post.return_value = MagicMock(status_code=200)

    event = {}
    context = {}
    response = handler(event, context)

    assert response['statusCode'] == 500
    assert json.loads(response['body']) == {"error": "DB error"}

    error_message = "❌ Error al obtener los cursos: DB error"
    mock_notification_instance.send_notification.assert_any_call('slack', error_message)
    mock_notification_instance.send_notification.assert_any_call('teams', error_message)

    