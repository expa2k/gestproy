from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import get_db_connection

miembros_bp = Blueprint('miembros', __name__)


@miembros_bp.route('/proyecto/<int:proyecto_id>', methods=['GET'])
@jwt_required()
def listar_miembros(proyecto_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT mp.*, 
               u.nombre as usuario_nombre, u.apellido as usuario_apellido, u.correo as usuario_correo,
               r.nombre as rol_nombre
        FROM miembros_proyecto mp
        JOIN usuarios u ON mp.usuario_id = u.id
        JOIN roles r ON mp.rol_id = r.id
        WHERE mp.proyecto_id = %s
    """, (proyecto_id,))
    
    miembros = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    result = []
    for m in miembros:
        result.append({
            'id': m['id'],
            'proyecto_id': m['proyecto_id'],
            'usuario_id': m['usuario_id'],
            'rol_id': m['rol_id'],
            'asignado_por': m['asignado_por'],
            'fecha_asignacion': m['fecha_asignacion'].isoformat() if m.get('fecha_asignacion') else None,
            'usuario': {
                'id': m['usuario_id'],
                'nombre': m['usuario_nombre'],
                'apellido': m['usuario_apellido'],
                'correo': m['usuario_correo']
            },
            'rol': {
                'id': m['rol_id'],
                'nombre': m['rol_nombre']
            }
        })
    
    return jsonify(result), 200


@miembros_bp.route('', methods=['POST'])
@jwt_required()
def asignar_miembro():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    required = ['proyecto_id', 'usuario_id', 'rol_id']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'El campo {field} es requerido'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT id FROM miembros_proyecto WHERE proyecto_id = %s AND usuario_id = %s
    """, (data['proyecto_id'], data['usuario_id']))
    
    if cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({'error': 'El usuario ya es miembro de este proyecto'}), 400
    
    cursor.execute("SELECT nombre FROM roles WHERE id = %s AND es_fijo = 1", (data['rol_id'],))
    rol_fijo = cursor.fetchone()
    
    if rol_fijo and rol_fijo['nombre'] in ['Product Owner', 'Technical Leader']:
        cursor.execute("""
            SELECT mp.id FROM miembros_proyecto mp
            WHERE mp.proyecto_id = %s AND mp.rol_id = %s
        """, (data['proyecto_id'], data['rol_id']))
        
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({'error': f'Ya existe un {rol_fijo["nombre"]} en este proyecto'}), 400
    
    cursor.execute("""
        INSERT INTO miembros_proyecto (proyecto_id, usuario_id, rol_id, asignado_por)
        VALUES (%s, %s, %s, %s)
    """, (data['proyecto_id'], data['usuario_id'], data['rol_id'], current_user_id))
    conn.commit()
    
    miembro_id = cursor.lastrowid
    
    cursor.execute("""
        SELECT mp.*, 
               u.nombre as usuario_nombre, u.apellido as usuario_apellido, u.correo as usuario_correo,
               r.nombre as rol_nombre
        FROM miembros_proyecto mp
        JOIN usuarios u ON mp.usuario_id = u.id
        JOIN roles r ON mp.rol_id = r.id
        WHERE mp.id = %s
    """, (miembro_id,))
    
    m = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    miembro = {
        'id': m['id'],
        'proyecto_id': m['proyecto_id'],
        'usuario_id': m['usuario_id'],
        'rol_id': m['rol_id'],
        'asignado_por': m['asignado_por'],
        'fecha_asignacion': m['fecha_asignacion'].isoformat() if m.get('fecha_asignacion') else None,
        'usuario': {
            'id': m['usuario_id'],
            'nombre': m['usuario_nombre'],
            'apellido': m['usuario_apellido'],
            'correo': m['usuario_correo']
        },
        'rol': {
            'id': m['rol_id'],
            'nombre': m['rol_nombre']
        }
    }
    
    return jsonify({
        'message': 'Miembro asignado',
        'miembro': miembro
    }), 201


@miembros_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def actualizar_miembro(id):
    data = request.get_json()
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT id, proyecto_id FROM miembros_proyecto WHERE id = %s", (id,))
    miembro_actual = cursor.fetchone()
    if not miembro_actual:
        cursor.close()
        conn.close()
        return jsonify({'error': 'Miembro no encontrado'}), 404
    
    if 'rol_id' in data:
        cursor.execute("SELECT nombre FROM roles WHERE id = %s AND es_fijo = 1", (data['rol_id'],))
        rol_fijo = cursor.fetchone()
        
        if rol_fijo and rol_fijo['nombre'] in ['Product Owner', 'Technical Leader']:
            cursor.execute("""
                SELECT mp.id FROM miembros_proyecto mp
                WHERE mp.proyecto_id = %s AND mp.rol_id = %s AND mp.id != %s
            """, (miembro_actual['proyecto_id'], data['rol_id'], id))
            
            if cursor.fetchone():
                cursor.close()
                conn.close()
                return jsonify({'error': f'Ya existe un {rol_fijo["nombre"]} en este proyecto'}), 400
        
        cursor.execute("UPDATE miembros_proyecto SET rol_id = %s WHERE id = %s", (data['rol_id'], id))
        conn.commit()
    
    cursor.execute("""
        SELECT mp.*, 
               u.nombre as usuario_nombre, u.apellido as usuario_apellido, u.correo as usuario_correo,
               r.nombre as rol_nombre
        FROM miembros_proyecto mp
        JOIN usuarios u ON mp.usuario_id = u.id
        JOIN roles r ON mp.rol_id = r.id
        WHERE mp.id = %s
    """, (id,))
    
    m = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    miembro = {
        'id': m['id'],
        'proyecto_id': m['proyecto_id'],
        'usuario_id': m['usuario_id'],
        'rol_id': m['rol_id'],
        'asignado_por': m['asignado_por'],
        'fecha_asignacion': m['fecha_asignacion'].isoformat() if m.get('fecha_asignacion') else None,
        'usuario': {
            'id': m['usuario_id'],
            'nombre': m['usuario_nombre'],
            'apellido': m['usuario_apellido'],
            'correo': m['usuario_correo']
        },
        'rol': {
            'id': m['rol_id'],
            'nombre': m['rol_nombre']
        }
    }
    
    return jsonify({
        'message': 'Miembro actualizado',
        'miembro': miembro
    }), 200


@miembros_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def eliminar_miembro(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT id FROM miembros_proyecto WHERE id = %s", (id,))
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({'error': 'Miembro no encontrado'}), 404
    
    cursor.execute("DELETE FROM miembros_proyecto WHERE id = %s", (id,))
    conn.commit()
    
    cursor.close()
    conn.close()
    
    return jsonify({'message': 'Miembro eliminado del proyecto'}), 200
