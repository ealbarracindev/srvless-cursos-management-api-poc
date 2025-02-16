# src/handlers/get_courses.py
import json
import logging
from src.notifications import Notification
from src.db import CourseDB
from src.logs import logger

def handler(event, context):
    try:
        logger.info("Received event: %s", json.dumps(event))

        db = CourseDB()
        cursos = db.get_all_courses()

        return {
            "statusCode": 200,
            "body": json.dumps([curso.to_dict() if hasattr(curso, 'to_dict') else curso for curso in cursos])
        }

    except Exception as e:
        logger.error("Error al obtener los cursos: %s", str(e))
        error_message = f"❌ Error al obtener los cursos: {str(e)}"
        notificaciones = Notification()
        notificaciones.send_notification('slack', error_message)
        notificaciones.send_notification('teams', error_message)
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
