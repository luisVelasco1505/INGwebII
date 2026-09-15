from rest_framework.response import Response
from rest_framework import status


def bad_request(message):
    return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)


def not_found(message='Recurso no encontrado'):
    return Response({'error': message}, status=status.HTTP_404_NOT_FOUND)


def forbidden(message='No tenés permisos para realizar esta acción'):
    return Response({'error': message}, status=status.HTTP_403_FORBIDDEN)
