import json
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import get_db_connection

requerimientos_bp = Blueprint('requerimientos', __name__)


def generar_codigo(cursor, subproceso_id):
    cursor.execute(
        "SELECT COUNT(*) as total FROM requerimientos WHERE subproceso_id = %s",
        (subproceso_id,)
    )
    total = cursor.fetchone()['total']
    return f"REQ-{str(total + 1).zfill(3)}"


@requerimientos_bp.route('/subproceso/<int:subproceso_id>', methods=['GET'])
@jwt_required()
def listar_por_subproceso(subproceso_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT r.*, t.nombre as tecnica_nombre, t.categoria as tecnica_categoria
        FROM requerimientos r
        JOIN subproceso_tecnicas st ON r.subproceso_tecnica_id = st.id
        JOIN tecnicas t ON st.tecnica_id = t.id
        WHERE r.subproceso_id = %s
        ORDER BY r.codigo
    """, (subproceso_id,))

    requerimientos = cursor.fetchall()

    for req in requerimientos:
        cursor.execute(
            "SELECT * FROM criterios_aceptacion WHERE requerimiento_id = %s ORDER BY orden",
            (req['id'],)
        )
        criterios = cursor.fetchall()
        for c in criterios:
            if c.get('fecha_creacion'):
                c['fecha_creacion'] = c['fecha_creacion'].isoformat()
        req['criterios'] = criterios

        if req.get('fecha_creacion'):
            req['fecha_creacion'] = req['fecha_creacion'].isoformat()
        if req.get('fecha_actualizacion'):
            req['fecha_actualizacion'] = req['fecha_actualizacion'].isoformat()
        if req.get('metadata') and isinstance(req['metadata'], str):
            req['metadata'] = json.loads(req['metadata'])

    cursor.close()
    conn.close()

    return jsonify(requerimientos), 200


@requerimientos_bp.route('/tecnica/<int:subproceso_tecnica_id>', methods=['GET'])
@jwt_required()
def listar_por_tecnica(subproceso_tecnica_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT r.* FROM requerimientos r
        WHERE r.subproceso_tecnica_id = %s
        ORDER BY r.codigo
    """, (subproceso_tecnica_id,))

    requerimientos = cursor.fetchall()

    for req in requerimientos:
        cursor.execute(
            "SELECT * FROM criterios_aceptacion WHERE requerimiento_id = %s ORDER BY orden",
            (req['id'],)
        )
        criterios = cursor.fetchall()
        for c in criterios:
            if c.get('fecha_creacion'):
                c['fecha_creacion'] = c['fecha_creacion'].isoformat()
        req['criterios'] = criterios

        if req.get('fecha_creacion'):
            req['fecha_creacion'] = req['fecha_creacion'].isoformat()
        if req.get('fecha_actualizacion'):
            req['fecha_actualizacion'] = req['fecha_actualizacion'].isoformat()
        if req.get('metadata') and isinstance(req['metadata'], str):
            req['metadata'] = json.loads(req['metadata'])

    cursor.close()
    conn.close()

    return jsonify(requerimientos), 200


@requerimientos_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def obtener(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT r.*, t.nombre as tecnica_nombre, t.categoria as tecnica_categoria
        FROM requerimientos r
        JOIN subproceso_tecnicas st ON r.subproceso_tecnica_id = st.id
        JOIN tecnicas t ON st.tecnica_id = t.id
        WHERE r.id = %s
    """, (id,))

    req = cursor.fetchone()

    if not req:
        cursor.close()
        conn.close()
        return jsonify({'error': 'Requerimiento no encontrado'}), 404

    cursor.execute(
        "SELECT * FROM criterios_aceptacion WHERE requerimiento_id = %s ORDER BY orden",
        (req['id'],)
    )
    criterios = cursor.fetchall()
    for c in criterios:
        if c.get('fecha_creacion'):
            c['fecha_creacion'] = c['fecha_creacion'].isoformat()
    req['criterios'] = criterios

    if req.get('fecha_creacion'):
        req['fecha_creacion'] = req['fecha_creacion'].isoformat()
    if req.get('fecha_actualizacion'):
        req['fecha_actualizacion'] = req['fecha_actualizacion'].isoformat()
    if req.get('metadata') and isinstance(req['metadata'], str):
        req['metadata'] = json.loads(req['metadata'])

    cursor.close()
    conn.close()

    return jsonify(req), 200


@requerimientos_bp.route('', methods=['POST'])
@jwt_required()
def crear():
    current_user_id = get_jwt_identity()
    data = request.get_json()

    required = ['subproceso_id', 'subproceso_tecnica_id', 'titulo']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'El campo {field} es requerido'}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    codigo = generar_codigo(cursor, data['subproceso_id'])

    metadata_value = None
    if data.get('metadata'):
        metadata_value = json.dumps(data['metadata']) if isinstance(data['metadata'], dict) else data['metadata']

    cursor.execute("""
        INSERT INTO requerimientos (subproceso_id, subproceso_tecnica_id, codigo, titulo, descripcion, tipo, prioridad, estado, metadata, creado_por)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        data['subproceso_id'],
        data['subproceso_tecnica_id'],
        codigo,
        data['titulo'],
        data.get('descripcion'),
        data.get('tipo', 'funcional'),
        data.get('prioridad', 'media'),
        data.get('estado', 'borrador'),
        metadata_value,
        current_user_id
    ))
    conn.commit()

    req_id = cursor.lastrowid

    if data.get('criterios'):
        for i, criterio in enumerate(data['criterios']):
            cursor.execute("""
                INSERT INTO criterios_aceptacion (requerimiento_id, descripcion, orden)
                VALUES (%s, %s, %s)
            """, (req_id, criterio['descripcion'], i))
        conn.commit()

    cursor.execute("""
        SELECT r.*, t.nombre as tecnica_nombre, t.categoria as tecnica_categoria
        FROM requerimientos r
        JOIN subproceso_tecnicas st ON r.subproceso_tecnica_id = st.id
        JOIN tecnicas t ON st.tecnica_id = t.id
        WHERE r.id = %s
    """, (req_id,))

    req = cursor.fetchone()

    cursor.execute(
        "SELECT * FROM criterios_aceptacion WHERE requerimiento_id = %s ORDER BY orden",
        (req_id,)
    )
    criterios = cursor.fetchall()
    for c in criterios:
        if c.get('fecha_creacion'):
            c['fecha_creacion'] = c['fecha_creacion'].isoformat()
    req['criterios'] = criterios

    if req.get('fecha_creacion'):
        req['fecha_creacion'] = req['fecha_creacion'].isoformat()
    if req.get('fecha_actualizacion'):
        req['fecha_actualizacion'] = req['fecha_actualizacion'].isoformat()
    if req.get('metadata') and isinstance(req['metadata'], str):
        req['metadata'] = json.loads(req['metadata'])

    cursor.close()
    conn.close()

    return jsonify({
        'message': 'Requerimiento creado',
        'requerimiento': req
    }), 201


@requerimientos_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def actualizar(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT id FROM requerimientos WHERE id = %s", (id,))
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({'error': 'Requerimiento no encontrado'}), 404

    data = request.get_json()

    updates = []
    values = []

    campos_texto = ['titulo', 'descripcion', 'tipo', 'prioridad', 'estado']
    for campo in campos_texto:
        if campo in data:
            updates.append(f"{campo} = %s")
            values.append(data[campo])

    if 'metadata' in data:
        updates.append("metadata = %s")
        meta = data['metadata']
        values.append(json.dumps(meta) if isinstance(meta, dict) else meta)

    if updates:
        values.append(id)
        cursor.execute(f"UPDATE requerimientos SET {', '.join(updates)} WHERE id = %s", values)
        conn.commit()

    cursor.execute("""
        SELECT r.*, t.nombre as tecnica_nombre, t.categoria as tecnica_categoria
        FROM requerimientos r
        JOIN subproceso_tecnicas st ON r.subproceso_tecnica_id = st.id
        JOIN tecnicas t ON st.tecnica_id = t.id
        WHERE r.id = %s
    """, (id,))

    req = cursor.fetchone()

    cursor.execute(
        "SELECT * FROM criterios_aceptacion WHERE requerimiento_id = %s ORDER BY orden",
        (id,)
    )
    criterios = cursor.fetchall()
    for c in criterios:
        if c.get('fecha_creacion'):
            c['fecha_creacion'] = c['fecha_creacion'].isoformat()
    req['criterios'] = criterios

    if req.get('fecha_creacion'):
        req['fecha_creacion'] = req['fecha_creacion'].isoformat()
    if req.get('fecha_actualizacion'):
        req['fecha_actualizacion'] = req['fecha_actualizacion'].isoformat()
    if req.get('metadata') and isinstance(req['metadata'], str):
        req['metadata'] = json.loads(req['metadata'])

    cursor.close()
    conn.close()

    return jsonify({
        'message': 'Requerimiento actualizado',
        'requerimiento': req
    }), 200


@requerimientos_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def eliminar(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT id FROM requerimientos WHERE id = %s", (id,))
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({'error': 'Requerimiento no encontrado'}), 404

    cursor.execute("DELETE FROM requerimientos WHERE id = %s", (id,))
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({'message': 'Requerimiento eliminado'}), 200


# --- Criterios de aceptacion ---

@requerimientos_bp.route('/<int:requerimiento_id>/criterios', methods=['POST'])
@jwt_required()
def agregar_criterio(requerimiento_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT id FROM requerimientos WHERE id = %s", (requerimiento_id,))
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({'error': 'Requerimiento no encontrado'}), 404

    data = request.get_json()

    if not data.get('descripcion'):
        cursor.close()
        conn.close()
        return jsonify({'error': 'La descripcion es requerida'}), 400

    cursor.execute(
        "SELECT COALESCE(MAX(orden), -1) + 1 as siguiente FROM criterios_aceptacion WHERE requerimiento_id = %s",
        (requerimiento_id,)
    )
    siguiente_orden = cursor.fetchone()['siguiente']

    cursor.execute("""
        INSERT INTO criterios_aceptacion (requerimiento_id, descripcion, orden)
        VALUES (%s, %s, %s)
    """, (requerimiento_id, data['descripcion'], siguiente_orden))
    conn.commit()

    criterio_id = cursor.lastrowid

    cursor.execute("SELECT * FROM criterios_aceptacion WHERE id = %s", (criterio_id,))
    criterio = cursor.fetchone()

    if criterio.get('fecha_creacion'):
        criterio['fecha_creacion'] = criterio['fecha_creacion'].isoformat()

    cursor.close()
    conn.close()

    return jsonify({
        'message': 'Criterio agregado',
        'criterio': criterio
    }), 201


@requerimientos_bp.route('/criterios/<int:id>', methods=['PUT'])
@jwt_required()
def actualizar_criterio(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT id FROM criterios_aceptacion WHERE id = %s", (id,))
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({'error': 'Criterio no encontrado'}), 404

    data = request.get_json()

    updates = []
    values = []

    if 'descripcion' in data:
        updates.append("descripcion = %s")
        values.append(data['descripcion'])
    if 'cumplido' in data:
        updates.append("cumplido = %s")
        values.append(data['cumplido'])
    if 'orden' in data:
        updates.append("orden = %s")
        values.append(data['orden'])

    if updates:
        values.append(id)
        cursor.execute(f"UPDATE criterios_aceptacion SET {', '.join(updates)} WHERE id = %s", values)
        conn.commit()

    cursor.execute("SELECT * FROM criterios_aceptacion WHERE id = %s", (id,))
    criterio = cursor.fetchone()

    if criterio.get('fecha_creacion'):
        criterio['fecha_creacion'] = criterio['fecha_creacion'].isoformat()

    cursor.close()
    conn.close()

    return jsonify({
        'message': 'Criterio actualizado',
        'criterio': criterio
    }), 200


@requerimientos_bp.route('/criterios/<int:id>', methods=['DELETE'])
@jwt_required()
def eliminar_criterio(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT id FROM criterios_aceptacion WHERE id = %s", (id,))
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({'error': 'Criterio no encontrado'}), 404

    cursor.execute("DELETE FROM criterios_aceptacion WHERE id = %s", (id,))
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({'message': 'Criterio eliminado'}), 200
