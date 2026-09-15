from django.urls import path

from clinic.views import appointments, auth, clients, docs, health, pets

urlpatterns = [
    path('health', health.health),
    path('auth/register', auth.register),
    path('auth/register-client', auth.register_client),
    path('auth/login', auth.login),
    path('clients', clients.client_list),
    path('clients/<int:client_id>', clients.client_detail),
    path('pets', pets.pet_list),
    path('pets/<int:pet_id>', pets.pet_detail),
    path('appointments', appointments.appointment_list),
    path('appointments/<int:appointment_id>', appointments.appointment_detail),
    path('openapi.yaml', docs.openapi_spec),
    path('docs/', docs.swagger_ui),
]
