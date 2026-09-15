from clinic.models import Client, Pet, User
from clinic.tests.base import BaseAPITestCase


class RegisterTests(BaseAPITestCase):
    def test_register_creates_vet(self):
        response = self.client.post(
            '/auth/register',
            {'name': 'Dra Vet', 'email': 'vet@vet.com', 'password': 'vet12345'},
            format='json',
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['role'], 'vet')
        self.assertTrue(User.objects.filter(email='vet@vet.com', role='vet').exists())

    def test_register_duplicate_email(self):
        self.make_vet(email='vet@vet.com')
        response = self.client.post(
            '/auth/register',
            {'name': 'Otra', 'email': 'vet@vet.com', 'password': 'x1234567'},
            format='json',
        )
        self.assertEqual(response.status_code, 400)

    def test_register_missing_fields(self):
        response = self.client.post('/auth/register', {'email': 'x@x.com'}, format='json')
        self.assertEqual(response.status_code, 400)


class RegisterClientTests(BaseAPITestCase):
    def payload(self, **overrides):
        data = {
            'name': 'Ana Lopez',
            'email': 'ana@mail.com',
            'phone': '555-1111',
            'address': 'Calle 1',
            'password': 'ana12345',
            'pet': {'name': 'Toby', 'species': 'perro', 'breed': 'Beagle', 'age': 2, 'weight': 10.5},
        }
        data.update(overrides)
        return data

    def test_creates_new_client_and_pet_and_returns_token(self):
        response = self.client.post('/auth/register-client', self.payload(), format='json')

        self.assertEqual(response.status_code, 201)
        self.assertIn('access_token', response.data)
        self.assertEqual(response.data['user']['role'], 'client')

        client = Client.objects.get(email='ana@mail.com')
        self.assertEqual(client.name, 'Ana Lopez')
        self.assertTrue(Pet.objects.filter(client=client, name='Toby').exists())

    def test_missing_pet_is_rejected(self):
        response = self.client.post(
            '/auth/register-client', self.payload(pet={}), format='json'
        )
        self.assertEqual(response.status_code, 400)

    def test_links_to_existing_staff_created_client_without_duplicating(self):
        client = Client.objects.create(name='Carlos Ruiz', email='carlos@mail.com', phone='555-2222')
        Pet.objects.create(client=client, name='Michi', species='gato')

        response = self.client.post(
            '/auth/register-client',
            self.payload(
                name='Carlos Ruiz',
                email='carlos@mail.com',
                pet={'name': 'Rocky', 'species': 'perro'},
            ),
            format='json',
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Client.objects.filter(email='carlos@mail.com').count(), 1)
        self.assertEqual(response.data['user']['client_id'], client.id)
        self.assertEqual(Pet.objects.filter(client=client).count(), 2)

    def test_existing_account_cannot_register_again(self):
        self.client.post('/auth/register-client', self.payload(), format='json')

        response = self.client.post(
            '/auth/register-client',
            self.payload(pet={'name': 'Otro', 'species': 'gato'}),
            format='json',
        )
        self.assertEqual(response.status_code, 400)


class LoginTests(BaseAPITestCase):
    def test_login_success_returns_token_and_user(self):
        self.make_vet(email='vet@vet.com')
        response = self.client.post(
            '/auth/login', {'email': 'vet@vet.com', 'password': 'password123'}, format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('access_token', response.data)
        self.assertEqual(response.data['user']['email'], 'vet@vet.com')

    def test_login_wrong_password(self):
        self.make_vet(email='vet@vet.com')
        response = self.client.post(
            '/auth/login', {'email': 'vet@vet.com', 'password': 'incorrecta'}, format='json'
        )
        self.assertEqual(response.status_code, 401)

    def test_login_unknown_email(self):
        response = self.client.post(
            '/auth/login', {'email': 'nadie@mail.com', 'password': 'x'}, format='json'
        )
        self.assertEqual(response.status_code, 401)
