import json
import os
from unittest.mock import patch, MagicMock
import pytest 
from src.course_create import handler

@patch.dict(os.environ, {
    "DYNAMODB_TABLE": "CursosTable",
    "SLACK_WEBHOOK_URL": "https://mock-slack-webhook-url.com",
    "TEAMS_WEBHOOK_URL": "https://mock-teams-webhook-url.com"
})
@patch("src.db.boto3.resource")  # Simular boto3.resource para DynamoDB
@patch("src.notifications.requests.post")
@patch("src.course_create.logger")  # Mockear el logger
def test_create_course_success(mock_logger, mock_requests_post, mock_dynamodb_resource):
    mock_table = MagicMock()
    mock_dynamodb_resource.return_value.Table.return_value = mock_table

    mock_table.query.return_value = {"Items": []}

    # Simular el evento de API Gateway
    event = {
        "body": json.dumps({
            "titulo": "Introducción a Python 2",
            "descripcion": "Curso básico de Python",
            "instructor": "Ana Pérez",
            "capacidad": 30
        }),
        # "requestContext": {
        #     "authorizer": {
        #         "principalId": "test-user"
        #     }
        # }
    }

    # Llamar al handler de la función Lambda
    response = handler(event, None)

    # Verificar que la respuesta sea exitosa
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["message"] == "Curso creado exitosamente."

    # Verificar que se haya llamado a put_item en DynamoDB
    mock_table.put_item.assert_called_once()

    # Verificar que se hayan enviado notificaciones
    assert mock_requests_post.call_count == 2

@patch.dict(os.environ, {
    "DYNAMODB_TABLE": "CursosTable",
    "SLACK_WEBHOOK_URL": "https://mock-slack-webhook-url.com",
    "TEAMS_WEBHOOK_URL": "https://mock-teams-webhook-url.com"
})
@patch("src.db.boto3.resource")  # Simular boto3.resource para DynamoDB
@patch("src.notifications.requests.post")
@patch("src.course_create.logger")  # Mockear el logger
def test_create_course_exception(mock_logger, mock_requests_post, mock_dynamodb_resource):
    # Configurar el mock de DynamoDB
    mock_table = MagicMock()
    mock_dynamodb_resource.return_value.Table.return_value = mock_table

    # Simular una excepción al intentar crear un curso
    mock_table.put_item.side_effect = Exception("Simulated DynamoDB exception")

    # Simular el evento de API Gateway
    event = {
        "body": json.dumps({
            "titulo": "Introducción a Python 2",
            "descripcion": "Curso básico de Python",
            "instructor": "Ana Pérez",
            "capacidad": 30
        }),
        "requestContext": {
            "authorizer": {
                "principalId": "test-user"
            }
        }
    }

    response = handler(event, None)

    # Verificar que la respuesta sea un error
    assert response["statusCode"] == 500
    body = json.loads(response["body"])
    assert "error" in body

    # Verificar que se haya registrado el error
    mock_logger.error.assert_called_once()

    # Verificar que se hayan enviado notificaciones de error
    assert mock_requests_post.call_count == 2