from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from extensions import get_db_connection

subproceso_tecnicas_bp = Blueprint('subproceso_tecnicas', __name__)


@subproceso_tecnicas_bp.route('/subproceso/<int:subproceso_id>', methods=['GET'])
@jwt_required()
def listar_tecnicas_subproceso(subproceso_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT st.*, t.nombre as tecnica_nombre, t.categoria as tecnica_categoria
        FROM subproceso_tecnicas st
        JOIN tecnicas t ON st.tecnica_id = t.id
        WHERE st.subproceso_id = %s
    """, (subproceso_id,))
    
    asignaciones = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    result = []
    for a in asignaciones:
        result.append({
            'id': a['id'],
            'subproceso_id': a['subproceso_id'],
            'tecnica_id': a['tecnica_id'],
            'notas': a['notas'],
            'fecha_asignacion': a['fecha_asignacion'].isoformat() if a.get('fecha_asignacion') else None,
            'tecnica': {
                'id': a['tecnica_id'],
                'nombre': a['tecnica_nombre'],
                'categoria': a['tecnica_categoria']
            }
        })
    
    return jsonify(result), 200


@subproceso_tecnicas_bp.route('', methods=['POST'])
@jwt_required()
def asignar_tecnica():
    data = request.get_json()
    
    if not data.get('subproceso_id'):
        return jsonify({'error': 'El subproceso_id es requerido'}), 400
    
    if not data.get('tecnica_id'):
        return jsonify({'error': 'El tecnica_id es requerido'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT id FROM subproceso_tecnicas WHERE subproceso_id = %s AND tecnica_id = %s
    """, (data['subproceso_id'], data['tecnica_id']))
    
    if cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({'error': 'La tecnica ya esta asignada a este subproceso'}), 400
    
    cursor.execute("""
        INSERT INTO subproceso_tecnicas (subproceso_id, tecnica_id, notas)
        VALUES (%s, %s, %s)
    """, (data['subproceso_id'], data['tecnica_id'], data.get('notas')))
    conn.commit()
    
    asignacion_id = cursor.lastrowid
    
    cursor.execute("""
        SELECT st.*, t.nombre as tecnica_nombre, t.categoria as tecnica_categoria
        FROM subproceso_tecnicas st
        JOIN tecnicas t ON st.tecnica_id = t.id
        WHERE st.id = %s
    """, (asignacion_id,))
    
    a = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    asignacion = {
        'id': a['id'],
        'subproceso_id': a['subproceso_id'],
        'tecnica_id': a['tecnica_id'],
        'notas': a['notas'],
        'fecha_asignacion': a['fecha_asignacion'].isoformat() if a.get('fecha_asignacion') else None,
        'tecnica': {
            'id': a['tecnica_id'],
            'nombre': a['tecnica_nombre'],
            'categoria': a['tecnica_categoria']
        }
    }
    
    return jsonify({
        'message': 'Tecnica asignada',
        'asignacion': asignacion
    }), 201


@subproceso_tecnicas_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def actualizar_asignacion(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT id FROM subproceso_tecnicas WHERE id = %s", (id,))
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({'error': 'Asignacion no encontrada'}), 404
    
    data = request.get_json()
    
    if 'notas' in data:
        cursor.execute("UPDATE subproceso_tecnicas SET notas = %s WHERE id = %s", (data['notas'], id))
        conn.commit()
    
    cursor.execute("""
        SELECT st.*, t.nombre as tecnica_nombre, t.categoria as tecnica_categoria
        FROM subproceso_tecnicas st
        JOIN tecnicas t ON st.tecnica_id = t.id
        WHERE st.id = %s
    """, (id,))
    
    a = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    asignacion = {
        'id': a['id'],
        'subproceso_id': a['subproceso_id'],
        'tecnica_id': a['tecnica_id'],
        'notas': a['notas'],
        'fecha_asignacion': a['fecha_asignacion'].isoformat() if a.get('fecha_asignacion') else None,
        'tecnica': {
            'id': a['tecnica_id'],
            'nombre': a['tecnica_nombre'],
            'categoria': a['tecnica_categoria']
        }
    }
    
    return jsonify({
        'message': 'Asignacion actualizada',
        'asignacion': asignacion
    }), 200


@subproceso_tecnicas_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def eliminar_asignacion(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT id FROM subproceso_tecnicas WHERE id = %s", (id,))
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({'error': 'Asignacion no encontrada'}), 404
    
    cursor.execute("DELETE FROM subproceso_tecnicas WHERE id = %s", (id,))
    conn.commit()
    
    cursor.close()
    conn.close()
    
    return jsonify({'message': 'Asignacion eliminada'}), 200
