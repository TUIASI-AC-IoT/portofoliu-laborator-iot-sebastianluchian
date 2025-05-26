from flask import Flask, request, jsonify, redirect, url_for
from flask_jwt_extended import (
    JWTManager, create_access_token, get_jwt_identity,
    jwt_required, get_jwt
)
from flasgger import Swagger, swag_from
from datetime import timedelta

app = Flask(__name__)

template = {
    "swagger": "2.0",
    "info": {
        "title": "Senzor API",
        "description": "API cu autentificare și autorizare pe roluri (JWT)",
        "version": "1.0"
    },
    "basePath": "/",
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT Authorization header using the Bearer scheme. Example: \"Authorization: Bearer {token}\""
        }
    },
}
swagger = Swagger(app)

app.config['JWT_SECRET_KEY'] = 'super-secret-key'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

jwt = JWTManager(app)

users = {
    "user1": {"passwd": "parola1", "role": "admin"},
    "user2": {"passwd": "parola2", "role": "owner"},
    "user3": {"passwd": "parolaX", "role": "owner"},
}

valid_tokens = set()

@app.route('/auth', methods=['POST'])
@swag_from({
    'tags': ['Autentificare'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'username': {'type': 'string'},
                    'password': {'type': 'string'}
                },
                'required': ['username', 'password']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Autentificare reușită',
            'examples': {'application/json': {'access_token': 'JWT'}}
        },
        401: {
            'description': 'Autentificare eșuată'
        }
    }
})
def login():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"msg": "Missing username or password"}), 400

    username = data['username']
    password = data['password']
    user = users.get(username)

    if not user or user['passwd'] != password:
        return jsonify({"msg": "Bad username or password"}), 401

    access_token = create_access_token(identity=username, additional_claims={"role": user["role"]})
    valid_tokens.add(access_token)
    return jsonify(access_token=access_token), 200

@app.route('/auth/jwtStore', methods=['GET'])
@jwt_required()
@swag_from({
    'tags': ['Token'],
    'security': [{'Bearer': []}],
    'responses': {
        200: {'description': 'Token valid, rol returnat'},
        404: {'description': 'Token invalid sau expirat'}
    }
})
def check_token():
    token = _extract_token_from_header()
    if token not in valid_tokens:
        return jsonify({"msg": "Token not found"}), 404
    claims = get_jwt()
    return jsonify(role=claims.get("role")), 200

@app.route('/auth/jwtStore', methods=['DELETE'])
@jwt_required()
@swag_from({
    'tags': ['Token'],
    'security': [{'Bearer': []}],
    'responses': {
        200: {'description': 'Delogare reușită'},
        404: {'description': 'Token inexistent sau deja invalidat'}
    }
})
def logout():
    token = _extract_token_from_header()
    if token not in valid_tokens:
        return jsonify({"msg": "Token not found"}), 404
    valid_tokens.remove(token)
    return jsonify({"msg": "Logged out"}), 200

def _extract_token_from_header():
    auth_header = request.headers.get('Authorization', None)
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header.split(" ")[1]
    return None

def role_required(*allowed_roles):
    def wrapper(fn):
        @jwt_required(optional=True)
        def decorator(*args, **kwargs):
            token = _extract_token_from_header()
            if not token or token not in valid_tokens:
                return redirect(url_for('login_page'))
            claims = get_jwt()
            role = claims.get('role', 'guest')
            if role not in allowed_roles:
                return redirect(url_for('login_page'))
            return fn(*args, **kwargs)
        decorator.__name__ = fn.__name__
        return decorator
    return wrapper

@app.route('/sensor/data', methods=['GET'])
@role_required('owner', 'admin')
@swag_from({
    'tags': ['Sensor'],
    'security': [{'Bearer': []}],
    'responses': {
        200: {
            'description': 'Date senzor',
            'examples': {'application/json': {"temperature": 23.5, "humidity": 60}}
        },
        401: {'description': 'Neautorizat'}
    }
})
def read_sensor():
    return jsonify({"temperature": 23.5, "humidity": 60}), 200

@app.route('/sensor/config', methods=['POST', 'PUT'])
@role_required('admin')
@swag_from({
    'tags': ['Sensor'],
    'security': [{'Bearer': []}],
    'responses': {
        200: {'description': 'Configurare actualizată'},
        401: {'description': 'Acces interzis pentru rolul curent'}
    }
})
def update_sensor_config():
    return jsonify({"msg": "Config updated"}), 200

@app.route('/auth', methods=['GET'])
def login_page():
    return jsonify({"msg": "Autentificare necesară"}), 401

@app.before_request
def check_auth_header():
    allowed_paths = [
        '/auth',
        '/auth/',
        '/apidocs',
        '/apidocs/',
        '/apidocs/static',
        '/flasgger_static',
        '/apispec_1.json',  # 👈 ADD THIS LINE
    ]
    if any(request.path.startswith(p) for p in allowed_paths):
        return
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith("Bearer "):
        return redirect(url_for('login_page'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
