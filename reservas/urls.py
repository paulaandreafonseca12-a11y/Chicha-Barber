"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views

app_name = 'reservas'

urlpatterns = [
    # Ahora la página principal de reservas SÍ procesa el guardado
    path('', views.reservas_view, name='reservas'),
    path('calificacion/', views.calificacion_view, name='calificacion'),
    path('cancelar/<int:pk>/', views.cancelar_cita, name='cancelar_cita'),
    path('ver-agenda/', views.ver_agenda, name='ver_agenda'),
    path('crear/', views.crear_reserva, name='crear_reserva'),
    path('cambiar-estado/<int:pk>/<str:nuevo_estado>/', views.cambiar_estado_reserva, name='cambiar_estado'),
    path('reprogramar/<int:pk>/', views.reprogramar_cita, name='reprogramar_cita'),
]
