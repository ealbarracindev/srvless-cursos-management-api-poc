import json
from src.db import CourseDB
from src.notifications import Notification
from src.logs import logger
from src.business_rules import validate_state_transition
from src.state_machine import StateMachine

def handler(event, context):
    try:
        curso_id = event['pathParameters']['cursoId']
        nuevo_estado = json.loads(event['body'])['nuevo_estado']
        
        db = CourseDB()
        notif = Notification()
        
        curso = db.get_course(curso_id)
        
        if not curso:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "Curso no encontrado."})
            }
        
        estado_actual = curso.get('estado')
        
        if estado_actual is None:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Estado actual no válido."})
            }
        
        # Validar transición
        if not validate_state_transition(estado_actual, nuevo_estado):
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Transición de estado no permitida."})
            }
        
        db.update_course_state(curso_id, nuevo_estado)
        
        if nuevo_estado in ["En Curso", "Completado"]:
            mensaje = f"📢 El curso '{curso['titulo']}' ha cambiado su estado a '{nuevo_estado}'."
            notif.send_notification('slack', mensaje)
        
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Estado del curso actualizado exitosamente."})
        }
    
    except ValueError as e:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(e)})
        }
    
    except Exception as e:
        logger.error(f"Error al cambiar el estado del curso: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Error interno del servidor."})
        }