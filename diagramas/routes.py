import json
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import get_db_connection

diagramas_bp = Blueprint('diagramas', __name__)

@diagramas_bp.route('/proyecto/<int:proyecto_id>', methods=['GET'])
@jwt_required()
def listar_por_proyecto(proyecto_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT d.id, d.proyecto_id, d.tipo, d.nombre, d.creado_por,
               u.nombre as creado_por_nombre, u.apellido as creado_por_apellido,
               d.fecha_creacion, d.fecha_actualizacion
        FROM diagramas d
        JOIN usuarios u ON d.creado_por = u.id
        WHERE d.proyecto_id = %s
        ORDER BY d.fecha_actualizacion DESC
    """, (proyecto_id,))

    diagramas = cursor.fetchall()
    for d in diagramas:
        if d.get('fecha_creacion'):
            d['fecha_creacion'] = d['fecha_creacion'].isoformat()
        if d.get('fecha_actualizacion'):
            d['fecha_actualizacion'] = d['fecha_actualizacion'].isoformat()

    cursor.close()
    conn.close()
    return jsonify(diagramas), 200

@diagramas_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def obtener(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT d.*, u.nombre as creado_por_nombre, u.apellido as creado_por_apellido
        FROM diagramas d
        JOIN usuarios u ON d.creado_por = u.id
        WHERE d.id = %s
    """, (id,))

    diagrama = cursor.fetchone()
    if not diagrama:
        cursor.close()
        conn.close()
        return jsonify({'error': 'Diagrama no encontrado'}), 404

    if diagrama.get('fecha_creacion'):
        diagrama['fecha_creacion'] = diagrama['fecha_creacion'].isoformat()
    if diagrama.get('fecha_actualizacion'):
        diagrama['fecha_actualizacion'] = diagrama['fecha_actualizacion'].isoformat()
    if diagrama.get('datos') and isinstance(diagrama['datos'], str):
        diagrama['datos'] = json.loads(diagrama['datos'])

    cursor.close()
    conn.close()
    return jsonify(diagrama), 200

@diagramas_bp.route('', methods=['POST'])
@jwt_required()
def crear():
    current_user_id = get_jwt_identity()
    data = request.get_json()

    if not data.get('proyecto_id'):
        return jsonify({'error': 'proyecto_id es requerido'}), 400
    if not data.get('nombre'):
        return jsonify({'error': 'nombre es requerido'}), 400
    if not data.get('tipo'):
        return jsonify({'error': 'tipo es requerido'}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    datos_json = json.dumps(data.get('datos', {'elements': [], 'connections': []}))

    cursor.execute("""
        INSERT INTO diagramas (proyecto_id, tipo, nombre, datos, creado_por)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        data['proyecto_id'],
        data['tipo'],
        data['nombre'],
        datos_json,
        current_user_id
    ))
    conn.commit()
    diagrama_id = cursor.lastrowid

    cursor.execute("SELECT * FROM diagramas WHERE id = %s", (diagrama_id,))
    diagrama = cursor.fetchone()
    if diagrama.get('fecha_creacion'):
        diagrama['fecha_creacion'] = diagrama['fecha_creacion'].isoformat()
    if diagrama.get('fecha_actualizacion'):
        diagrama['fecha_actualizacion'] = diagrama['fecha_actualizacion'].isoformat()
    if diagrama.get('datos') and isinstance(diagrama['datos'], str):
        diagrama['datos'] = json.loads(diagrama['datos'])

    cursor.close()
    conn.close()
    return jsonify({'message': 'Diagrama creado', 'diagrama': diagrama}), 201

@diagramas_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def actualizar(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT id FROM diagramas WHERE id = %s", (id,))
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({'error': 'Diagrama no encontrado'}), 404

    data = request.get_json()
    updates = []
    values = []

    if 'nombre' in data:
        updates.append("nombre = %s")
        values.append(data['nombre'])
    if 'datos' in data:
        updates.append("datos = %s")
        valores_datos = data['datos']
        values.append(json.dumps(valores_datos) if isinstance(valores_datos, dict) else valores_datos)

    if updates:
        values.append(id)
        cursor.execute(f"UPDATE diagramas SET {', '.join(updates)} WHERE id = %s", values)
        conn.commit()

    cursor.execute("SELECT * FROM diagramas WHERE id = %s", (id,))
    diagrama = cursor.fetchone()
    if diagrama.get('fecha_creacion'):
        diagrama['fecha_creacion'] = diagrama['fecha_creacion'].isoformat()
    if diagrama.get('fecha_actualizacion'):
        diagrama['fecha_actualizacion'] = diagrama['fecha_actualizacion'].isoformat()
    if diagrama.get('datos') and isinstance(diagrama['datos'], str):
        diagrama['datos'] = json.loads(diagrama['datos'])

    cursor.close()
    conn.close()
    return jsonify({'message': 'Diagrama actualizado', 'diagrama': diagrama}), 200

@diagramas_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def eliminar(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT id FROM diagramas WHERE id = %s", (id,))
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({'error': 'Diagrama no encontrado'}), 404

    cursor.execute("DELETE FROM diagramas WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'Diagrama eliminado'}), 200
