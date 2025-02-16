import json
import os
from unittest.mock import patch, MagicMock
from src.course_delete import handler


# Mock para el evento de AWS Lambda
def create_event(curso_id):
    return {
        "pathParameters": {
            "cursoId": curso_id
        }
    }

# @patch.dict(os.environ, {
#     "DYNAMODB_TABLE": "CursosTable",
#     "SLACK_WEBHOOK_URL": "https://mock-slack-webhook-url.com",
#     "TEAMS_WEBHOOK_URL": "https://mock-teams-webhook-url.com"
# })
@patch("src.notifications.requests.post")
@patch("src.course_delete.CourseDB")
@patch("src.course_delete.Notification")
@patch("src.course_delete.logger") 
def test_delete_course_success(mock_logger, mock_notification, mock_course_db, mock_requests_post, set_env_vars):
    # Mock de métodos
    mock_db_instance = mock_course_db.return_value
    mock_db_instance.delete_course.return_value = None

    mock_notif_instance = mock_notification.return_value
    mock_notif_instance.send_notification.return_value = None

    # Crear un evento simulado
    event = create_event("curso123")

    # Ejecutar la función
    response = handler(event, None)

    # Verificar respuesta esperada
    assert response["statusCode"] == 200
    assert json.loads(response["body"]) == {"message": "Curso eliminado exitosamente."}

    # Verificar que los métodos fueron llamados
    mock_course_db.assert_called_once()
    mock_db_instance.delete_course.assert_called_once_with("curso123")
    mock_notification.assert_called()
    mock_notif_instance.send_notification.assert_any_call('slack', "🗑️ El curso 'curso123' ha sido eliminado.")
    mock_logger.info.assert_called()

    # mock_notification_instance = mock_notification.return_value

    # mock_course_db_instance = mock_course_db.return_value
    # mock_course_db_instance.delete_course.return_value = [
    #     {"cursoId": "1", "titulo": "Curso de Python", "instructor": "Ana Pérez", "capacidad": 30},
    #     {"cursoId": "2", "titulo": "Curso de AWS", "instructor": "Luis Martínez", "capacidad": 25}
    # ]

    # event = {'pathParameters': {'cursoId': '1'}}
    # context = {}

    # response = handler(event, context)

    # assert response['statusCode'] == 200
    # body = json.loads(response['body'])
    # assert body['message'] == 'Curso eliminado exitosamente.'

    # mock_table.delete_item.assert_called_once_with(Key={'cursoId': '1'})

    # assert mock_requests_post.call_count == 2

# @patch("src.notifications.requests.post")
# @patch("src.course_get.CourseDB")
# @patch("src.course_get.logger") 
@patch("src.course_delete.CourseDB")
@patch("src.course_delete.Notification")
@patch("src.course_delete.logger")
def test_delete_course_exception(mock_logger, mock_notification, mock_course_db):
    # Configurar mocks para simular error
    mock_db_instance = mock_course_db.return_value
    mock_db_instance.delete_course.side_effect = Exception("Error al eliminar el curso")

    mock_notif_instance = mock_notification.return_value
    mock_notif_instance.send_notification.return_value = None

    # Crear un evento simulado
    event = create_event("curso123")

    # Ejecutar la función
    response = handler(event, None)

    # Verificar respuesta esperada
    assert response["statusCode"] == 500
    assert "error" in json.loads(response["body"])
    assert json.loads(response["body"])["error"] == "Error al eliminar el curso"

    # Verificar que los métodos fueron llamados
    mock_course_db.assert_called_once()
    mock_db_instance.delete_course.assert_called_once_with("curso123")
    mock_notification.assert_called()
    mock_notif_instance.send_notification.assert_any_call('slack', "❌ Error al eliminar el curso: Error al eliminar el curso")
    mock_logger.error.assert_called()