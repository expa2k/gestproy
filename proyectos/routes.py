from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import get_db_connection

proyectos_bp = Blueprint('proyectos', __name__)


@proyectos_bp.route('', methods=['GET'])
@jwt_required()
def listar_proyectos():
    current_user_id = get_jwt_identity()
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT DISTINCT p.* FROM proyectos p
        LEFT JOIN miembros_proyecto mp ON p.id = mp.proyecto_id
        WHERE p.creado_por = %s OR mp.usuario_id = %s
    """, (current_user_id, current_user_id))
    
    proyectos = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    for p in proyectos:
        if p.get('fecha_inicio'):
            p['fecha_inicio'] = p['fecha_inicio'].isoformat()
        if p.get('fecha_fin'):
            p['fecha_fin'] = p['fecha_fin'].isoformat()
        if p.get('fecha_creacion'):
            p['fecha_creacion'] = p['fecha_creacion'].isoformat()
        if p.get('fecha_actualizacion'):
            p['fecha_actualizacion'] = p['fecha_actualizacion'].isoformat()
    
    return jsonify(proyectos), 200


@proyectos_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def obtener_proyecto(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM proyectos WHERE id = %s", (id,))
    proyecto = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    if not proyecto:
        return jsonify({'error': 'Proyecto no encontrado'}), 404
    
    if proyecto.get('fecha_inicio'):
        proyecto['fecha_inicio'] = proyecto['fecha_inicio'].isoformat()
    if proyecto.get('fecha_fin'):
        proyecto['fecha_fin'] = proyecto['fecha_fin'].isoformat()
    if proyecto.get('fecha_creacion'):
        proyecto['fecha_creacion'] = proyecto['fecha_creacion'].isoformat()
    if proyecto.get('fecha_actualizacion'):
        proyecto['fecha_actualizacion'] = proyecto['fecha_actualizacion'].isoformat()
    
    return jsonify(proyecto), 200


@proyectos_bp.route('', methods=['POST'])
@jwt_required()
def crear_proyecto():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data.get('nombre'):
        return jsonify({'error': 'El nombre es requerido'}), 400
    
    if not data.get('prioridad'):
        return jsonify({'error': 'La prioridad es requerida'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        INSERT INTO proyectos (nombre, descripcion, estado, prioridad, fecha_inicio, fecha_fin, creado_por)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        data['nombre'],
        data.get('descripcion'),
        data.get('estado', 'iniciado'),
        data['prioridad'],
        data.get('fecha_inicio'),
        data.get('fecha_fin'),
        current_user_id
    ))
    conn.commit()
    
    proyecto_id = cursor.lastrowid
    
    cursor.execute("SELECT id FROM roles WHERE nombre = 'Product Owner' AND es_fijo = 1")
    rol_po = cursor.fetchone()
    
    if rol_po:
        cursor.execute("""
            INSERT INTO miembros_proyecto (proyecto_id, usuario_id, rol_id, asignado_por)
            VALUES (%s, %s, %s, %s)
        """, (proyecto_id, current_user_id, rol_po['id'], current_user_id))
        conn.commit()
    
    cursor.execute("SELECT * FROM proyectos WHERE id = %s", (proyecto_id,))
    proyecto = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    if proyecto.get('fecha_inicio'):
        proyecto['fecha_inicio'] = proyecto['fecha_inicio'].isoformat()
    if proyecto.get('fecha_fin'):
        proyecto['fecha_fin'] = proyecto['fecha_fin'].isoformat()
    if proyecto.get('fecha_creacion'):
        proyecto['fecha_creacion'] = proyecto['fecha_creacion'].isoformat()
    if proyecto.get('fecha_actualizacion'):
        proyecto['fecha_actualizacion'] = proyecto['fecha_actualizacion'].isoformat()
    
    return jsonify({
        'message': 'Proyecto creado',
        'proyecto': proyecto
    }), 201


@proyectos_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def actualizar_proyecto(id):
    data = request.get_json()
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT id FROM proyectos WHERE id = %s", (id,))
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({'error': 'Proyecto no encontrado'}), 404
    
    updates = []
    values = []
    
    if 'nombre' in data:
        updates.append("nombre = %s")
        values.append(data['nombre'])
    if 'descripcion' in data:
        updates.append("descripcion = %s")
        values.append(data['descripcion'])
    if 'estado' in data:
        updates.append("estado = %s")
        values.append(data['estado'])
    if 'prioridad' in data:
        updates.append("prioridad = %s")
        values.append(data['prioridad'])
    if 'fecha_inicio' in data:
        updates.append("fecha_inicio = %s")
        values.append(data['fecha_inicio'] if data['fecha_inicio'] else None)
    if 'fecha_fin' in data:
        updates.append("fecha_fin = %s")
        values.append(data['fecha_fin'] if data['fecha_fin'] else None)
    
    if updates:
        values.append(id)
        cursor.execute(f"UPDATE proyectos SET {', '.join(updates)} WHERE id = %s", values)
        conn.commit()
    
    cursor.execute("SELECT * FROM proyectos WHERE id = %s", (id,))
    proyecto = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    if proyecto.get('fecha_inicio'):
        proyecto['fecha_inicio'] = proyecto['fecha_inicio'].isoformat()
    if proyecto.get('fecha_fin'):
        proyecto['fecha_fin'] = proyecto['fecha_fin'].isoformat()
    if proyecto.get('fecha_creacion'):
        proyecto['fecha_creacion'] = proyecto['fecha_creacion'].isoformat()
    if proyecto.get('fecha_actualizacion'):
        proyecto['fecha_actualizacion'] = proyecto['fecha_actualizacion'].isoformat()
    
    return jsonify({
        'message': 'Proyecto actualizado',
        'proyecto': proyecto
    }), 200


@proyectos_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def eliminar_proyecto(id):
    current_user_id = get_jwt_identity()
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT creado_por FROM proyectos WHERE id = %s", (id,))
    proyecto = cursor.fetchone()
    
    if not proyecto:
        cursor.close()
        conn.close()
        return jsonify({'error': 'Proyecto no encontrado'}), 404
    
    if proyecto['creado_por'] != current_user_id:
        cursor.close()
        conn.close()
        return jsonify({'error': 'No tienes permiso para eliminar este proyecto'}), 403
    
    cursor.execute("DELETE FROM proyectos WHERE id = %s", (id,))
    conn.commit()
    
    cursor.close()
    conn.close()
    
    return jsonify({'message': 'Proyecto eliminado'}), 200
