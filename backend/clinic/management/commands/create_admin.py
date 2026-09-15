import getpass

from django.core.management.base import BaseCommand

from clinic.models import User


class Command(BaseCommand):
    help = 'Crea un usuario con rol admin.'

    def add_arguments(self, parser):
        parser.add_argument('--name', default=None)
        parser.add_argument('--email', default=None)
        parser.add_argument('--password', default=None)

    def handle(self, *args, **options):
        name = options['name'] or input('Name: ')
        email = (options['email'] or input('Email: ')).strip().lower()
        password = options['password'] or getpass.getpass('Password: ')

        if User.objects.filter(email=email).exists():
            self.stdout.write(f'Ya existe un usuario con el email {email}')
            return

        User.objects.create_user(email=email, name=name, password=password, role='admin')
        self.stdout.write(self.style.SUCCESS(f'Admin "{email}" creado correctamente.'))
