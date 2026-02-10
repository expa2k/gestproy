from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from extensions import get_db_connection

subprocesos_bp = Blueprint('subprocesos', __name__)


@subprocesos_bp.route('/proceso/<int:proceso_id>', methods=['GET'])
@jwt_required()
def listar_subprocesos(proceso_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT s.*, u.nombre as responsable_nombre, u.apellido as responsable_apellido
        FROM subprocesos s
        LEFT JOIN usuarios u ON s.responsable_id = u.id
        WHERE s.proceso_id = %s
    """, (proceso_id,))
    
    subprocesos = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    result = []
    for s in subprocesos:
        result.append({
            'id': s['id'],
            'proceso_id': s['proceso_id'],
            'nombre': s['nombre'],
            'descripcion': s['descripcion'],
            'responsable_id': s['responsable_id'],
            'estado': s['estado'],
            'horas_estimadas': float(s['horas_estimadas']) if s.get('horas_estimadas') else None,
            'fecha_creacion': s['fecha_creacion'].isoformat() if s.get('fecha_creacion') else None,
            'fecha_actualizacion': s['fecha_actualizacion'].isoformat() if s.get('fecha_actualizacion') else None,
            'responsable': {
                'id': s['responsable_id'],
                'nombre': s['responsable_nombre'],
                'apellido': s['responsable_apellido']
            } if s.get('responsable_id') else None
        })
    
    return jsonify(result), 200


@subprocesos_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def obtener_subproceso(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT s.*, u.nombre as responsable_nombre, u.apellido as responsable_apellido
        FROM subprocesos s
        LEFT JOIN usuarios u ON s.responsable_id = u.id
        WHERE s.id = %s
    """, (id,))
    
    s = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    if not s:
        return jsonify({'error': 'Subproceso no encontrado'}), 404
    
    subproceso = {
        'id': s['id'],
        'proceso_id': s['proceso_id'],
        'nombre': s['nombre'],
        'descripcion': s['descripcion'],
        'responsable_id': s['responsable_id'],
        'estado': s['estado'],
        'horas_estimadas': float(s['horas_estimadas']) if s.get('horas_estimadas') else None,
        'fecha_creacion': s['fecha_creacion'].isoformat() if s.get('fecha_creacion') else None,
        'fecha_actualizacion': s['fecha_actualizacion'].isoformat() if s.get('fecha_actualizacion') else None,
        'responsable': {
            'id': s['responsable_id'],
            'nombre': s['responsable_nombre'],
            'apellido': s['responsable_apellido']
        } if s.get('responsable_id') else None
    }
    
    return jsonify(subproceso), 200


@subprocesos_bp.route('', methods=['POST'])
@jwt_required()
def crear_subproceso():
    data = request.get_json()
    
    if not data.get('proceso_id'):
        return jsonify({'error': 'El proceso_id es requerido'}), 400
    
    if not data.get('nombre'):
        return jsonify({'error': 'El nombre es requerido'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        INSERT INTO subprocesos (proceso_id, nombre, descripcion, responsable_id, estado, horas_estimadas)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        data['proceso_id'],
        data['nombre'],
        data.get('descripcion'),
        data.get('responsable_id'),
        data.get('estado', 'definido'),
        data.get('horas_estimadas')
    ))
    conn.commit()
    
    subproceso_id = cursor.lastrowid
    
    cursor.execute("""
        SELECT s.*, u.nombre as responsable_nombre, u.apellido as responsable_apellido
        FROM subprocesos s
        LEFT JOIN usuarios u ON s.responsable_id = u.id
        WHERE s.id = %s
    """, (subproceso_id,))
    
    s = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    subproceso = {
        'id': s['id'],
        'proceso_id': s['proceso_id'],
        'nombre': s['nombre'],
        'descripcion': s['descripcion'],
        'responsable_id': s['responsable_id'],
        'estado': s['estado'],
        'horas_estimadas': float(s['horas_estimadas']) if s.get('horas_estimadas') else None,
        'fecha_creacion': s['fecha_creacion'].isoformat() if s.get('fecha_creacion') else None,
        'fecha_actualizacion': s['fecha_actualizacion'].isoformat() if s.get('fecha_actualizacion') else None,
        'responsable': {
            'id': s['responsable_id'],
            'nombre': s['responsable_nombre'],
            'apellido': s['responsable_apellido']
        } if s.get('responsable_id') else None
    }
    
    return jsonify({
        'message': 'Subproceso creado',
        'subproceso': subproceso
    }), 201


@subprocesos_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def actualizar_subproceso(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT id FROM subprocesos WHERE id = %s", (id,))
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({'error': 'Subproceso no encontrado'}), 404
    
    data = request.get_json()
    
    updates = []
    values = []
    
    campos = ['nombre', 'descripcion', 'responsable_id', 'estado', 'horas_estimadas']
    
    for campo in campos:
        if campo in data:
            updates.append(f"{campo} = %s")
            values.append(data[campo])
    
    if updates:
        values.append(id)
        cursor.execute(f"UPDATE subprocesos SET {', '.join(updates)} WHERE id = %s", values)
        conn.commit()
    
    cursor.execute("""
        SELECT s.*, u.nombre as responsable_nombre, u.apellido as responsable_apellido
        FROM subprocesos s
        LEFT JOIN usuarios u ON s.responsable_id = u.id
        WHERE s.id = %s
    """, (id,))
    
    s = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    subproceso = {
        'id': s['id'],
        'proceso_id': s['proceso_id'],
        'nombre': s['nombre'],
        'descripcion': s['descripcion'],
        'responsable_id': s['responsable_id'],
        'estado': s['estado'],
        'horas_estimadas': float(s['horas_estimadas']) if s.get('horas_estimadas') else None,
        'fecha_creacion': s['fecha_creacion'].isoformat() if s.get('fecha_creacion') else None,
        'fecha_actualizacion': s['fecha_actualizacion'].isoformat() if s.get('fecha_actualizacion') else None,
        'responsable': {
            'id': s['responsable_id'],
            'nombre': s['responsable_nombre'],
            'apellido': s['responsable_apellido']
        } if s.get('responsable_id') else None
    }
    
    return jsonify({
        'message': 'Subproceso actualizado',
        'subproceso': subproceso
    }), 200


@subprocesos_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def eliminar_subproceso(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT id FROM subprocesos WHERE id = %s", (id,))
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({'error': 'Subproceso no encontrado'}), 404
    
    cursor.execute("DELETE FROM subprocesos WHERE id = %s", (id,))
    conn.commit()
    
    cursor.close()
    conn.close()
    
    return jsonify({'message': 'Subproceso eliminado'}), 200
