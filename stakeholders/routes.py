from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from extensions import get_db_connection

stakeholders_bp = Blueprint('stakeholders', __name__)


@stakeholders_bp.route('/proyecto/<int:proyecto_id>', methods=['GET'])
@jwt_required()
def listar_stakeholders(proyecto_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM stakeholders WHERE proyecto_id = %s", (proyecto_id,))
    stakeholders = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    for s in stakeholders:
        if s.get('fecha_creacion'):
            s['fecha_creacion'] = s['fecha_creacion'].isoformat()
    
    return jsonify(stakeholders), 200


@stakeholders_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def obtener_stakeholder(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM stakeholders WHERE id = %s", (id,))
    stakeholder = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    if not stakeholder:
        return jsonify({'error': 'Stakeholder no encontrado'}), 404
    
    if stakeholder.get('fecha_creacion'):
        stakeholder['fecha_creacion'] = stakeholder['fecha_creacion'].isoformat()
    
    return jsonify(stakeholder), 200


@stakeholders_bp.route('', methods=['POST'])
@jwt_required()
def crear_stakeholder():
    data = request.get_json()
    
    required = ['proyecto_id', 'nombre_completo', 'tipo', 'nivel_influencia_interes']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'El campo {field} es requerido'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        INSERT INTO stakeholders (proyecto_id, nombre_completo, correo, telefono, organizacion, cargo, tipo, nivel_influencia_interes, notas)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        data['proyecto_id'],
        data['nombre_completo'],
        data.get('correo'),
        data.get('telefono'),
        data.get('organizacion'),
        data.get('cargo'),
        data['tipo'],
        data['nivel_influencia_interes'],
        data.get('notas')
    ))
    conn.commit()
    
    stakeholder_id = cursor.lastrowid
    
    cursor.execute("SELECT * FROM stakeholders WHERE id = %s", (stakeholder_id,))
    stakeholder = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    if stakeholder.get('fecha_creacion'):
        stakeholder['fecha_creacion'] = stakeholder['fecha_creacion'].isoformat()
    
    return jsonify({
        'message': 'Stakeholder creado',
        'stakeholder': stakeholder
    }), 201


@stakeholders_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def actualizar_stakeholder(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT id FROM stakeholders WHERE id = %s", (id,))
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({'error': 'Stakeholder no encontrado'}), 404
    
    data = request.get_json()
    
    updates = []
    values = []
    
    campos = ['nombre_completo', 'correo', 'telefono', 'organizacion', 'cargo', 'tipo', 'nivel_influencia_interes', 'notas']
    
    for campo in campos:
        if campo in data:
            updates.append(f"{campo} = %s")
            values.append(data[campo])
    
    if updates:
        values.append(id)
        cursor.execute(f"UPDATE stakeholders SET {', '.join(updates)} WHERE id = %s", values)
        conn.commit()
    
    cursor.execute("SELECT * FROM stakeholders WHERE id = %s", (id,))
    stakeholder = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    if stakeholder.get('fecha_creacion'):
        stakeholder['fecha_creacion'] = stakeholder['fecha_creacion'].isoformat()
    
    return jsonify({
        'message': 'Stakeholder actualizado',
        'stakeholder': stakeholder
    }), 200


@stakeholders_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def eliminar_stakeholder(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT id FROM stakeholders WHERE id = %s", (id,))
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({'error': 'Stakeholder no encontrado'}), 404
    
    cursor.execute("DELETE FROM stakeholders WHERE id = %s", (id,))
    conn.commit()
    
    cursor.close()
    conn.close()
    
    return jsonify({'message': 'Stakeholder eliminado'}), 200
