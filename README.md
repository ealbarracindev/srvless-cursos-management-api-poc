## Descripcion del Proyecto
API para la Gestión de Cursos con Estados de Curso y Notificaciones Personalizadas que permiten demostrar una amplia gama de habilidades técnicas, incluyendo la gestión de estados, integración de notificaciones, implementación de seguridad, y uso de diversas herramientas de AWS.

## Estructura de Carpetas y Archivos
```
srvless-curso-management-api-poc/
│
├── README.md
├── template.yaml                # Plantilla SAM para CloudFormation
├── .gitignore
├── requirements.txt              # Dependencias de Python
│
├── src/
│   ├── auth/
│   │   └── authorizer.py         # Función Lambda autorizadora
│   │
│   ├── handlers/
│   │   ├── create_course.py      # Crear cursos
│   │   ├── get_course.py         # Obtener cursos
│   │   ├── update_course.py      # Actualizar cursos
│   │   ├── delete_course.py      # Eliminar cursos
│   │   ├── change_course_state.py# Cambiar estado de cursos
│   │   └── notications.py             # Enviar notificaciones
│   │
│   ├── models/
│   │   └── course.py             # Modelos de datos (DynamoDB)
│   │
│   ├── utils/
│   │   ├── db.py                 # Conexión y operaciones con DynamoDB
│   │   └── notifications.py      # Integración con SNS/SES y Webhooks
│   │
│   └── app.py                    # Punto de entrada (si aplica)
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py               # Configuración de pytest
│   ├── test_create_course.py
│   ├── test_get_course.py
│   ├── test_update_course.py
│   ├── test_delete_course.py
│   ├── test_change_course_state.py
│   └── test_notify.py
│
└── scripts/
    └── deploy.sh                  # Script de despliegue (opcional)
```
## Diagrama de Flujo Simplificado

```
Cliente (HTTP Request)
       |
       v
Amazon API Gateway
       |
       v
Lambda Authorizer (Autenticación y Autorización)
       |
       v
Lambda Handlers (Operaciones CRUD y Lógica de Negocio)
       |
       v
Amazon DynamoDB (Almacenamiento de Datos)
       |
       v
Amazon SNS/SES/Webhooks (Notificaciones)
       |
       v
Monitoreo con Amazon CloudWatch

```
## Reglas de Negocio

1. Gestión de Estados de Curso:
Estados Permitidos: "Planeado", "En Curso", "Completado", "Cancelado".
Transiciones Válidas:
"Planeado" → "En Curso"
"En Curso" → "Completado"
"Planeado" → "Cancelado"
"En Curso" → "Cancelado"
Restricciones: No permitir transiciones directas de "Planeado" a "Completado" o de "Completado" a cualquier otro estado.
2. Capacidad de Curso:
Límite de Estudiantes: Cada curso tiene un número máximo de estudiantes inscritos.
Gestión de Listas de Espera: Si un curso está lleno, las nuevas inscripciones se añaden a una lista de espera.
3. Validación de Inscripción:
Requisitos de Curso: Los estudiantes deben cumplir ciertos requisitos (por ejemplo, completar cursos previos) para inscribirse en cursos avanzados.
Inscripción Única: Un estudiante no puede inscribirse múltiples veces en el mismo curso.
4. Emisión de Certificados:
Criterios de Finalización: Solo emitir certificados a estudiantes que han completado el curso y han alcanzado una calificación mínima.

## Ejemplos de Alertas
1. Notificaciones de Negocio:

Cambio de Estado de Curso:
Evento: Un curso cambia de "Planeado" a "En Curso".
Notificación: Enviar un mensaje al canal de instructores y estudiantes en Slack/Teams informando sobre el inicio del curso.
Emisión de Certificados:
Evento: Un estudiante completa un curso exitosamente y recibe un certificado.
Notificación: Enviar un correo electrónico y un mensaje a un canal de logros en Slack/Teams notificando al estudiante y a los administradores.
2. Alertas de Errores:
    2.1 Transición de Estado Inválida:
        Evento: Intento de cambiar el estado de un curso de "Planeado" a "Completado" directamente.
        Alerta: Enviar una alerta al canal de soporte técnico en Slack/Teams indicando una tentativa de transición inválida.
    
    2.2 Falla en la Inscripción:
        Evento: Error al inscribir a un estudiante debido a restricciones de capacidad o requisitos no cumplidos.
        Alerta: Enviar una notificación al canal de errores en Teams/Slack para su revisión inmediata.

    2.3 Alertas de Rendimiento:
        Latencia Alta en Lambda:
            Evento: Una función Lambda excede el tiempo de ejecución esperado.
            Alerta: Enviar una alerta al canal de infraestructura en Slack/Teams para investigar el problema.
    2.4 Errores de Lambda:
        Evento: Un incremento en los errores 5xx de las funciones Lambda.
        Alerta: Enviar una alerta crítica al canal de operaciones en Slack/Teams.

## Detalles del template.yaml
CursosTable: Tabla de DynamoDB para almacenar información de los cursos.
SNSTopic: Tema de SNS para enviar notificaciones.
SlackWebhookURL: Parámetro de SSM para almacenar la URL del webhook de Slack (puedes usar Teams de manera similar).
AuthorizerFunction: Función Lambda para la autorización personalizada.
CursosApi: API Gateway con endpoints definidos para operaciones CRUD y cambio de estado.
Funciones Lambda:
CreateCursoFunction
GetCursosFunction
GetCursoFunction
UpdateCursoFunction
DeleteCursoFunction
ChangeCourseStateFunction

## Inicio del proyecto

powershell
windows:
$ Crear la carpeta de ambiente para las dependencias
$ cd /path/proyecto
$ py -m venv venv
$ source .\venv\Script\activate

### Ejecutar en PS desde el siguiente origin --> venv/Scripts `.\Activate.ps1`
```bash
$ pip install -r requirements.txt
$ pip install -r publisher/requirements.txt
$ pip install -r tests/unit/requirements.txt
```
## Deploy the sample application

To build and deploy your application for the first time, run the following in your shell:

```bash
sam validate --lint
sam build
sam build --cached
sam deploy --guided
```

## Tests
Tests son definidos en la carpeta `tests`. Usar PIP para instalar dependencias y correr los tests.
```powershell
windows:
$ cd /path/proyecto
$ py -m venv venv
$ source .\venv\Script\activate
```
### ejecutar en PS desde el siguiente origin --> venv/Scripts `.\Activate.ps1`
$ pip install -r tests/unit/requirements.txt
$ pip install -r requirements.txt
$ Para validar estructura del template
### `sam validate --lint`
$ py tests
### Para ejecutar los tests
pytest

### Para ejecutar pruebas especificas
pytest -k "MyClass and not method"
pytest --fail-first
pytest --last-failed
pytest --failed-first

### Para agregar marcadores en los tests
@pytest.mark.slow
@pytest.mark.current
pytest.mark.skip(reason="este tests falta verificar la simulacion de topico")
pytest.mark.xfail
def test_this():
    ...
Para ejecutar el o los tests marcados se puede hacer con los siguientes comandos:
pytest -m current -s -v
pytest -m 'slow and not integration'
pytest -m 'smoke and unit'

$ Para ejecutar los tests con mas detalles (verbose)
### `pytest -v`
### `coverage run -m pytest`
### `coverage report -m`
$ deactivate

## Comandos para AWS CLI
```bash
CloudFormation:
aws cloudformation help
aws cloudformation delete-stack --stack-name srvless-merval-publisher-poc --debug
aws cloudformation describe-stacks --stack-name srvless-merval-publisher-poc
aws cloudformation describe-stack-events --stack-name srvless-merval-publisher-poc #(para obtener más detalles sobre el error específico)
aws cloudformation describe-stack-resources --stack-name srvless-merval-publisher-poc
aws cloudformation describe-stacks --stack-name srvless-merval-publisher-poc

Lambdas:
aws lambda help
aws lambda invoke --function-name apps-dev-merval-function --payload '{}' output.txt

Caso 30 dias
$logResult = aws lambda invoke --function-name apps-dev-merval-function --payload '{\"Input\":{\"cant_dias\":\"30\", \"tipo\":\"mensual\"}}' --cli-binary-format raw-in-base64-out output.txt --log-type Tail --query 'LogResult' --output text
[System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($logResult))

Caso 60 dias solo para mobile
$logResult = aws lambda invoke --function-name apps-dev-merval-function --payload '{\"Input\":{\"cant_dias\":\"60\", \"tipo\":\"anual\"}}' --cli-binary-format raw-in-base64-out output.txt --log-type Tail --query 'LogResult' --output text
[System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($logResult))

aws lambda invoke --function-name apps-dev-merval-function --payload file://payload.json --cli-binary-format raw-in-base64-out output.txt
aws lambda invoke --function-name apps-dev-merval-function --payload '{"mensaje":"prueba_sns", "filtro":"value2"}' output.txt
aws lambda invoke --function-name apps-dev-merval-anual-function --payload file://payload.json output.txt
aws lambda invoke \
    --function-name apps-dev-merval-anual-function \
    --payload '{"mensaje": "prueba de mensaje sns hacia una cola sqs", "filtro": "value2"}' \
    output.txt
aws lambda invoke \
    --function-name apps-dev-merval-anual-function \
    --payload '{"mensaje": "prueba de mensaje sns hacia una cola sqs", "filtro": "value2"}' \
    output.txt    

SQS
aws sqs help
aws sqs list list-queues https://sqs.us-east-1.amazonaws.com/875766450028/merval-anual-cola-sqs

aws sqs receive-message --queue-url https://sqs.us-east-1.amazonaws.com/875766450028/merval-para-api-net

IAM
aws sts get-caller-identity
aws iam list-attached-role-policies --role-name

Exportación de OpenAPI

aws apigateway get-export \
    --rest-api-id <api-id> \
    --stage-name dev \
    --export-type swagger \
    --output-file cursos-api.json \
    --accepts application/json

aws apigateway get-export --rest-api-id w4sh2c5cvi --stage-name dev --export-type swagger --output-file cursos-api.json --accepts application/json

aws apigateway get-export --rest-api-id 'cdjl5u7ah8'  --stage-name dev --export-type swagger --accepts application/json --output json docs/swagger-cursos-api.json

aws apigateway get-export --rest-api-id 'cdjl5u7ah8'  --stage-name dev --export-type swagger --accepts application/yaml --output yaml docs/swagger-cursos-api.yaml


Formato OpenAPI 3.0

aws apigateway get-export --rest-api-id 'w4sh2c5cvi'  --stage-name dev --export-type oas30 --accepts application/json --output json docs/swagger-cursos-api.json

aws apigateway get-export --rest-api-id 'cdjl5u7ah8'  --stage-name dev --export-type oas30 --accepts application/yaml --output yaml docs/swagger-cursos-api.yaml
```
