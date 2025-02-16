# src/handlers/create_course.py

import json
import uuid
import boto3
import os
from datetime import datetime
from src.db import CourseDB
from src.notifications import Notification
from src.logs import logger

def handler(event, context):
    notif = Notification()
    try:
        logger.info("Received event: %s", json.dumps(event))

        body = json.loads(event['body'])
        titulo = body['titulo']
        descripcion = body['descripcion']
        instructor = body['instructor']
        capacidad = body['capacidad']

        db = CourseDB()
        existing_course = db.get_course_by_title_and_instructor(titulo, instructor)
        if existing_course:
            raise ValueError("Ya existe un curso con el mismo título e instructor.")

        curso_id = str(uuid.uuid4())
        curso_item = {
            'cursoId': curso_id,
            'titulo': titulo,
            'descripcion': descripcion,
            'instructor': instructor,
            'capacidad': capacidad,
            'inscritos': 0,
            'estado': 'Planeado',
            'fechaCreacion': datetime.utcnow().isoformat()
        }
        
        db.create_course(curso_item)
        
        mensaje = f"📢 Nuevo curso creado: '{titulo}' por {instructor}."
        notif.send_notification('slack', mensaje)
        notif.send_notification('teams', mensaje)

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Curso creado exitosamente.", "cursoId": curso_id})
        }

    except Exception as e:
        error_message = f"❌ Error al crear el curso: {str(e)}"
        logger.error("Error al crear el curso: %s", str(e))
        notif.send_notification('slack', error_message)
        notif.send_notification('teams', error_message)
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
