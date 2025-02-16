import pytest
import os
from unittest.mock import patch, MagicMock
from src.db import CourseDB 
from decimal import Decimal


@patch("boto3.resource")
def test_create_course(mock_boto3_resource):
    course_data = {
        'cursoId': '123',
        'titulo': 'Curso de Python',
        'descripcion': 'Aprender Python desde cero',
        'instructor': 'Juan Perez',
        'capacidad': 50,
        'estado': 'activo'
    }

    # Mock del recurso de DynamoDB
    mock_table = MagicMock()
    mock_boto3_resource.return_value.Table.return_value = mock_table

    # Crear instancia de la clase
    db_instance = CourseDB(table_name="TestTable")
    db_instance.create_course(course_data)

    # Verificar que se haya llamado put_item con los argumentos correctos
    mock_table.put_item.assert_called_once_with(Item=course_data)

@patch("boto3.resource")
def test_get_course(mock_boto3_resource):
    curso_id = '123'
    course_data = {
        'cursoId': '123',
        'titulo': 'Curso de Python',
        'descripcion': 'Aprender Python desde cero',
        'instructor': 'Juan Perez',
        'capacidad': 50,
        'estado': 'activo'
    }

    # Mock del recurso de DynamoDB
    mock_table = MagicMock()
    mock_boto3_resource.return_value.Table.return_value = mock_table
    mock_table.get_item.return_value = {'Item': course_data}

    # Crear instancia de la clase
    db_instance = CourseDB(table_name="TestTable")
    result = db_instance.get_course(curso_id)

    # Verificar que se haya llamado get_item con los argumentos correctos
    mock_table.get_item.assert_called_once_with(Key={'cursoId': curso_id})

    # Verificar el resultado
    assert result == course_data

@patch("boto3.resource")
def test_update_course(mock_boto3_resource):
    curso_id = '123'
    update_expression = "SET titulo = :t"
    expression_values = {":t": "Curso de Python Avanzado"}

    # Mock del recurso de DynamoDB
    mock_table = MagicMock()
    mock_boto3_resource.return_value.Table.return_value = mock_table

    # Crear instancia de la clase
    db_instance = CourseDB(table_name="TestTable")
    db_instance.update_course(curso_id, update_expression, expression_values)

    # Verificar que se haya llamado update_item con los argumentos correctos
    mock_table.update_item.assert_called_once_with(
        Key={'cursoId': curso_id},
        UpdateExpression=update_expression,
        ExpressionAttributeValues=expression_values,
        ReturnValues="UPDATED_NEW"
    )
    
@patch("boto3.resource")
def test_get_all_courses(mock_boto3_resource):
    courses_data = [
        {
            'cursoId': '123',
            'titulo': 'Curso de Python',
            'descripcion': 'Aprender Python desde cero',
            'instructor': 'Juan Perez',
            'capacidad': Decimal('50'),
            'estado': 'activo'
        },
        {
            'cursoId': '124',
            'titulo': 'Curso de Java',
            'descripcion': 'Aprender Java avanzado',
            'instructor': 'Maria Lopez',
            'capacidad': Decimal('30'),
            'estado': 'activo'
        }
    ]

    # Mock del recurso de DynamoDB
    mock_table = MagicMock()
    mock_boto3_resource.return_value.Table.return_value = mock_table
    mock_table.scan.return_value = {'Items': courses_data}

    # Crear instancia de la clase
    db_instance = CourseDB(table_name="TestTable")
    result = db_instance.get_all_courses()

    # Verificar que se haya llamado scan
    mock_table.scan.assert_called_once_with()

    # Verificar el resultado
    assert result == [
        {
            'cursoId': '123',
            'titulo': 'Curso de Python',
            'descripcion': 'Aprender Python desde cero',
            'instructor': 'Juan Perez',
            'capacidad': 50.0,
            'estado': 'activo'
        },
        {
            'cursoId': '124',
            'titulo': 'Curso de Java',
            'descripcion': 'Aprender Java avanzado',
            'instructor': 'Maria Lopez',
            'capacidad': 30.0,
            'estado': 'activo'
        }
    ]


@patch("src.db.CourseDB.update_course")  # Mockea el método update_course
def test_update_course_state(mock_update_course):
    curso_id = '123'
    nuevo_estado = 'activo'
    
    # Crear instancia de la clase
    db_instance = CourseDB(table_name="TestTable")
    db_instance.update_course_state(curso_id, nuevo_estado)
    
    # Verificar que el método update_course se llame con los argumentos correctos
    mock_update_course.assert_called_once_with(curso_id, "SET estado = :s", {":s": nuevo_estado})

@patch("boto3.resource")
def test_delete_course(mock_boto3_resource):
    curso_id = '123'

    # Mock del recurso de DynamoDB
    mock_table = MagicMock()
    mock_boto3_resource.return_value.Table.return_value = mock_table

    # Crear instancia de la clase
    db_instance = CourseDB(table_name="TestTable")
    db_instance.delete_course(curso_id)

    # Verificar que se haya llamado delete_item con los argumentos correctos
    mock_table.delete_item.assert_called_once_with(Key={'cursoId': curso_id})

def test_convert_decimal():
    db_instance = CourseDB(table_name="TestTable")  # Instancia sin conexión real

    item = {
        'price': Decimal('19.99'),
        'details': {
            'weight': Decimal('1.5')
        },
        'tags': [Decimal('1'), Decimal('2')]
    }

    converted_item = db_instance._convert_decimal(item)

    assert converted_item == {
        'price': 19.99,
        'details': {
            'weight': 1.5
        },
        'tags': [1.0, 2.0]
    }

@patch("boto3.resource")
def test_get_course_by_title_and_instructor(mock_boto3_resource):
    titulo = 'Curso de Python'
    instructor = 'Juan Perez'

    # Mock del recurso de DynamoDB
    mock_table = MagicMock()
    mock_boto3_resource.return_value.Table.return_value = mock_table
    mock_table.query.return_value = {'Items': [{'titulo': titulo, 'instructor': instructor}]}

    # Crear instancia de la clase
    db_instance = CourseDB(table_name="TestTable")

    result = db_instance.get_course_by_title_and_instructor(titulo, instructor)

    # Verificar que se haya llamado query con los argumentos correctos
    mock_table.query.assert_called_once_with(
        IndexName='titulo-instructor-index',
        KeyConditionExpression='titulo = :t AND instructor = :i',
        ExpressionAttributeValues={':t': titulo, ':i': instructor}
    )

    # Verificar el resultado
    assert result == {'titulo': titulo, 'instructor': instructor}