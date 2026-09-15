from clinic.models import Client, Pet
from clinic.tests.base import BaseAPITestCase


class PetListTests(BaseAPITestCase):
    def test_vet_can_create_pet(self):
        client = Client.objects.create(name='Dueño')
        self.auth_as(self.make_vet())

        response = self.client.post(
            '/pets',
            {'name': 'Firulais', 'species': 'perro', 'client_id': client.id, 'age': 3},
            format='json',
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['client_id'], client.id)

    def test_invalid_species_is_rejected(self):
        client = Client.objects.create(name='Dueño')
        self.auth_as(self.make_vet())

        response = self.client.post(
            '/pets',
            {'name': 'X', 'species': 'dinosaurio', 'client_id': client.id},
            format='json',
        )
        self.assertEqual(response.status_code, 400)

    def test_unknown_client_id_is_rejected(self):
        self.auth_as(self.make_vet())
        response = self.client.post(
            '/pets', {'name': 'X', 'species': 'perro', 'client_id': 999}, format='json'
        )
        self.assertEqual(response.status_code, 400)

    def test_client_role_cannot_create_pet(self):
        owner, user = self.make_client_with_user()
        self.auth_as(user)

        response = self.client.post(
            '/pets',
            {'name': 'X', 'species': 'perro', 'client_id': owner.id},
            format='json',
        )
        self.assertEqual(response.status_code, 403)

    def test_filter_by_client_id(self):
        a = Client.objects.create(name='A')
        b = Client.objects.create(name='B')
        Pet.objects.create(client=a, name='Pet A', species='perro')
        Pet.objects.create(client=b, name='Pet B', species='gato')
        self.auth_as(self.make_admin())

        response = self.client.get(f'/pets?client_id={a.id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Pet A')

    def test_client_role_only_sees_own_pets(self):
        other_client = Client.objects.create(name='Otro')
        Pet.objects.create(client=other_client, name='Ajena', species='gato')

        owner, user = self.make_client_with_user()
        Pet.objects.create(client=owner, name='Toby', species='perro')
        self.auth_as(user)

        response = self.client.get('/pets')
        self.assertEqual(response.status_code, 200)
        names = [p['name'] for p in response.data]
        self.assertEqual(names, ['Toby'])


class PetDetailTests(BaseAPITestCase):
    def test_client_role_cannot_view_others_pet(self):
        other_client = Client.objects.create(name='Otro')
        pet = Pet.objects.create(client=other_client, name='Ajena', species='gato')

        _, user = self.make_client_with_user()
        self.auth_as(user)

        response = self.client.get(f'/pets/{pet.id}')
        self.assertEqual(response.status_code, 403)

    def test_admin_can_update_pet(self):
        client = Client.objects.create(name='Dueño')
        pet = Pet.objects.create(client=client, name='Toby', species='perro')
        self.auth_as(self.make_admin())

        response = self.client.put(f'/pets/{pet.id}', {'age': 5}, format='json')
        self.assertEqual(response.status_code, 200)
        pet.refresh_from_db()
        self.assertEqual(pet.age, 5)

    def test_only_admin_can_delete_pet(self):
        client = Client.objects.create(name='Dueño')
        pet = Pet.objects.create(client=client, name='Toby', species='perro')
        self.auth_as(self.make_vet())

        response = self.client.delete(f'/pets/{pet.id}')
        self.assertEqual(response.status_code, 403)

    def test_deleting_client_cascades_to_pets(self):
        client = Client.objects.create(name='Dueño')
        pet = Pet.objects.create(client=client, name='Toby', species='perro')
        self.auth_as(self.make_admin())

        response = self.client.delete(f'/clients/{client.id}')
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Pet.objects.filter(id=pet.id).exists())
