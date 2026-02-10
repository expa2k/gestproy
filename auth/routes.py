from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from extensions import get_db_connection, bcrypt

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    required = ['nombre', 'apellido', 'correo', 'contrasena']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'El campo {field} es requerido'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT id FROM usuarios WHERE correo = %s", (data['correo'],))
    if cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({'error': 'El correo ya esta registrado'}), 400
    
    hashed_password = bcrypt.generate_password_hash(data['contrasena']).decode('utf-8')
    
    cursor.execute(
        "INSERT INTO usuarios (nombre, apellido, correo, contrasena) VALUES (%s, %s, %s, %s)",
        (data['nombre'], data['apellido'], data['correo'], hashed_password)
    )
    conn.commit()
    
    user_id = cursor.lastrowid
    
    cursor.execute("SELECT id, nombre, apellido, correo, activo, fecha_creacion FROM usuarios WHERE id = %s", (user_id,))
    usuario = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    if usuario and usuario.get('fecha_creacion'):
        usuario['fecha_creacion'] = usuario['fecha_creacion'].isoformat()
    
    access_token = create_access_token(identity=str(user_id))
    refresh_token = create_refresh_token(identity=str(user_id))
    
    return jsonify({
        'message': 'Usuario registrado exitosamente',
        'usuario': usuario,
        'access_token': access_token,
        'refresh_token': refresh_token
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data.get('correo') or not data.get('contrasena'):
        return jsonify({'error': 'Correo y contrasena son requeridos'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM usuarios WHERE correo = %s", (data['correo'],))
    usuario = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    if not usuario or not bcrypt.check_password_hash(usuario['contrasena'], data['contrasena']):
        return jsonify({'error': 'Credenciales invalidas'}), 401
    
    if not usuario['activo']:
        return jsonify({'error': 'Usuario desactivado'}), 401
    
    access_token = create_access_token(identity=str(usuario['id']))
    refresh_token = create_refresh_token(identity=str(usuario['id']))
    
    del usuario['contrasena']
    if usuario.get('fecha_creacion'):
        usuario['fecha_creacion'] = usuario['fecha_creacion'].isoformat()
    if usuario.get('fecha_actualizacion'):
        usuario['fecha_actualizacion'] = usuario['fecha_actualizacion'].isoformat()
    
    return jsonify({
        'message': 'Login exitoso',
        'usuario': usuario,
        'access_token': access_token,
        'refresh_token': refresh_token
    }), 200


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user_id = get_jwt_identity()
    access_token = create_access_token(identity=current_user_id)
    
    return jsonify({
        'access_token': access_token
    }), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    current_user_id = get_jwt_identity()
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT id, nombre, apellido, correo, activo, fecha_creacion FROM usuarios WHERE id = %s", (current_user_id,))
    usuario = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    if not usuario:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    
    if usuario.get('fecha_creacion'):
        usuario['fecha_creacion'] = usuario['fecha_creacion'].isoformat()
    
    return jsonify(usuario), 200
