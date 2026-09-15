from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from clinic.errors import bad_request, forbidden, not_found
from clinic.models import SPECIES, Client, Pet


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def pet_list(request):
    if request.method == 'POST':
        if request.user.role not in ('admin', 'vet'):
            return forbidden()

        data = request.data or {}
        name = (data.get('name') or '').strip()
        species = data.get('species')
        client_id = data.get('client_id')

        if not name or not species or not client_id:
            return bad_request('name, species y client_id son obligatorios')
        if species not in dict(SPECIES):
            species_list = ', '.join(code for code, _ in SPECIES)
            return bad_request(f'species debe ser una de: {species_list}')
        if not Client.objects.filter(id=client_id).exists():
            return bad_request('client_id no corresponde a un cliente existente')

        pet = Pet.objects.create(
            name=name,
            species=species,
            client_id=client_id,
            breed=data.get('breed'),
            age=data.get('age'),
            weight=data.get('weight'),
        )
        return Response(pet.to_dict(), status=status.HTTP_201_CREATED)

    pets = Pet.objects.all()
    if request.user.role == 'client':
        pets = pets.filter(client_id=request.user.client_id)
    else:
        client_id = request.query_params.get('client_id')
        if client_id is not None:
            pets = pets.filter(client_id=client_id)

    pets = pets.order_by('id')
    return Response([p.to_dict() for p in pets])


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def pet_detail(request, pet_id):
    pet = Pet.objects.filter(id=pet_id).first()

    if request.method == 'GET':
        if not pet:
            return not_found('Mascota no encontrada')
        if request.user.role == 'client' and pet.client_id != request.user.client_id:
            return forbidden('No tenés permisos para ver esta mascota')
        return Response(pet.to_dict())

    if not pet:
        return not_found('Mascota no encontrada')

    if request.method == 'PUT':
        if request.user.role not in ('admin', 'vet'):
            return forbidden()

        data = request.data or {}
        if 'name' in data:
            name = (data.get('name') or '').strip()
            if not name:
                return bad_request('name no puede estar vacío')
            pet.name = name
        if 'species' in data:
            species = data.get('species')
            if species not in dict(SPECIES):
                species_list = ', '.join(code for code, _ in SPECIES)
                return bad_request(f'species debe ser una de: {species_list}')
            pet.species = species
        if 'client_id' in data:
            if not Client.objects.filter(id=data.get('client_id')).exists():
                return bad_request('client_id no corresponde a un cliente existente')
            pet.client_id = data.get('client_id')
        if 'breed' in data:
            pet.breed = data.get('breed')
        if 'age' in data:
            pet.age = data.get('age')
        if 'weight' in data:
            pet.weight = data.get('weight')
        pet.save()
        return Response(pet.to_dict())

    if request.method == 'DELETE':
        if request.user.role != 'admin':
            return forbidden()
        pet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
