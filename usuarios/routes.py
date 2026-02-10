from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import get_db_connection, bcrypt

usuarios_bp = Blueprint('usuarios', __name__)


@usuarios_bp.route('', methods=['GET'])
@jwt_required()
def listar_usuarios():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT id, nombre, apellido, correo, activo, fecha_creacion FROM usuarios WHERE activo = TRUE")
    usuarios = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    for u in usuarios:
        if u.get('fecha_creacion'):
            u['fecha_creacion'] = u['fecha_creacion'].isoformat()
    
    return jsonify(usuarios), 200


@usuarios_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def obtener_usuario(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT id, nombre, apellido, correo, activo, fecha_creacion FROM usuarios WHERE id = %s", (id,))
    usuario = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    if not usuario:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    
    if usuario.get('fecha_creacion'):
        usuario['fecha_creacion'] = usuario['fecha_creacion'].isoformat()
    
    return jsonify(usuario), 200


@usuarios_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def actualizar_usuario(id):
    current_user_id = get_jwt_identity()
    
    if current_user_id != id:
        return jsonify({'error': 'No tienes permiso para actualizar este usuario'}), 403
    
    data = request.get_json()
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT id FROM usuarios WHERE id = %s", (id,))
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({'error': 'Usuario no encontrado'}), 404
    
    if 'correo' in data:
        cursor.execute("SELECT id FROM usuarios WHERE correo = %s AND id != %s", (data['correo'], id))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({'error': 'El correo ya esta en uso'}), 400
    
    updates = []
    values = []
    
    if 'nombre' in data:
        updates.append("nombre = %s")
        values.append(data['nombre'])
    if 'apellido' in data:
        updates.append("apellido = %s")
        values.append(data['apellido'])
    if 'correo' in data:
        updates.append("correo = %s")
        values.append(data['correo'])
    if 'contrasena' in data:
        updates.append("contrasena = %s")
        values.append(bcrypt.generate_password_hash(data['contrasena']).decode('utf-8'))
    
    if updates:
        values.append(id)
        cursor.execute(f"UPDATE usuarios SET {', '.join(updates)} WHERE id = %s", values)
        conn.commit()
    
    cursor.execute("SELECT id, nombre, apellido, correo, activo, fecha_creacion FROM usuarios WHERE id = %s", (id,))
    usuario = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    if usuario.get('fecha_creacion'):
        usuario['fecha_creacion'] = usuario['fecha_creacion'].isoformat()
    
    return jsonify({
        'message': 'Usuario actualizado',
        'usuario': usuario
    }), 200


@usuarios_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def desactivar_usuario(id):
    current_user_id = get_jwt_identity()
    
    if current_user_id != id:
        return jsonify({'error': 'No tienes permiso para desactivar este usuario'}), 403
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT id FROM usuarios WHERE id = %s", (id,))
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({'error': 'Usuario no encontrado'}), 404
    
    cursor.execute("UPDATE usuarios SET activo = FALSE WHERE id = %s", (id,))
    conn.commit()
    
    cursor.close()
    conn.close()
    
    return jsonify({'message': 'Usuario desactivado'}), 200
