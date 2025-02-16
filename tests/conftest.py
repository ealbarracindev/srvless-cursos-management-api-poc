import pytest
import os
import boto3
from unittest.mock import patch, MagicMock
#from src.db import CourseDB

# @pytest.fixture(scope="module")
# def mock_dynamodb():
#     """
#     Fixture para conectarse a DynamoDB simulado en LocalStack.
#     """
#     endpoint_url = "http://localhost:4566"

#     dynamodb = boto3.resource(
#         "dynamodb",
#         region_name="us-east-1",  # Región ficticia para pruebas
#         endpoint_url=endpoint_url
#     )

#     yield dynamodb

# @pytest.fixture(scope="function")
# def mock_dynamodb_table(mock_dynamodb):
#     """
#     Fixture para configurar y limpiar una tabla DynamoDB para cada test.
#     """
#     table = mock_dynamodb.create_table(
#         TableName="test-table-cursos",
#         KeySchema=[{"AttributeName": "cursoId", "KeyType": "HASH"}],
#         AttributeDefinitions=[{"AttributeName": "cursoId", "AttributeType": "S"}],
#         BillingMode='PAY_PER_REQUEST'
#     )
#     table.meta.client.get_waiter("table_exists").wait(TableName="test-table")
#     yield table
#     table.delete()
#     table.meta.client.get_waiter("table_not_exists").wait(TableName="test-table")

# @pytest.fixture
# def mock_course_db(mock_dynamodb_table):
#     """
#     Fixture para configurar la instancia de CourseDB para usar la tabla simulada.
#     """
#     instance = CourseDB()
#     instance.table = mock_dynamodb_table
#     yield instance


# @pytest.fixture
# def mock_course_db():
#     """
#     Fixture para configurar la instancia de CourseDB para usar la tabla simulada.
#     """
#     instance = CourseDB()
#     yield instance

@pytest.fixture(autouse=True)
def set_env_vars():
    with patch.dict(os.environ, {
        "DYNAMODB_TABLE": "test-table",
        "SLACK_WEBHOOK_URL": "https://mock-slack-webhook-url.com",
        "TEAMS_WEBHOOK_URL": "https://mock-teams-webhook-url.com"
    }):
        yield

# @pytest.fixture(autouse=True)
# def mock_logger():
#     with patch("src.course_delete.logger") as mock_logger:
#         yield mock_logger

# @pytest.fixture(autouse=True)
# def mock_requests_post():
#     with patch("src.notifications.requests.post") as mock_requests_post:
#         yield mock_requests_post

# @pytest.fixture(autouse=True)
# def mock_notification():
#     with patch("src.notifications.Notification") as mock_notification:
#         yield mock_notification