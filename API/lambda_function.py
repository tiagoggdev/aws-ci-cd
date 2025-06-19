import json
import boto3
from decimal import Decimal

# Inicializar el recurso DynamoDB
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Inventarios')

# Clase para convertir Decimal a float
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

def lambda_handler(event, context):
    try:
        # Detectar el método HTTP
        http_method = event['httpMethod']

        # Método POST: insertar nuevo registro
        if http_method == 'POST':
            if 'body' not in event or not event['body']:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": "El cuerpo de la solicitud no está presente o es inválido."})
                }

            body = json.loads(event['body'])
            item_id = body.get("id")
            item_name = body.get("name")
            quantity = body.get("quantity")

            if not item_id or not item_name or quantity is None:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": "Faltan campos obligatorios (id, name o quantity)."})
                }

            table.put_item(Item={"id": item_id, "name": item_name, "quantity": Decimal(str(quantity))})

            return {
                "statusCode": 200,
                "body": json.dumps({"message": "Item agregado", "item_id": item_id})
            }

        # Método GET: consultar uno o todos
        elif http_method == 'GET':
            params = event.get('queryStringParameters')

            # Si viene parámetro 'id', buscar por ID
            if params and 'id' in params:
                item_id = params['id']
                response = table.get_item(Key={"id": item_id})
                item = response.get('Item')

                if not item:
                    return {
                        "statusCode": 404,
                        "body": json.dumps({"error": f"El item con id '{item_id}' no existe."})
                    }

                return {
                    "statusCode": 200,
                    "body": json.dumps(item, cls=DecimalEncoder)
                }

            # Si no hay parámetro, devolver todos
            else:
                response = table.scan()
                items = response.get('Items', [])

                return {
                    "statusCode": 200,
                    "body": json.dumps(items, cls=DecimalEncoder)
                }

        # Método no soportado
        else:
            return {
                "statusCode": 405,
                "body": json.dumps({"error": f"Método '{http_method}' no soportado."})
            }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Error interno", "details": str(e)})
        }
