import json
import os


def lambda_handler(event, context):
    
    swagger_path = os.path.join(os.path.dirname(__file__), "../swagger-cursos-api.json") 

    try:        
        with open(swagger_path, "r") as f:
            swagger_content = json.load(f)
            
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps(swagger_content)
        }
    
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
