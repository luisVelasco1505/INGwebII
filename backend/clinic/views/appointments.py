from datetime import datetime

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from clinic.errors import bad_request, forbidden, not_found
from clinic.models import APPOINTMENT_STATUSES, Appointment, Pet


def parse_date(value):
    try:
        return datetime.fromisoformat(value)
    except (TypeError, ValueError):
        return None


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def appointment_list(request):
    if request.method == 'POST':
        if request.user.role not in ('admin', 'vet'):
            return forbidden()

        data = request.data or {}
        pet_id = data.get('pet_id')
        reason = (data.get('reason') or '').strip()
        date = parse_date(data.get('date'))
        status_value = data.get('status', 'pendiente')

        if not pet_id or not reason or date is None:
            return bad_request('pet_id, reason y date (ISO 8601) son obligatorios')
        if not Pet.objects.filter(id=pet_id).exists():
            return bad_request('pet_id no corresponde a una mascota existente')
        if status_value not in dict(APPOINTMENT_STATUSES):
            statuses = ', '.join(code for code, _ in APPOINTMENT_STATUSES)
            return bad_request(f'status debe ser una de: {statuses}')

        appointment = Appointment.objects.create(
            pet_id=pet_id,
            date=date,
            reason=reason,
            diagnosis=data.get('diagnosis'),
            treatment=data.get('treatment'),
            status=status_value,
        )
        return Response(appointment.to_dict(), status=status.HTTP_201_CREATED)

    appointments = Appointment.objects.all()
    if request.user.role == 'client':
        appointments = appointments.filter(pet__client_id=request.user.client_id)

    pet_id = request.query_params.get('pet_id')
    status_filter = request.query_params.get('status')
    if pet_id is not None:
        appointments = appointments.filter(pet_id=pet_id)
    if status_filter is not None:
        appointments = appointments.filter(status=status_filter)

    appointments = appointments.order_by('id')
    return Response([a.to_dict() for a in appointments])


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def appointment_detail(request, appointment_id):
    appointment = Appointment.objects.filter(id=appointment_id).first()

    if request.method == 'GET':
        if not appointment:
            return not_found('Cita no encontrada')
        if (
            request.user.role == 'client'
            and appointment.pet.client_id != request.user.client_id
        ):
            return forbidden('No tenés permisos para ver esta cita')
        return Response(appointment.to_dict())

    if not appointment:
        return not_found('Cita no encontrada')

    if request.method == 'PUT':
        if request.user.role not in ('admin', 'vet'):
            return forbidden()

        data = request.data or {}
        if 'pet_id' in data:
            if not Pet.objects.filter(id=data.get('pet_id')).exists():
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
            status_value = data.get('status')
            if status_value not in dict(APPOINTMENT_STATUSES):
                statuses = ', '.join(code for code, _ in APPOINTMENT_STATUSES)
                return bad_request(f'status debe ser una de: {statuses}')
            appointment.status = status_value
        appointment.save()
        return Response(appointment.to_dict())

    if request.method == 'DELETE':
        if request.user.role != 'admin':
            return forbidden()
        appointment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
