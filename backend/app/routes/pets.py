from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, jwt_required

from app.auth import role_required
from app.errors import bad_request, not_found
from app.extensions import db
from app.models.client import Client
from app.models.pet import SPECIES, Pet

pets_bp = Blueprint('pets', __name__, url_prefix='/pets')


@pets_bp.route('', methods=['GET'])
@jwt_required()
def list_pets():
    claims = get_jwt()
    query = Pet.query

    if claims.get('role') == 'client':
        query = query.filter_by(client_id=claims.get('client_id'))
    else:
        client_id = request.args.get('client_id', type=int)
        if client_id is not None:
            query = query.filter_by(client_id=client_id)

    pets = query.order_by(Pet.id).all()
    return jsonify([p.to_dict() for p in pets])


@pets_bp.route('', methods=['POST'])
@role_required('admin', 'vet')
def create_pet():
    data = request.get_json(silent=True) or {}
    name = (data.get('name') or '').strip()
    species = data.get('species')
    client_id = data.get('client_id')

    if not name or not species or not client_id:
        return bad_request('name, species y client_id son obligatorios')
    if species not in SPECIES:
        return bad_request(f'species debe ser una de: {", ".join(SPECIES)}')
    if not db.session.get(Client, client_id):
        return bad_request('client_id no corresponde a un cliente existente')

    pet = Pet(
        name=name,
        species=species,
        client_id=client_id,
        breed=data.get('breed'),
        age=data.get('age'),
        weight=data.get('weight'),
    )
    db.session.add(pet)
    db.session.commit()

    return jsonify(pet.to_dict()), 201


@pets_bp.route('/<int:pet_id>', methods=['GET'])
@jwt_required()
def get_pet(pet_id):
    pet = db.session.get(Pet, pet_id)
    if not pet:
        return not_found('Mascota no encontrada')

    claims = get_jwt()
    if claims.get('role') == 'client' and pet.client_id != claims.get('client_id'):
        return jsonify(error='No tenés permisos para ver esta mascota'), 403

    return jsonify(pet.to_dict())


@pets_bp.route('/<int:pet_id>', methods=['PUT'])
@role_required('admin', 'vet')
def update_pet(pet_id):
    pet = db.session.get(Pet, pet_id)
    if not pet:
        return not_found('Mascota no encontrada')

    data = request.get_json(silent=True) or {}
    if 'name' in data:
        name = (data.get('name') or '').strip()
        if not name:
            return bad_request('name no puede estar vacío')
        pet.name = name
    if 'species' in data:
        species = data.get('species')
        if species not in SPECIES:
            return bad_request(f'species debe ser una de: {", ".join(SPECIES)}')
        pet.species = species
    if 'client_id' in data:
        if not db.session.get(Client, data.get('client_id')):
            return bad_request('client_id no corresponde a un cliente existente')
        pet.client_id = data.get('client_id')
    if 'breed' in data:
        pet.breed = data.get('breed')
    if 'age' in data:
        pet.age = data.get('age')
    if 'weight' in data:
        pet.weight = data.get('weight')

    db.session.commit()
    return jsonify(pet.to_dict())


@pets_bp.route('/<int:pet_id>', methods=['DELETE'])
@role_required('admin')
def delete_pet(pet_id):
    pet = db.session.get(Pet, pet_id)
    if not pet:
        return not_found('Mascota no encontrada')

    db.session.delete(pet)
    db.session.commit()
    return '', 204
