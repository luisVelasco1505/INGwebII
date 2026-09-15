from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token

from app.errors import bad_request
from app.extensions import db
from app.models.user import User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


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


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify(error='Credenciales inválidas'), 401

    access_token = create_access_token(
        identity=str(user.id), additional_claims={'role': user.role}
    )
    return jsonify(access_token=access_token, user=user.to_dict())
