# src/handlers/delete_course.py

import json
import boto3
import os
from src.db import CourseDB
from src.notifications import Notification
from src.logs import logger

def handler(event, context):
    notif = Notification()
    try:
        logger.info("Received event: %s", json.dumps(event))

        curso_id = event['pathParameters']['cursoId']
        db = CourseDB()
        db.delete_course(curso_id)

        mensaje = f"🗑️ El curso '{curso_id}' ha sido eliminado."
        notif.send_notification('slack', mensaje)
        notif.send_notification('teams', mensaje)

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Curso eliminado exitosamente."})
        }

    except Exception as e:
        logger.error("Error al crear el curso: %s", str(e))
        error_message = f"❌ Error al eliminar el curso: {str(e)}"
        notif.send_notification('slack', error_message)
        notif.send_notification('teams', error_message)
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
