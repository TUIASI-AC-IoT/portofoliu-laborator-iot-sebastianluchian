from flask import Flask, request, jsonify, abort
import os
from flasgger import Swagger

app = Flask(__name__)
swagger = Swagger(app)

FILES_DIR = './files'
os.makedirs(FILES_DIR, exist_ok=True)

def safe_path(path):
    full_path = os.path.abspath(os.path.join(FILES_DIR, path))
    if not full_path.startswith(os.path.abspath(FILES_DIR)):
        abort(400, 'Invalid path')
    return full_path

def list_files_recursively():
    files_list = []
    for root, dirs, files in os.walk(FILES_DIR):
        for f in files:
            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(full_path, FILES_DIR)
            files_list.append(rel_path.replace("\\", "/"))
    return files_list

def generate_filename():
    existing = list_files_recursively()
    i = 1
    while True:
        name = f"file{i}.txt"
        if name not in existing:
            return name
        i += 1

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
    return jsonify(list_files_recursively())

@app.route('/files', methods=['POST'])
def create_file_auto():
    """
    crearea unui fisier specificat prin continut
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
    filename = generate_filename()
    full_path = safe_path(filename)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(content)
    return jsonify({'filename': filename, 'message': 'File created'}), 201

@app.route('/files/<path:filename>', methods=['GET'])
def get_file(filename):
    """
    listarea continutului unui fisier specificat prin nume
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
    full_path = safe_path(filename)
    if not os.path.isfile(full_path):
        abort(404, 'File not found')
    with open(full_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return jsonify({'filename': filename, 'content': content})

@app.route('/files/<path:filename>', methods=['PUT'])
def update_file(filename):
    """
    Creare sau actualizarea fisier specificat prin nume
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
    full_path = safe_path(filename)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(content)
    return jsonify({'message': 'File created/updated'})

@app.route('/files/<path:filename>', methods=['DELETE'])
def delete_file(filename):
    """
    stergerea fisierului specificat prin nume
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
    full_path = safe_path(filename)
    if not os.path.isfile(full_path):
        abort(404, 'File not found')
    os.remove(full_path)
    return jsonify({'message': 'File deleted'})

if __name__ == '__main__':
    app.run(debug=True)
