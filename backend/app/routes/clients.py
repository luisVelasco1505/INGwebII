from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.auth import role_required
from app.errors import bad_request, not_found
from app.extensions import db
from app.models.client import Client

clients_bp = Blueprint('clients', __name__, url_prefix='/clients')


@clients_bp.route('', methods=['GET'])
@jwt_required()
def list_clients():
    clients = Client.query.order_by(Client.id).all()
    return jsonify([c.to_dict() for c in clients])


@clients_bp.route('', methods=['POST'])
@jwt_required()
def create_client():
    data = request.get_json(silent=True) or {}
    name = (data.get('name') or '').strip()

    if not name:
        return bad_request('name es obligatorio')

    client = Client(
        name=name,
        email=data.get('email'),
        phone=data.get('phone'),
        address=data.get('address'),
    )
    db.session.add(client)
    db.session.commit()

    return jsonify(client.to_dict()), 201


@clients_bp.route('/<int:client_id>', methods=['GET'])
@jwt_required()
def get_client(client_id):
    client = db.session.get(Client, client_id)
    if not client:
        return not_found('Cliente no encontrado')
    return jsonify(client.to_dict())


@clients_bp.route('/<int:client_id>', methods=['PUT'])
@jwt_required()
def update_client(client_id):
    client = db.session.get(Client, client_id)
    if not client:
        return not_found('Cliente no encontrado')

    data = request.get_json(silent=True) or {}
    if 'name' in data:
        name = (data.get('name') or '').strip()
        if not name:
            return bad_request('name no puede estar vacío')
        client.name = name
    if 'email' in data:
        client.email = data.get('email')
    if 'phone' in data:
        client.phone = data.get('phone')
    if 'address' in data:
        client.address = data.get('address')

    db.session.commit()
    return jsonify(client.to_dict())


@clients_bp.route('/<int:client_id>', methods=['DELETE'])
@role_required('admin')
def delete_client(client_id):
    client = db.session.get(Client, client_id)
    if not client:
        return not_found('Cliente no encontrado')

    db.session.delete(client)
    db.session.commit()
    return '', 204
