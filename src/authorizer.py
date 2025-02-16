import json

def lambda_handler(event, context):
    token = event['authorizationToken']
    method_arn = event['methodArn']

    # Verificar el token (esto es solo un ejemplo, implementa tu propia lógica de verificación)
    if token == "allow":
        effect = "Allow"
    elif token == "deny":
        effect = "Deny"
    else:
        effect = "Deny"

    return generate_policy("user", effect, method_arn)

def generate_policy(principal_id, effect, method_arn):
    if not effect or not method_arn:
        return None

    return {
        'principalId': principal_id,
        'policyDocument': {
            'Version': '2012-10-17',
            'Statement': [
                {
                    'Action': 'execute-api:Invoke',
                    'Effect': effect,
                    'Resource': method_arn
                }
            ]
        }
    }