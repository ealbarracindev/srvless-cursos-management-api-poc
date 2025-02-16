# src/handlers/update_course.py

import json
import boto3
import os
from .notifications import Notification
from .db import CourseDB
from .logs import logger

def handler(event, context):
    notif = Notification()
    try:
        curso_id = event['pathParameters']['cursoId']
        body = json.loads(event['body'])

        update_expression = "SET "
        expression_attribute_values = {}
        for key, value in body.items():
            update_expression += f"{key} = :{key}, "
            expression_attribute_values[f":{key}"] = value
        
        update_expression = update_expression.rstrip(', ')

        db = CourseDB()
        db.update_course(curso_id, update_expression, expression_attribute_values)

        mensaje = f"🔄 El curso '{curso_id}' ha sido actualizado."
        notif.send_notification('slack', mensaje)
        notif.send_notification('teams', mensaje)

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Curso actualizado exitosamente."})
        }

    except Exception as e:
        logger.error("Error al crear el curso: %s", str(e))
        error_message = f"❌ Error al actualizar el curso: {str(e)}"
        notif.send_notification('slack', error_message)
        notif.send_notification('teams', error_message)
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
