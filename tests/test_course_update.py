import json
import pytest
from unittest.mock import patch, MagicMock
from src.course_update import handler

@patch("src.course_update.CourseDB")
@patch("src.course_update.Notification")
@patch("src.course_update.logger")
def test_update_course_success(mock_logger, mock_notification, mock_course_db):
    mock_course_db_instance = mock_course_db.return_value
    mock_notification_instance = mock_notification.return_value

    event = {
        'pathParameters': {'cursoId': '1'},
        'body': json.dumps({"titulo": "Curso de Python Avanzado", "descripcion": "Curso avanzado de Python"})
    }
    context = {}

    # Llamar al handler de la función Lambda
    response = handler(event, context)

    # Verificar que la respuesta sea exitosa
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['message'] == "Curso actualizado exitosamente."

    # Verificar que se haya llamado a update_course en DynamoDB
    update_expression = "SET titulo = :titulo, descripcion = :descripcion"
    expression_attribute_values = {":titulo": "Curso de Python Avanzado", ":descripcion": "Curso avanzado de Python"}
    mock_course_db_instance.update_course.assert_called_once_with("1", update_expression, expression_attribute_values)

    # Verificar que se hayan enviado notificaciones
    mensaje = "🔄 El curso '1' ha sido actualizado."
    mock_notification_instance.send_notification.assert_any_call('slack', mensaje)
    mock_notification_instance.send_notification.assert_any_call('teams', mensaje)

@patch("src.course_update.CourseDB")
@patch("src.course_update.Notification")
@patch("src.course_update.logger")
def test_update_course_exception(mock_logger, mock_notification, mock_course_db):
    mock_course_db_instance = mock_course_db.return_value
    mock_notification_instance = mock_notification.return_value

    # Simular una excepción al intentar actualizar un curso
    mock_course_db_instance.update_course.side_effect = Exception("Simulated DynamoDB exception")

    event = {
        'pathParameters': {'cursoId': '1'},
        'body': json.dumps({"titulo": "Curso de Python Avanzado", "descripcion": "Curso avanzado de Python"})
    }
    context = {}

    # Llamar al handler de la función Lambda
    response = handler(event, context)

    # Verificar que la respuesta sea un error
    assert response['statusCode'] == 500
    body = json.loads(response['body'])
    assert 'error' in body
    assert 'Simulated DynamoDB exception' in body['error']

    # Verificar que se haya registrado el error
    mock_logger.error.assert_called_once()

    # Verificar que se hayan enviado notificaciones de error
    error_message = "❌ Error al actualizar el curso: Simulated DynamoDB exception"
    mock_notification_instance.send_notification.assert_any_call('slack', error_message)
    mock_notification_instance.send_notification.assert_any_call('teams', error_message)