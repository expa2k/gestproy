import json
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import get_db_connection

ejecuciones_bp = Blueprint('ejecuciones', __name__)

@ejecuciones_bp.route('/tecnica/<int:subproceso_tecnica_id>', methods=['GET'])
@jwt_required()
def listar_por_tecnica(subproceso_tecnica_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT e.*, u.nombre as creado_por_nombre, u.apellido as creado_por_apellido
        FROM ejecuciones_tecnica e
        JOIN usuarios u ON e.creado_por = u.id
        WHERE e.subproceso_tecnica_id = %s
        ORDER BY e.fecha_creacion DESC
    """, (subproceso_tecnica_id,))

    ejecuciones = cursor.fetchall()

    for e in ejecuciones:
        if e.get('fecha_ejecucion'):
            e['fecha_ejecucion'] = e['fecha_ejecucion'].isoformat()
        if e.get('fecha_creacion'):
            e['fecha_creacion'] = e['fecha_creacion'].isoformat()
        if e.get('fecha_actualizacion'):
            e['fecha_actualizacion'] = e['fecha_actualizacion'].isoformat()
        if e.get('datos') and isinstance(e['datos'], str):
            e['datos'] = json.loads(e['datos'])

    cursor.close()
    conn.close()

    return jsonify(ejecuciones), 200

@ejecuciones_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def obtener(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT e.*, u.nombre as creado_por_nombre, u.apellido as creado_por_apellido
        FROM ejecuciones_tecnica e
        JOIN usuarios u ON e.creado_por = u.id
        WHERE e.id = %s
    """, (id,))

    ejecucion = cursor.fetchone()

    if not ejecucion:
        cursor.close()
        conn.close()
        return jsonify({'error': 'Ejecucion no encontrada'}), 404

    if ejecucion.get('fecha_ejecucion'):
        ejecucion['fecha_ejecucion'] = ejecucion['fecha_ejecucion'].isoformat()
    if ejecucion.get('fecha_creacion'):
        ejecucion['fecha_creacion'] = ejecucion['fecha_creacion'].isoformat()
    if ejecucion.get('fecha_actualizacion'):
        ejecucion['fecha_actualizacion'] = ejecucion['fecha_actualizacion'].isoformat()
    if ejecucion.get('datos') and isinstance(ejecucion['datos'], str):
        ejecucion['datos'] = json.loads(ejecucion['datos'])

    cursor.close()
    conn.close()

    return jsonify(ejecucion), 200

@ejecuciones_bp.route('', methods=['POST'])
@jwt_required()
def crear():
    current_user_id = get_jwt_identity()
    data = request.get_json()

    required = ['subproceso_tecnica_id', 'datos']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'El campo {field} es requerido'}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    datos_value = json.dumps(data['datos']) if isinstance(data['datos'], dict) else data['datos']

    cursor.execute("""
        INSERT INTO ejecuciones_tecnica (subproceso_tecnica_id, datos, participantes, fecha_ejecucion, estado, notas, creado_por)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        data['subproceso_tecnica_id'],
        datos_value,
        data.get('participantes'),
        data.get('fecha_ejecucion'),
        data.get('estado', 'planificada'),
        data.get('notas'),
        current_user_id
    ))
    conn.commit()
    ejecucion_id = cursor.lastrowid

    cursor.execute("SELECT * FROM ejecuciones_tecnica WHERE id = %s", (ejecucion_id,))
    ejecucion = cursor.fetchone()
    
    if ejecucion.get('fecha_ejecucion'):
        ejecucion['fecha_ejecucion'] = ejecucion['fecha_ejecucion'].isoformat()
    if ejecucion.get('fecha_creacion'):
        ejecucion['fecha_creacion'] = ejecucion['fecha_creacion'].isoformat()
    if ejecucion.get('fecha_actualizacion'):
        ejecucion['fecha_actualizacion'] = ejecucion['fecha_actualizacion'].isoformat()
    if ejecucion.get('datos') and isinstance(ejecucion['datos'], str):
        ejecucion['datos'] = json.loads(ejecucion['datos'])

    cursor.close()
    conn.close()

    return jsonify({
        'message': 'Ejecucion registrada',
        'ejecucion': ejecucion
    }), 201

@ejecuciones_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def actualizar(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT id FROM ejecuciones_tecnica WHERE id = %s", (id,))
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({'error': 'Ejecucion no encontrada'}), 404

    data = request.get_json()

    updates = []
    values = []

    campos_texto = ['participantes', 'fecha_ejecucion', 'estado', 'notas']
    for campo in campos_texto:
        if campo in data:
            updates.append(f"{campo} = %s")
            values.append(data[campo])

    if 'datos' in data:
        updates.append("datos = %s")
        meta = data['datos']
        values.append(json.dumps(meta) if isinstance(meta, dict) else meta)

    if updates:
        values.append(id)
        cursor.execute(f"UPDATE ejecuciones_tecnica SET {', '.join(updates)} WHERE id = %s", values)
        conn.commit()

    cursor.execute("SELECT * FROM ejecuciones_tecnica WHERE id = %s", (id,))
    ejecucion = cursor.fetchone()
    
    if ejecucion.get('fecha_ejecucion'):
        ejecucion['fecha_ejecucion'] = ejecucion['fecha_ejecucion'].isoformat()
    if ejecucion.get('fecha_creacion'):
        ejecucion['fecha_creacion'] = ejecucion['fecha_creacion'].isoformat()
    if ejecucion.get('fecha_actualizacion'):
        ejecucion['fecha_actualizacion'] = ejecucion['fecha_actualizacion'].isoformat()
    if ejecucion.get('datos') and isinstance(ejecucion['datos'], str):
        ejecucion['datos'] = json.loads(ejecucion['datos'])

    cursor.close()
    conn.close()

    return jsonify({
        'message': 'Ejecucion actualizada',
        'ejecucion': ejecucion
    }), 200

@ejecuciones_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def eliminar(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT id FROM ejecuciones_tecnica WHERE id = %s", (id,))
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({'error': 'Ejecucion no encontrada'}), 404

    cursor.execute("DELETE FROM ejecuciones_tecnica WHERE id = %s", (id,))
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({'message': 'Ejecucion eliminada'}), 200
