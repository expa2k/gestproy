from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from extensions import get_db_connection

roles_bp = Blueprint('roles', __name__)


@roles_bp.route('', methods=['GET'])
@jwt_required()
def listar_roles():
    proyecto_id = request.args.get('proyecto_id', type=int)
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if proyecto_id:
        cursor.execute("""
            SELECT * FROM roles WHERE es_fijo = TRUE OR proyecto_id = %s
        """, (proyecto_id,))
    else:
        cursor.execute("SELECT * FROM roles WHERE es_fijo = TRUE")
    
    roles = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    for r in roles:
        if r.get('fecha_creacion'):
            r['fecha_creacion'] = r['fecha_creacion'].isoformat()
    
    return jsonify(roles), 200


@roles_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def obtener_rol(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM roles WHERE id = %s", (id,))
    rol = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    if not rol:
        return jsonify({'error': 'Rol no encontrado'}), 404
    
    if rol.get('fecha_creacion'):
        rol['fecha_creacion'] = rol['fecha_creacion'].isoformat()
    
    return jsonify(rol), 200


@roles_bp.route('', methods=['POST'])
@jwt_required()
def crear_rol():
    data = request.get_json()
    
    if not data.get('nombre'):
        return jsonify({'error': 'El nombre es requerido'}), 400
    
    if not data.get('proyecto_id'):
        return jsonify({'error': 'El proyecto_id es requerido'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        INSERT INTO roles (proyecto_id, nombre, descripcion, es_fijo)
        VALUES (%s, %s, %s, FALSE)
    """, (data['proyecto_id'], data['nombre'], data.get('descripcion')))
    conn.commit()
    
    rol_id = cursor.lastrowid
    
    cursor.execute("SELECT * FROM roles WHERE id = %s", (rol_id,))
    rol = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    if rol.get('fecha_creacion'):
        rol['fecha_creacion'] = rol['fecha_creacion'].isoformat()
    
    return jsonify({
        'message': 'Rol creado',
        'rol': rol
    }), 201


@roles_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def actualizar_rol(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM roles WHERE id = %s", (id,))
    rol = cursor.fetchone()
    
    if not rol:
        cursor.close()
        conn.close()
        return jsonify({'error': 'Rol no encontrado'}), 404
    
    if rol['es_fijo']:
        cursor.close()
        conn.close()
        return jsonify({'error': 'No se pueden modificar roles fijos'}), 403
    
    data = request.get_json()
    
    updates = []
    values = []
    
    if 'nombre' in data:
        updates.append("nombre = %s")
        values.append(data['nombre'])
    if 'descripcion' in data:
        updates.append("descripcion = %s")
        values.append(data['descripcion'])
    
    if updates:
        values.append(id)
        cursor.execute(f"UPDATE roles SET {', '.join(updates)} WHERE id = %s", values)
        conn.commit()
    
    cursor.execute("SELECT * FROM roles WHERE id = %s", (id,))
    rol = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    if rol.get('fecha_creacion'):
        rol['fecha_creacion'] = rol['fecha_creacion'].isoformat()
    
    return jsonify({
        'message': 'Rol actualizado',
        'rol': rol
    }), 200


@roles_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def eliminar_rol(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM roles WHERE id = %s", (id,))
    rol = cursor.fetchone()
    
    if not rol:
        cursor.close()
        conn.close()
        return jsonify({'error': 'Rol no encontrado'}), 404
    
    if rol['es_fijo']:
        cursor.close()
        conn.close()
        return jsonify({'error': 'No se pueden eliminar roles fijos'}), 403
    
    cursor.execute("DELETE FROM roles WHERE id = %s", (id,))
    conn.commit()
    
    cursor.close()
    conn.close()
    
    return jsonify({'message': 'Rol eliminado'}), 200
