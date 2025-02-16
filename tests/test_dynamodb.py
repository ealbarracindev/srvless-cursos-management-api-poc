def test_dynamodb_with_localstack(mock_dynamodb):
    """
    Prueba para crear una tabla en DynamoDB usando LocalStack.
    """
    # Crear una tabla de prueba
    table = mock_dynamodb.create_table(
        TableName="test-table-localstack",
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
        ProvisionedThroughput={"ReadCapacityUnits": 1, "WriteCapacityUnits": 1},
    )

    # Esperar a que la tabla esté activa
    table.meta.client.get_waiter("table_exists").wait(TableName="test-table")

    # Verificar que la tabla se creó correctamente
    assert table.table_status == "ACTIVE"
    print("¡La tabla DynamoDB se creó correctamente en LocalStack!")

    # Eliminar la tabla después de la prueba
    table.delete()
    table.meta.client.get_waiter("table_not_exists").wait(TableName="test-table")
    print("¡La tabla DynamoDB se eliminó correctamente después de la prueba!")