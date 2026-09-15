from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token

from app.errors import bad_request
from app.extensions import db
from app.models.client import Client
from app.models.pet import SPECIES, Pet
from app.models.user import User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


def issue_token(user):
    return create_access_token(
        identity=str(user.id),
        additional_claims={'role': user.role, 'client_id': user.client_id},
    )


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json(silent=True) or {}
    name = (data.get('name') or '').strip()
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    if not name or not email or not password:
        return bad_request('name, email y password son obligatorios')

    if User.query.filter_by(email=email).first():
        return bad_request('Ya existe un usuario con ese email')

    user = User(name=name, email=email, role='vet')
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify(user.to_dict()), 201


@auth_bp.route('/register-client', methods=['POST'])
def register_client():
    data = request.get_json(silent=True) or {}
    name = (data.get('name') or '').strip()
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''
    phone = data.get('phone')
    address = data.get('address')

    pet_data = data.get('pet') or {}
    pet_name = (pet_data.get('name') or '').strip()
    pet_species = pet_data.get('species')

    if not name or not email or not password:
        return bad_request('name, email y password son obligatorios')
    if not pet_name or pet_species not in SPECIES:
        return bad_request(
            f'Se requiere al menos una mascota con name y species '
            f'({", ".join(SPECIES)})'
        )
    if User.query.filter_by(email=email).first():
        return bad_request('Ya existe una cuenta con ese email')

    client = Client.query.filter_by(email=email).first()
    if client:
        if User.query.filter_by(client_id=client.id).first():
            return bad_request('Ese cliente ya tiene una cuenta, iniciá sesión')
        client.name = name
        client.phone = phone or client.phone
        client.address = address or client.address
    else:
        client = Client(name=name, email=email, phone=phone, address=address)
        db.session.add(client)
        db.session.flush()

    pet = Pet(
        client_id=client.id,
        name=pet_name,
        species=pet_species,
        breed=pet_data.get('breed'),
        age=pet_data.get('age'),
        weight=pet_data.get('weight'),
    )
    db.session.add(pet)

    user = User(name=name, email=email, role='client', client_id=client.id)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    access_token = issue_token(user)
    return jsonify(access_token=access_token, user=user.to_dict()), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify(error='Credenciales inválidas'), 401

    access_token = issue_token(user)
    return jsonify(access_token=access_token, user=user.to_dict())
