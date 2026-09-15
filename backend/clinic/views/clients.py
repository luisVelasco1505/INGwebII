from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from clinic.errors import bad_request, forbidden, not_found
from clinic.models import Client


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def client_list(request):
    if request.method == 'POST':
        if request.user.role not in ('admin', 'vet'):
            return forbidden()

        data = request.data or {}
        name = (data.get('name') or '').strip()
        if not name:
            return bad_request('name es obligatorio')

        client = Client.objects.create(
            name=name,
            email=data.get('email'),
            phone=data.get('phone'),
            address=data.get('address'),
        )
        return Response(client.to_dict(), status=status.HTTP_201_CREATED)

    if request.user.role == 'client':
        client = Client.objects.filter(id=request.user.client_id).first()
        return Response([client.to_dict()] if client else [])

    clients = Client.objects.order_by('id')
    return Response([c.to_dict() for c in clients])


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def client_detail(request, client_id):
    if request.method == 'GET':
        if request.user.role == 'client' and request.user.client_id != client_id:
            return forbidden('No tenés permisos para ver este cliente')
        client = Client.objects.filter(id=client_id).first()
        if not client:
            return not_found('Cliente no encontrado')
        return Response(client.to_dict())

    client = Client.objects.filter(id=client_id).first()
    if not client:
        return not_found('Cliente no encontrado')

    if request.method == 'PUT':
        if request.user.role not in ('admin', 'vet'):
            return forbidden()

        data = request.data or {}
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
        client.save()
        return Response(client.to_dict())

    if request.method == 'DELETE':
        if request.user.role != 'admin':
            return forbidden()
        client.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
