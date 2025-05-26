from flask import Flask, request, jsonify, abort
import os
import random
from flasgger import Swagger

app = Flask(__name__)
swagger = Swagger(app)

FILES_DIR = './files'
os.makedirs(FILES_DIR, exist_ok=True)

SENSOR_CONFIG_DIR = './sensor_configs'
os.makedirs(SENSOR_CONFIG_DIR, exist_ok=True)

# --- Funcții utile ---
def safe_path(base_dir, path):
    full_path = os.path.abspath(os.path.join(base_dir, path))
    if not full_path.startswith(os.path.abspath(base_dir)):
        abort(400, 'Invalid path')
    return full_path

def list_files_recursively(base_dir):
    files_list = []
    for root, dirs, files in os.walk(base_dir):
        for f in files:
            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(full_path, base_dir)
            files_list.append(rel_path.replace("\\", "/"))
    return files_list

def generate_filename(base_dir):
    existing = list_files_recursively(base_dir)
    i = 1
    while True:
        name = f"file{i}.txt"
        if name not in existing:
            return name
        i += 1

def simulate_sensor_value(sensor_id):
    # Simulare simplă, randomizat
    return round(random.uniform(10.0, 100.0), 2)

# --- Rute pentru gestionare fisiere (fără schimbări) ---
@app.route('/files', methods=['GET'])
def list_files():
    """
    Listare fisiere
    ---
    responses:
      200:
        description: Listare fisiere
        schema:
          type: array
          items:
            type: string
    """
    return jsonify(list_files_recursively(FILES_DIR))

@app.route('/files', methods=['POST'])
def create_file_auto():
    """
    Creare fisier cu continut
    ---
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            content:
              type: string
              example: "Laborator 11 IOT"
    responses:
      201:
        description: File created
        schema:
          type: object
          properties:
            filename:
              type: string
            message:
              type: string
    """
    data = request.get_json()
    content = data.get('content') if data else None
    if content is None:
        abort(400, 'Content missing')
    filename = generate_filename(FILES_DIR)
    full_path = safe_path(FILES_DIR, filename)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(content)
    return jsonify({'filename': filename, 'message': 'File created'}), 201

@app.route('/files/<path:filename>', methods=['GET'])
def get_file(filename):
    """
    Listare continut fisier
    ---
    parameters:
      - in: path
        name: filename
        type: string
        required: true
        description: The path of the file
    responses:
      200:
        description: File content
        schema:
          type: object
          properties:
            filename:
              type: string
            content:
              type: string
      404:
        description: File not found
    """
    full_path = safe_path(FILES_DIR, filename)
    if not os.path.isfile(full_path):
        abort(404, 'File not found')
    with open(full_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return jsonify({'filename': filename, 'content': content})

@app.route('/files/<path:filename>', methods=['PUT'])
def update_file(filename):
    """
    Creare/actualizare fisier specificat
    ---
    parameters:
      - in: path
        name: filename
        type: string
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            content:
              type: string
              example: "New content"
    responses:
      200:
        description: File updated
    """
    data = request.get_json()
    content = data.get('content') if data else None
    if content is None:
        abort(400, 'Content missing')
    full_path = safe_path(FILES_DIR, filename)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(content)
    return jsonify({'message': 'File created/updated'})

@app.route('/files/<path:filename>', methods=['DELETE'])
def delete_file(filename):
    """
    Stergere fisier specificat
    ---
    parameters:
      - in: path
        name: filename
        type: string
        required: true
    responses:
      200:
        description: File deleted
      404:
        description: File not found
    """
    full_path = safe_path(FILES_DIR, filename)
    if not os.path.isfile(full_path):
        abort(404, 'File not found')
    os.remove(full_path)
    return jsonify({'message': 'File deleted'})

# --- Rute pentru senzori ---

@app.route('/sensors/<string:sensor_id>', methods=['GET'])
def get_sensor_value(sensor_id):
    """
    Citire valoare senzor simulata
    ---
    parameters:
      - name: sensor_id
        in: path
        type: string
        required: true
        description: ID-ul senzorului
    responses:
      200:
        description: Valoarea senzorului
        schema:
          type: object
          properties:
            sensor_id:
              type: string
            value:
              type: number
    """
    value = simulate_sensor_value(sensor_id)
    return jsonify({'sensor_id': sensor_id, 'value': value})

@app.route('/sensors/<string:sensor_id>', methods=['POST'])
def create_sensor_config(sensor_id):
    """
    Creare fisier configurare senzor (dacă nu există)
    ---
    parameters:
      - name: sensor_id
        in: path
        type: string
        required: true
    responses:
      201:
        description: Config file creat
      409:
        description: Config file deja existent
        schema:
          type: object
          properties:
            error:
              type: string
    """
    sensor_dir = safe_path(SENSOR_CONFIG_DIR, sensor_id)
    os.makedirs(sensor_dir, exist_ok=True)
    config_path = os.path.join(sensor_dir, 'config.txt')

    if os.path.exists(config_path):
        return jsonify({'error': f'Config file for sensor {sensor_id} already exists.'}), 409

    with open(config_path, 'w', encoding='utf-8') as f:
        f.write('scale=1.0\n')

    return jsonify({'message': f'Config file created for sensor {sensor_id}', 'filename': 'config.txt'}), 201

@app.route('/sensors/<string:sensor_id>/<string:config_file>', methods=['PUT'])
def update_sensor_config(sensor_id, config_file):
    """
    Inlocuire fisier configurare senzor (daca exista)
    ---
    parameters:
      - name: sensor_id
        in: path
        type: string
        required: true
      - name: config_file
        in: path
        type: string
        required: true
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            content:
              type: string
              example: "scale=2.5"
    responses:
      200:
        description: Config file updated
      404:
        description: Config file nu există
        schema:
          type: object
          properties:
            error:
              type: string
    """
    data = request.get_json()
    content = data.get('content') if data else None
    if content is None:
        abort(400, 'Content missing')

    config_path = safe_path(SENSOR_CONFIG_DIR, os.path.join(sensor_id, config_file))
    if not os.path.exists(config_path):
        return jsonify({'error': f'Config file {config_file} does not exist for sensor {sensor_id}.'}), 404

    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(content)

    return jsonify({'message': f'Config file {config_file} updated for sensor {sensor_id}.'})

if __name__ == '__main__':
    app.run(debug=True)
