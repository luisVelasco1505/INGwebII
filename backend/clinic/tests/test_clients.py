from clinic.models import Client
from clinic.tests.base import BaseAPITestCase


class ClientListTests(BaseAPITestCase):
    def test_unauthenticated_request_is_rejected(self):
        response = self.client.get('/clients')
        self.assertEqual(response.status_code, 401)

    def test_admin_sees_all_clients(self):
        Client.objects.create(name='A')
        Client.objects.create(name='B')
        self.auth_as(self.make_admin())

        response = self.client.get('/clients')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_client_role_sees_only_own_record(self):
        Client.objects.create(name='Otro cliente')
        owner, user = self.make_client_with_user()
        self.auth_as(user)

        response = self.client.get('/clients')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], owner.id)

    def test_vet_can_create_client(self):
        self.auth_as(self.make_vet())
        response = self.client.post('/clients', {'name': 'Nuevo Cliente'}, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['name'], 'Nuevo Cliente')

    def test_create_requires_name(self):
        self.auth_as(self.make_vet())
        response = self.client.post('/clients', {}, format='json')
        self.assertEqual(response.status_code, 400)

    def test_client_role_cannot_create(self):
        _, user = self.make_client_with_user()
        self.auth_as(user)
        response = self.client.post('/clients', {'name': 'X'}, format='json')
        self.assertEqual(response.status_code, 403)


class ClientDetailTests(BaseAPITestCase):
    def test_get_missing_client_is_404(self):
        self.auth_as(self.make_admin())
        response = self.client.get('/clients/999')
        self.assertEqual(response.status_code, 404)

    def test_client_role_cannot_view_other_client(self):
        other = Client.objects.create(name='Otro')
        _, user = self.make_client_with_user()
        self.auth_as(user)

        response = self.client.get(f'/clients/{other.id}')
        self.assertEqual(response.status_code, 403)

    def test_client_role_can_view_own_record(self):
        owner, user = self.make_client_with_user()
        self.auth_as(user)

        response = self.client.get(f'/clients/{owner.id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], owner.id)

    def test_admin_can_update_client(self):
        client = Client.objects.create(name='Original')
        self.auth_as(self.make_admin())

        response = self.client.put(f'/clients/{client.id}', {'name': 'Actualizado'}, format='json')
        self.assertEqual(response.status_code, 200)
        client.refresh_from_db()
        self.assertEqual(client.name, 'Actualizado')

    def test_client_role_cannot_update(self):
        owner, user = self.make_client_with_user()
        self.auth_as(user)

        response = self.client.put(f'/clients/{owner.id}', {'name': 'Hackeado'}, format='json')
        self.assertEqual(response.status_code, 403)

    def test_only_admin_can_delete(self):
        client = Client.objects.create(name='Para borrar')
        self.auth_as(self.make_vet())

        response = self.client.delete(f'/clients/{client.id}')
        self.assertEqual(response.status_code, 403)

    def test_admin_delete_succeeds(self):
        client = Client.objects.create(name='Para borrar')
        self.auth_as(self.make_admin())

        response = self.client.delete(f'/clients/{client.id}')
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Client.objects.filter(id=client.id).exists())
