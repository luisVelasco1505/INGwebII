from clinic.models import Appointment, Client, Pet
from clinic.tests.base import BaseAPITestCase


class AppointmentListTests(BaseAPITestCase):
    def setUp(self):
        self.client_owner = Client.objects.create(name='Dueño')
        self.pet = Pet.objects.create(client=self.client_owner, name='Toby', species='perro')

    def test_vet_can_create_appointment(self):
        self.auth_as(self.make_vet())
        response = self.client.post(
            '/appointments',
            {'pet_id': self.pet.id, 'date': '2026-09-20T10:00:00', 'reason': 'Control'},
            format='json',
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['status'], 'pendiente')

    def test_invalid_status_is_rejected(self):
        self.auth_as(self.make_vet())
        response = self.client.post(
            '/appointments',
            {
                'pet_id': self.pet.id,
                'date': '2026-09-20T10:00:00',
                'reason': 'Control',
                'status': 'no-existe',
            },
            format='json',
        )
        self.assertEqual(response.status_code, 400)

    def test_invalid_date_is_rejected(self):
        self.auth_as(self.make_vet())
        response = self.client.post(
            '/appointments',
            {'pet_id': self.pet.id, 'date': 'no-es-fecha', 'reason': 'Control'},
            format='json',
        )
        self.assertEqual(response.status_code, 400)

    def test_unknown_pet_id_is_rejected(self):
        self.auth_as(self.make_vet())
        response = self.client.post(
            '/appointments',
            {'pet_id': 999, 'date': '2026-09-20T10:00:00', 'reason': 'Control'},
            format='json',
        )
        self.assertEqual(response.status_code, 400)

    def test_client_role_cannot_create_appointment(self):
        _, user = self.make_client_with_user()
        self.auth_as(user)
        response = self.client.post(
            '/appointments',
            {'pet_id': self.pet.id, 'date': '2026-09-20T10:00:00', 'reason': 'Control'},
            format='json',
        )
        self.assertEqual(response.status_code, 403)

    def test_filter_by_status(self):
        Appointment.objects.create(pet=self.pet, date='2026-09-20T10:00:00', reason='A', status='pendiente')
        Appointment.objects.create(pet=self.pet, date='2026-09-21T10:00:00', reason='B', status='atendida')
        self.auth_as(self.make_admin())

        response = self.client.get('/appointments?status=atendida')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['reason'], 'B')

    def test_client_role_only_sees_appointments_of_own_pets(self):
        other_client = Client.objects.create(name='Otro')
        other_pet = Pet.objects.create(client=other_client, name='Ajena', species='gato')
        Appointment.objects.create(pet=other_pet, date='2026-09-20T10:00:00', reason='Ajena')

        owner, user = self.make_client_with_user()
        own_pet = Pet.objects.create(client=owner, name='Mia', species='perro')
        Appointment.objects.create(pet=own_pet, date='2026-09-20T10:00:00', reason='Mia')
        self.auth_as(user)

        response = self.client.get('/appointments')
        self.assertEqual(response.status_code, 200)
        reasons = [a['reason'] for a in response.data]
        self.assertEqual(reasons, ['Mia'])


class AppointmentDetailTests(BaseAPITestCase):
    def setUp(self):
        self.client_owner = Client.objects.create(name='Dueño')
        self.pet = Pet.objects.create(client=self.client_owner, name='Toby', species='perro')
        self.appointment = Appointment.objects.create(
            pet=self.pet, date='2026-09-20T10:00:00', reason='Control'
        )

    def test_client_role_cannot_view_others_appointment(self):
        _, user = self.make_client_with_user()
        self.auth_as(user)

        response = self.client.get(f'/appointments/{self.appointment.id}')
        self.assertEqual(response.status_code, 403)

    def test_admin_can_update_status(self):
        self.auth_as(self.make_admin())
        response = self.client.put(
            f'/appointments/{self.appointment.id}',
            {'status': 'atendida', 'diagnosis': 'Sano', 'treatment': 'Ninguno'},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.appointment.refresh_from_db()
        self.assertEqual(self.appointment.status, 'atendida')

    def test_only_admin_can_delete_appointment(self):
        self.auth_as(self.make_vet())
        response = self.client.delete(f'/appointments/{self.appointment.id}')
        self.assertEqual(response.status_code, 403)

    def test_deleting_pet_cascades_to_appointments(self):
        self.auth_as(self.make_admin())
        response = self.client.delete(f'/pets/{self.pet.id}')
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Appointment.objects.filter(id=self.appointment.id).exists())
