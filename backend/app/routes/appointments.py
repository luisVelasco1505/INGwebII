from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, jwt_required

from app.auth import role_required
from app.errors import bad_request, not_found
from app.extensions import db
from app.models.appointment import STATUSES, Appointment
from app.models.pet import Pet

appointments_bp = Blueprint('appointments', __name__, url_prefix='/appointments')


def parse_date(value):
    try:
        return datetime.fromisoformat(value)
    except (TypeError, ValueError):
        return None


@appointments_bp.route('', methods=['GET'])
@jwt_required()
def list_appointments():
    claims = get_jwt()
    query = Appointment.query

    if claims.get('role') == 'client':
        query = query.join(Pet).filter(Pet.client_id == claims.get('client_id'))

    pet_id = request.args.get('pet_id', type=int)
    status = request.args.get('status')
    if pet_id is not None:
        query = query.filter(Appointment.pet_id == pet_id)
    if status is not None:
        query = query.filter(Appointment.status == status)

    appointments = query.order_by(Appointment.id).all()
    return jsonify([a.to_dict() for a in appointments])


@appointments_bp.route('', methods=['POST'])
@role_required('admin', 'vet')
def create_appointment():
    data = request.get_json(silent=True) or {}
    pet_id = data.get('pet_id')
    reason = (data.get('reason') or '').strip()
    date = parse_date(data.get('date'))
    status = data.get('status', 'pendiente')

    if not pet_id or not reason or date is None:
        return bad_request('pet_id, reason y date (ISO 8601) son obligatorios')
    if not db.session.get(Pet, pet_id):
        return bad_request('pet_id no corresponde a una mascota existente')
    if status not in STATUSES:
        return bad_request(f'status debe ser una de: {", ".join(STATUSES)}')

    appointment = Appointment(
        pet_id=pet_id,
        date=date,
        reason=reason,
        diagnosis=data.get('diagnosis'),
        treatment=data.get('treatment'),
        status=status,
    )
    db.session.add(appointment)
    db.session.commit()

    return jsonify(appointment.to_dict()), 201


@appointments_bp.route('/<int:appointment_id>', methods=['GET'])
@jwt_required()
def get_appointment(appointment_id):
    appointment = db.session.get(Appointment, appointment_id)
    if not appointment:
        return not_found('Cita no encontrada')

    claims = get_jwt()
    if claims.get('role') == 'client':
        pet = db.session.get(Pet, appointment.pet_id)
        if not pet or pet.client_id != claims.get('client_id'):
            return jsonify(error='No tenés permisos para ver esta cita'), 403

    return jsonify(appointment.to_dict())


@appointments_bp.route('/<int:appointment_id>', methods=['PUT'])
@role_required('admin', 'vet')
def update_appointment(appointment_id):
    appointment = db.session.get(Appointment, appointment_id)
    if not appointment:
        return not_found('Cita no encontrada')

    data = request.get_json(silent=True) or {}
    if 'pet_id' in data:
        if not db.session.get(Pet, data.get('pet_id')):
            return bad_request('pet_id no corresponde a una mascota existente')
        appointment.pet_id = data.get('pet_id')
    if 'date' in data:
        date = parse_date(data.get('date'))
        if date is None:
            return bad_request('date debe tener formato ISO 8601')
        appointment.date = date
    if 'reason' in data:
        reason = (data.get('reason') or '').strip()
        if not reason:
            return bad_request('reason no puede estar vacío')
        appointment.reason = reason
    if 'diagnosis' in data:
        appointment.diagnosis = data.get('diagnosis')
    if 'treatment' in data:
        appointment.treatment = data.get('treatment')
    if 'status' in data:
        status = data.get('status')
        if status not in STATUSES:
            return bad_request(f'status debe ser una de: {", ".join(STATUSES)}')
        appointment.status = status

    db.session.commit()
    return jsonify(appointment.to_dict())


@appointments_bp.route('/<int:appointment_id>', methods=['DELETE'])
@role_required('admin')
def delete_appointment(appointment_id):
    appointment = db.session.get(Appointment, appointment_id)
    if not appointment:
        return not_found('Cita no encontrada')

    db.session.delete(appointment)
    db.session.commit()
    return '', 204
