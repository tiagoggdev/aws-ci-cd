import json
import logging
import boto3
from botocore.exceptions import ClientError
from decimal import Decimal  # para serializar Decimal

# Configurar logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Cliente DynamoDB
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('users')  # Nombre de la tabla DynamoDB


# Clase personalizada para serializar Decimals
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return int(obj) if obj % 1 == 0 else float(obj)
        return super(DecimalEncoder, self).default(obj)


def lambda_handler(event, context):
    """
    Función principal de Lambda con persistencia REAL en DynamoDB
    """
    
    logger.info(f"Evento recibido: {json.dumps(event, default=str, cls=DecimalEncoder)}")
    
    # Extraer información del evento
    http_method = event.get('httpMethod', '')
    path_parameters = event.get('pathParameters') or {}
    raw_body = event.get('body')
    
    # Parsear JSON del body
    request_data = None
    if raw_body:
        try:
            request_data = json.loads(raw_body)
            logger.info(f"Datos recibidos: {request_data}")
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON: {e}")
            return create_response(400, {
                "success": False,
                "message": "JSON inválido en el cuerpo de la petición",
                "error": str(e)
            })
    
    # Enrutamiento según método HTTP
    try:
        logger.info(f"Procesando método: {http_method}")
        
        if http_method == 'GET':
            return handle_get_real(path_parameters)
        elif http_method == 'POST':
            return handle_post_real(request_data)
        elif http_method == 'PUT':
            return handle_put_real(path_parameters, request_data)
        elif http_method == 'DELETE':
            return handle_delete_real(path_parameters)
        else:
            logger.warning(f"Método no permitido: {http_method}")
            return create_response(405, {
                "success": False,
                "message": f"Método {http_method} no permitido",
                "allowed_methods": ["GET", "POST", "PUT", "DELETE"]
            })
            
    except Exception as e:
        logger.error(f"Error interno: {str(e)}", exc_info=True)
        return create_response(500, {
            "success": False,
            "message": "Error interno del servidor",
            "error": str(e)
        })

def create_response(status_code, body_data):
    """Crear respuesta HTTP con headers CORS"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json; charset=utf-8',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
            'Access-Control-Max-Age': '86400'
        },
        'body': json.dumps(body_data, ensure_ascii=False, indent=2, cls=DecimalEncoder)
    }

def handle_get_real(path_parameters):
    """Manejar peticiones GET con DynamoDB"""
    user_id = path_parameters.get('id')
    
    try:
        if user_id:
            # GET /users/{id} - Obtener usuario específico
            logger.info(f"Buscando usuario con ID: {user_id}")
            
            try:
                user_id = int(user_id)
                
                response = table.get_item(Key={'id': user_id})
                
                if 'Item' in response:
                    user = response['Item']
                    logger.info(f"Usuario encontrado: {user['name']}")
                    return create_response(200, {
                        "success": True,
                        "data": user,
                        "message": f"Usuario con ID {user_id} encontrado"
                    })
                else:
                    logger.warning(f"Usuario con ID {user_id} no encontrado")
                    return create_response(404, {
                        "success": False,
                        "message": f"Usuario con ID {user_id} no existe"
                    })
                    
            except ValueError:
                logger.error(f"ID inválido: {user_id}")
                return create_response(400, {
                    "success": False,
                    "message": "El ID del usuario debe ser un número entero",
                    "received": user_id
                })
        else:
            # GET /users - Obtener todos los usuarios
            logger.info("Obteniendo todos los usuarios de DynamoDB")
            
            response = table.scan()
            users = response['Items']
            
            # Ordenar por ID
            users.sort(key=lambda x: x['id'])
            
            logger.info(f"Usuarios encontrados: {len(users)}")
            return create_response(200, {
                "success": True,
                "data": users,
                "count": len(users),
                "message": f"Se encontraron {len(users)} usuarios"
            })
            
    except ClientError as e:
        logger.error(f"Error DynamoDB: {e}")
        return create_response(500, {
            "success": False,
            "message": "Error accediendo a la base de datos",
            "error": str(e)
        })

def handle_post_real(request_data):
    """Manejar peticiones POST - Crear usuario en DynamoDB"""
    logger.info("Procesando creación de nuevo usuario")
    
    # Validar que existan datos
    if not request_data:
        return create_response(400, {
            "success": False,
            "message": "Se requieren datos del usuario",
            "required_fields": ["name", "email"]
        })
    
    # Extraer y limpiar datos
    name = request_data.get('name', '').strip()
    email = request_data.get('email', '').strip()
    role = request_data.get('role', 'user').strip()
    
    # Validaciones
    validation_errors = []
    
    if not name:
        validation_errors.append("El nombre es obligatorio")
    elif len(name) < 2:
        validation_errors.append("El nombre debe tener al menos 2 caracteres")
    
    if not email:
        validation_errors.append("El email es obligatorio")
    elif not is_valid_email(email):
        validation_errors.append("El formato del email es inválido")
    
    if validation_errors:
        return create_response(400, {
            "success": False,
            "message": "Errores de validación",
            "errors": validation_errors
        })
    
    try:
        # Verificar email único
        response = table.scan(
            FilterExpression=boto3.dynamodb.conditions.Attr('email').eq(email)
        )
        
        if response['Items']:
            logger.warning(f"Email duplicado: {email}")
            return create_response(409, {
                "success": False,
                "message": "Ya existe un usuario con ese email",
                "email": email
            })
        
        # Obtener el siguiente ID disponible
        response = table.scan()
        existing_ids = [item['id'] for item in response['Items']]
        new_id = max(existing_ids, default=0) + 1
        
        # Validar rol
        valid_roles = ['admin', 'user', 'moderator']
        if role not in valid_roles:
            role = 'user'
        
        # Crear nuevo usuario
        new_user = {
            'id': new_id,
            'name': name,
            'email': email,
            'role': role
        }
        
        # Guardar en DynamoDB
        table.put_item(Item=new_user)
        
        logger.info(f"Usuario guardado en DynamoDB: {new_user}")
        
        return create_response(201, {
            "success": True,
            "message": f"Usuario '{name}' creado exitosamente",
            "data": new_user
        })
        
    except ClientError as e:
        logger.error(f"Error DynamoDB: {e}")
        return create_response(500, {
            "success": False,
            "message": "Error guardando en la base de datos",
            "error": str(e)
        })

def handle_put_real(path_parameters, request_data):
    """Manejar peticiones PUT - Actualizar usuario en DynamoDB"""
    user_id = path_parameters.get('id')
    
    logger.info(f"Procesando actualización de usuario ID: {user_id}")
    
    # Validar ID en la URL
    if not user_id:
        return create_response(400, {
            "success": False,
            "message": "Se requiere el ID del usuario en la URL",
            "format": "/users/{id}"
        })
    
    # Validar datos en el body
    if not request_data:
        return create_response(400, {
            "success": False,
            "message": "Se requieren datos para actualizar",
            "allowed_fields": ["name", "email", "role"]
        })
    
    try:
        user_id = int(user_id)
        
        # Verificar que el usuario existe
        response = table.get_item(Key={'id': user_id})
        
        if 'Item' not in response:
            logger.warning(f"Usuario con ID {user_id} no encontrado")
            return create_response(404, {
                "success": False,
                "message": f"Usuario con ID {user_id} no existe"
            })
        
        current_user = response['Item']
        update_expression = "SET "
        expression_values = {}
        updates = []
        
        # Validaciones y preparación de updates
        validation_errors = []
        
        if 'name' in request_data:
            name = request_data['name'].strip()
            if name and len(name) >= 2:
                updates.append("#n = :name")
                expression_values[':name'] = name
            elif not name:
                validation_errors.append("El nombre no puede estar vacío")
            else:
                validation_errors.append("El nombre debe tener al menos 2 caracteres")
        
        if 'email' in request_data:
            email = request_data['email'].strip()
            if email and is_valid_email(email):
                # Verificar email único (excluyendo usuario actual)
                scan_response = table.scan(
                    FilterExpression=boto3.dynamodb.conditions.Attr('email').eq(email) & 
                                   boto3.dynamodb.conditions.Attr('id').ne(user_id)
                )
                
                if scan_response['Items']:
                    validation_errors.append("Ya existe otro usuario con ese email")
                else:
                    updates.append("email = :email")
                    expression_values[':email'] = email
            elif not email:
                validation_errors.append("El email no puede estar vacío")
            else:
                validation_errors.append("Formato de email inválido")
        
        if 'role' in request_data:
            role = request_data['role'].strip()
            valid_roles = ['admin', 'user', 'moderator']
            if role in valid_roles:
                updates.append("#r = :role")
                expression_values[':role'] = role
            else:
                validation_errors.append(f"Rol inválido. Valores permitidos: {', '.join(valid_roles)}")
        
        # Si hay errores, retornar
        if validation_errors:
            return create_response(400, {
                "success": False,
                "message": "Errores de validación",
                "errors": validation_errors
            })
        
        if not updates:
            return create_response(400, {
                "success": False,
                "message": "No se proporcionaron campos válidos para actualizar"
            })
        
        # Ejecutar actualización
        update_expression += ", ".join(updates)
        expression_names = {}
        if "#n" in update_expression:
            expression_names["#n"] = "name"
        if "#r" in update_expression:
            expression_names["#r"] = "role"
        
        update_params = {
            'Key': {'id': user_id},
            'UpdateExpression': update_expression,
            'ExpressionAttributeValues': expression_values,
            'ReturnValues': 'ALL_NEW'
        }
        
        if expression_names:
            update_params['ExpressionAttributeNames'] = expression_names
        
        response = table.update_item(**update_params)
        updated_user = response['Attributes']
        
        logger.info(f"Usuario actualizado en DynamoDB: {updated_user}")
        
        return create_response(200, {
            "success": True,
            "message": f"Usuario '{updated_user['name']}' actualizado exitosamente",
            "data": updated_user
        })
        
    except ValueError:
        return create_response(400, {
            "success": False,
            "message": "El ID del usuario debe ser un número entero",
            "received": user_id
        })
    except ClientError as e:
        logger.error(f"Error DynamoDB: {e}")
        return create_response(500, {
            "success": False,
            "message": "Error actualizando en la base de datos",
            "error": str(e)
        })

def handle_delete_real(path_parameters):
    """Manejar peticiones DELETE - Eliminar usuario de DynamoDB"""
    user_id = path_parameters.get('id')
    
    logger.info(f"Procesando eliminación de usuario ID: {user_id}")
    
    # Validar ID en la URL
    if not user_id:
        return create_response(400, {
            "success": False,
            "message": "Se requiere el ID del usuario en la URL",
            "format": "/users/{id}"
        })
    
    try:
        user_id = int(user_id)
        
        # Verificar que el usuario existe antes de eliminar
        response = table.get_item(Key={'id': user_id})
        
        if 'Item' not in response:
            logger.warning(f"Usuario con ID {user_id} no encontrado")
            return create_response(404, {
                "success": False,
                "message": f"Usuario con ID {user_id} no existe"
            })
        
        user_to_delete = response['Item']
        
        # Eliminar de DynamoDB
        table.delete_item(Key={'id': user_id})
        
        logger.info(f"Usuario eliminado de DynamoDB: {user_to_delete}")
        
        return create_response(200, {
            "success": True,
            "message": f"Usuario '{user_to_delete['name']}' eliminado exitosamente",
            "deleted_user": {
                "id": user_to_delete['id'],
                "name": user_to_delete['name'],
                "email": user_to_delete['email']
            }
        })
        
    except ValueError:
        return create_response(400, {
            "success": False,
            "message": "El ID del usuario debe ser un número entero",
            "received": user_id
        })
    except ClientError as e:
        logger.error(f"Error DynamoDB: {e}")
        return create_response(500, {
            "success": False,
            "message": "Error eliminando de la base de datos",
            "error": str(e)
        })

def is_valid_email(email):
    """Validar formato básico de email"""
    return '@' in email and '.' in email and len(email) > 5