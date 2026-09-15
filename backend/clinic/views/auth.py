from django.db import transaction
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken

from clinic.errors import bad_request
from clinic.models import SPECIES, Client, Pet, User


def issue_token(user):
    token = AccessToken.for_user(user)
    token['role'] = user.role
    token['client_id'] = user.client_id
    return str(token)


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    data = request.data or {}
    name = (data.get('name') or '').strip()
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    if not name or not email or not password:
        return bad_request('name, email y password son obligatorios')

    if User.objects.filter(email=email).exists():
        return bad_request('Ya existe un usuario con ese email')

    user = User.objects.create_user(email=email, name=name, password=password, role='vet')

    return Response(user.to_dict(), status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
@transaction.atomic
def register_client(request):
    data = request.data or {}
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
    if not pet_name or pet_species not in dict(SPECIES):
        species_list = ', '.join(code for code, _ in SPECIES)
        return bad_request(
            f'Se requiere al menos una mascota con name y species ({species_list})'
        )
    if User.objects.filter(email=email).exists():
        return bad_request('Ya existe una cuenta con ese email')

    client = Client.objects.filter(email=email).first()
    if client:
        if User.objects.filter(client_id=client.id).exists():
            return bad_request('Ese cliente ya tiene una cuenta, iniciá sesión')
        client.name = name
        client.phone = phone or client.phone
        client.address = address or client.address
        client.save()
    else:
        client = Client.objects.create(name=name, email=email, phone=phone, address=address)

    Pet.objects.create(
        client=client,
        name=pet_name,
        species=pet_species,
        breed=pet_data.get('breed'),
        age=pet_data.get('age'),
        weight=pet_data.get('weight'),
    )

    user = User.objects.create_user(
        email=email, name=name, password=password, role='client', client=client
    )

    return Response(
        {'access_token': issue_token(user), 'user': user.to_dict()},
        status=status.HTTP_201_CREATED,
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    data = request.data or {}
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    user = User.objects.filter(email=email).first()
    if not user or not user.check_password(password):
        return Response({'error': 'Credenciales inválidas'}, status=status.HTTP_401_UNAUTHORIZED)

    return Response({'access_token': issue_token(user), 'user': user.to_dict()})
