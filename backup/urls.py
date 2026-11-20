from django.urls import path

from .backup import backup, restaurar_datos


urlpatterns = [
    path('', backup, name='backup'),
    path('restaurar/', restaurar_datos, name='restaurar_datos'),
]
