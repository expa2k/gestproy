from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from extensions import get_db_connection

tecnicas_bp = Blueprint('tecnicas', __name__)


@tecnicas_bp.route('', methods=['GET'])
@jwt_required()
def listar_tecnicas():
    categoria = request.args.get('categoria')
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if categoria:
        cursor.execute("SELECT * FROM tecnicas WHERE activo = TRUE AND categoria = %s", (categoria,))
    else:
        cursor.execute("SELECT * FROM tecnicas WHERE activo = TRUE")
    
    tecnicas = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    for t in tecnicas:
        if t.get('fecha_creacion'):
            t['fecha_creacion'] = t['fecha_creacion'].isoformat()
    
    return jsonify(tecnicas), 200


@tecnicas_bp.route('/todas', methods=['GET'])
@jwt_required()
def listar_todas_tecnicas():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM tecnicas")
    tecnicas = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    for t in tecnicas:
        if t.get('fecha_creacion'):
            t['fecha_creacion'] = t['fecha_creacion'].isoformat()
    
    return jsonify(tecnicas), 200


@tecnicas_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def obtener_tecnica(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM tecnicas WHERE id = %s", (id,))
    tecnica = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    if not tecnica:
        return jsonify({'error': 'Tecnica no encontrada'}), 404
    
    if tecnica.get('fecha_creacion'):
        tecnica['fecha_creacion'] = tecnica['fecha_creacion'].isoformat()
    
    return jsonify(tecnica), 200


@tecnicas_bp.route('', methods=['POST'])
@jwt_required()
def crear_tecnica():
    data = request.get_json()
    
    if not data.get('nombre'):
        return jsonify({'error': 'El nombre es requerido'}), 400
    
    if not data.get('categoria'):
        return jsonify({'error': 'La categoria es requerida'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        INSERT INTO tecnicas (nombre, descripcion, categoria, activo)
        VALUES (%s, %s, %s, %s)
    """, (
        data['nombre'],
        data.get('descripcion'),
        data['categoria'],
        data.get('activo', True)
    ))
    conn.commit()
    
    tecnica_id = cursor.lastrowid
    
    cursor.execute("SELECT * FROM tecnicas WHERE id = %s", (tecnica_id,))
    tecnica = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    if tecnica.get('fecha_creacion'):
        tecnica['fecha_creacion'] = tecnica['fecha_creacion'].isoformat()
    
    return jsonify({
        'message': 'Tecnica creada',
        'tecnica': tecnica
    }), 201


@tecnicas_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def actualizar_tecnica(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT id FROM tecnicas WHERE id = %s", (id,))
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({'error': 'Tecnica no encontrada'}), 404
    
    data = request.get_json()
    
    updates = []
    values = []
    
    campos = ['nombre', 'descripcion', 'categoria', 'activo']
    
    for campo in campos:
        if campo in data:
            updates.append(f"{campo} = %s")
            values.append(data[campo])
    
    if updates:
        values.append(id)
        cursor.execute(f"UPDATE tecnicas SET {', '.join(updates)} WHERE id = %s", values)
        conn.commit()
    
    cursor.execute("SELECT * FROM tecnicas WHERE id = %s", (id,))
    tecnica = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    if tecnica.get('fecha_creacion'):
        tecnica['fecha_creacion'] = tecnica['fecha_creacion'].isoformat()
    
    return jsonify({
        'message': 'Tecnica actualizada',
        'tecnica': tecnica
    }), 200


@tecnicas_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def desactivar_tecnica(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT id FROM tecnicas WHERE id = %s", (id,))
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({'error': 'Tecnica no encontrada'}), 404
    
    cursor.execute("UPDATE tecnicas SET activo = FALSE WHERE id = %s", (id,))
    conn.commit()
    
    cursor.close()
    conn.close()
    
    return jsonify({'message': 'Tecnica desactivada'}), 200
