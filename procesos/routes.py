from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from extensions import get_db_connection

procesos_bp = Blueprint('procesos', __name__)


@procesos_bp.route('/proyecto/<int:proyecto_id>', methods=['GET'])
@jwt_required()
def listar_procesos(proyecto_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT p.*, u.nombre as responsable_nombre, u.apellido as responsable_apellido
        FROM procesos p
        LEFT JOIN usuarios u ON p.responsable_id = u.id
        WHERE p.proyecto_id = %s
    """, (proyecto_id,))
    
    procesos = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    result = []
    for p in procesos:
        result.append({
            'id': p['id'],
            'proyecto_id': p['proyecto_id'],
            'nombre': p['nombre'],
            'descripcion': p['descripcion'],
            'objetivo': p['objetivo'],
            'responsable_id': p['responsable_id'],
            'estado': p['estado'],
            'fecha_creacion': p['fecha_creacion'].isoformat() if p.get('fecha_creacion') else None,
            'fecha_actualizacion': p['fecha_actualizacion'].isoformat() if p.get('fecha_actualizacion') else None,
            'responsable': {
                'id': p['responsable_id'],
                'nombre': p['responsable_nombre'],
                'apellido': p['responsable_apellido']
            } if p.get('responsable_id') else None
        })
    
    return jsonify(result), 200


@procesos_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def obtener_proceso(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT p.*, u.nombre as responsable_nombre, u.apellido as responsable_apellido
        FROM procesos p
        LEFT JOIN usuarios u ON p.responsable_id = u.id
        WHERE p.id = %s
    """, (id,))
    
    p = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    if not p:
        return jsonify({'error': 'Proceso no encontrado'}), 404
    
    proceso = {
        'id': p['id'],
        'proyecto_id': p['proyecto_id'],
        'nombre': p['nombre'],
        'descripcion': p['descripcion'],
        'objetivo': p['objetivo'],
        'responsable_id': p['responsable_id'],
        'estado': p['estado'],
        'fecha_creacion': p['fecha_creacion'].isoformat() if p.get('fecha_creacion') else None,
        'fecha_actualizacion': p['fecha_actualizacion'].isoformat() if p.get('fecha_actualizacion') else None,
        'responsable': {
            'id': p['responsable_id'],
            'nombre': p['responsable_nombre'],
            'apellido': p['responsable_apellido']
        } if p.get('responsable_id') else None
    }
    
    return jsonify(proceso), 200


@procesos_bp.route('', methods=['POST'])
@jwt_required()
def crear_proceso():
    data = request.get_json()
    
    if not data.get('proyecto_id'):
        return jsonify({'error': 'El proyecto_id es requerido'}), 400
    
    if not data.get('nombre'):
        return jsonify({'error': 'El nombre es requerido'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        INSERT INTO procesos (proyecto_id, nombre, descripcion, objetivo, responsable_id, estado)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        data['proyecto_id'],
        data['nombre'],
        data.get('descripcion'),
        data.get('objetivo'),
        data.get('responsable_id'),
        data.get('estado', 'definido')
    ))
    conn.commit()
    
    proceso_id = cursor.lastrowid
    
    cursor.execute("""
        SELECT p.*, u.nombre as responsable_nombre, u.apellido as responsable_apellido
        FROM procesos p
        LEFT JOIN usuarios u ON p.responsable_id = u.id
        WHERE p.id = %s
    """, (proceso_id,))
    
    p = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    proceso = {
        'id': p['id'],
        'proyecto_id': p['proyecto_id'],
        'nombre': p['nombre'],
        'descripcion': p['descripcion'],
        'objetivo': p['objetivo'],
        'responsable_id': p['responsable_id'],
        'estado': p['estado'],
        'fecha_creacion': p['fecha_creacion'].isoformat() if p.get('fecha_creacion') else None,
        'fecha_actualizacion': p['fecha_actualizacion'].isoformat() if p.get('fecha_actualizacion') else None,
        'responsable': {
            'id': p['responsable_id'],
            'nombre': p['responsable_nombre'],
            'apellido': p['responsable_apellido']
        } if p.get('responsable_id') else None
    }
    
    return jsonify({
        'message': 'Proceso creado',
        'proceso': proceso
    }), 201


@procesos_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def actualizar_proceso(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT id FROM procesos WHERE id = %s", (id,))
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({'error': 'Proceso no encontrado'}), 404
    
    data = request.get_json()
    
    updates = []
    values = []
    
    campos = ['nombre', 'descripcion', 'objetivo', 'responsable_id', 'estado']
    
    for campo in campos:
        if campo in data:
            updates.append(f"{campo} = %s")
            values.append(data[campo])
    
    if updates:
        values.append(id)
        cursor.execute(f"UPDATE procesos SET {', '.join(updates)} WHERE id = %s", values)
        conn.commit()
    
    cursor.execute("""
        SELECT p.*, u.nombre as responsable_nombre, u.apellido as responsable_apellido
        FROM procesos p
        LEFT JOIN usuarios u ON p.responsable_id = u.id
        WHERE p.id = %s
    """, (id,))
    
    p = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    proceso = {
        'id': p['id'],
        'proyecto_id': p['proyecto_id'],
        'nombre': p['nombre'],
        'descripcion': p['descripcion'],
        'objetivo': p['objetivo'],
        'responsable_id': p['responsable_id'],
        'estado': p['estado'],
        'fecha_creacion': p['fecha_creacion'].isoformat() if p.get('fecha_creacion') else None,
        'fecha_actualizacion': p['fecha_actualizacion'].isoformat() if p.get('fecha_actualizacion') else None,
        'responsable': {
            'id': p['responsable_id'],
            'nombre': p['responsable_nombre'],
            'apellido': p['responsable_apellido']
        } if p.get('responsable_id') else None
    }
    
    return jsonify({
        'message': 'Proceso actualizado',
        'proceso': proceso
    }), 200


@procesos_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def eliminar_proceso(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT id FROM procesos WHERE id = %s", (id,))
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({'error': 'Proceso no encontrado'}), 404
    
    cursor.execute("DELETE FROM procesos WHERE id = %s", (id,))
    conn.commit()
    
    cursor.close()
    conn.close()
    
    return jsonify({'message': 'Proceso eliminado'}), 200
