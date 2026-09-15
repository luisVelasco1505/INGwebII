from rest_framework.test import APITestCase

from clinic.models import Client, User
from clinic.views.auth import issue_token


class BaseAPITestCase(APITestCase):
    def make_user(self, email, role='vet', name='Test User', password='password123', client=None):
        return User.objects.create_user(
            email=email, name=name, password=password, role=role, client=client
        )

    def make_admin(self, email='admin@vet.com'):
        return self.make_user(email, role='admin', name='Admin')

    def make_vet(self, email='vet@vet.com'):
        return self.make_user(email, role='vet', name='Vet')

    def make_client_with_user(self, email='owner@mail.com', name='Owner'):
        client = Client.objects.create(name=name, email=email)
        user = self.make_user(email, role='client', name=name, client=client)
        return client, user

    def auth_as(self, user):
        token = issue_token(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        return token

    def clear_auth(self):
        self.client.credentials()
