
def lambda_handler(event, context):
    swagger_ui_html = """<!DOCTYPE html>
                    <html>
                    <head>
                    <title>API Cursos - Swagger UI</title>
                    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/4.5.0/swagger-ui.css">
                    </head>
                    <body>
                    <div id="swagger-ui"></div>
                    <script src="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/4.5.0/swagger-ui-bundle.js"></script>
                    <script>
                        window.onload = function() {
                        SwaggerUIBundle({
                            url: "https://cdjl5u7ah8.execute-api.us-east-1.amazonaws.com/dev/docs",
                            dom_id: "#swagger-ui",
                        });
                        };
                    </script>
                    </body>
                    </html>"""

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "text/html",
            "Access-Control-Allow-Origin": "*"
        },
        "body": swagger_ui_html
    }
