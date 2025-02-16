import os
import boto3
from .course import Course
from decimal import Decimal

class CourseDB:
    
    def __init__(self, table_name=None):
        self.table_name = table_name or os.getenv('DYNAMODB_TABLE')
        if not self.table_name:
            raise EnvironmentError("La variable de entorno 'DYNAMODB_TABLE' no está configurada")
        
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(self.table_name)

    def get_all_courses(self) -> list:
        response = self.table.scan()
        fields = ['cursoId', 'titulo', 'descripcion', 'instructor', 'capacidad', 'estado']
        return [
            {field: self._convert_decimal(item[field]) for field in fields}
            for item in response.get("Items", [])
        ]

    def get_course(self, curso_id):
        response = self.table.get_item(Key={'cursoId': curso_id})
        item = response.get('Item')
        return self._convert_decimal(item) if item else None

    def create_course(self, course_data):
        self.table.put_item(Item=course_data)

    def update_course(self, curso_id, update_expression, expression_values):
        self.table.update_item(
            Key={'cursoId': curso_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_values,
            ReturnValues="UPDATED_NEW"
        )

    def update_course_state(self, curso_id, nuevo_estado):
        update_expression = "SET estado = :s"
        expression_values = {":s": nuevo_estado}
        self.update_course(curso_id, update_expression, expression_values)

    def delete_course(self, curso_id):
        self.table.delete_item(Key={'cursoId': curso_id})

    def _convert_decimal(self, item):
        """Convierte los valores de tipo Decimal a tipos serializables"""
        if isinstance(item, list):
            return [self._convert_decimal(i) for i in item]
        elif isinstance(item, dict):
            return {k: self._convert_decimal(v) for k, v in item.items()}
        elif isinstance(item, Decimal):
            return float(item)
        else:
            return item

    def get_course_by_title_and_instructor(self, titulo: str, instructor: str) -> dict | None:
        """
        Obtiene un curso basado en el título y el instructor.

        :param titulo: Título del curso.
        :param instructor: Nombre del instructor.
        :return: Curso encontrado o None.
        """
        response = self.table.query(
            IndexName='titulo-instructor-index',
            KeyConditionExpression="titulo = :t AND instructor = :i",
            ExpressionAttributeValues={
                ":t": titulo,
                ":i": instructor
            }
        )
        items = response.get('Items', [])
        return self._convert_decimal(items[0]) if items else None
