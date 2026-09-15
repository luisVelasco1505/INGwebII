from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models

ROLES = (
    ('admin', 'admin'),
    ('vet', 'vet'),
    ('client', 'client'),
)

SPECIES = (
    ('perro', 'perro'),
    ('gato', 'gato'),
    ('otro', 'otro'),
)

APPOINTMENT_STATUSES = (
    ('pendiente', 'pendiente'),
    ('atendida', 'atendida'),
    ('cancelada', 'cancelada'),
)


class Client(models.Model):
    name = models.CharField(max_length=120)
    email = models.CharField(max_length=120, null=True, blank=True)
    phone = models.CharField(max_length=30, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'created_at': self.created_at.isoformat(),
        }


class Pet(models.Model):
    client = models.ForeignKey(Client, related_name='pets', on_delete=models.CASCADE)
    name = models.CharField(max_length=120)
    species = models.CharField(max_length=20, choices=SPECIES)
    breed = models.CharField(max_length=120, null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def to_dict(self):
        return {
            'id': self.id,
            'client_id': self.client_id,
            'name': self.name,
            'species': self.species,
            'breed': self.breed,
            'age': self.age,
            'weight': self.weight,
            'created_at': self.created_at.isoformat(),
        }


class Appointment(models.Model):
    pet = models.ForeignKey(Pet, related_name='appointments', on_delete=models.CASCADE)
    date = models.DateTimeField()
    reason = models.CharField(max_length=255)
    diagnosis = models.TextField(null=True, blank=True)
    treatment = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=APPOINTMENT_STATUSES, default='pendiente')
    created_at = models.DateTimeField(auto_now_add=True)

    def to_dict(self):
        return {
            'id': self.id,
            'pet_id': self.pet_id,
            'date': self.date.isoformat(),
            'reason': self.reason,
            'diagnosis': self.diagnosis,
            'treatment': self.treatment,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
        }


class UserManager(BaseUserManager):
    def create_user(self, email, name, password, role='vet', client=None):
        if not email:
            raise ValueError('El email es obligatorio')
        user = self.model(email=self.normalize_email(email), name=name, role=role, client=client)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password):
        return self.create_user(email, name, password, role='admin')


class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=120)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLES, default='vet')
    client = models.OneToOneField(
        Client, related_name='user', on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'client_id': self.client_id,
            'created_at': self.created_at.isoformat(),
        }
