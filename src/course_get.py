# src/handlers/get_course.py

import json
import boto3
import os
from src.notifications import Notification
from src.db import CourseDB
from src.logs import logger

def handler(event, context):    
    try:
        logger.info("Received event: %s", json.dumps(event))
        
        if 'pathParameters' not in event or 'cursoId' not in event['pathParameters']:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing path parameters or cursoId."})
            }

        curso_id = event['pathParameters']['cursoId']
        db = CourseDB()
        curso = db.get_course(curso_id)        

        if not curso:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "Curso no encontrado."})
            }

        return {
            "statusCode": 200,
            "body": json.dumps( curso )
        }
        
    except Exception as e:
        logger.error("Error al crear el curso: %s", str(e))
        error_message = f"❌ Error al obtener los cursos: {str(e)}"
        notif = Notification()
        notif.send_notification('slack', error_message)
        notif.send_notification('teams', error_message)
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
