# C:\Users\Natalia\Documents\GitHub\Django.py\reservas\urls.py
from django.urls import path
from . import views


urlpatterns = [
    # --- GESTIÓN DE AGENDA (ADMIN) ---
    path('agenda/', views.ver_agenda, name='ver_agenda'),
    path('agenda/crear/', views.crear_reserva_admin, name='crear_reserva_admin'),
    path('reprogramar/<int:pk>/', views.reprogramar_cita, name='reprogramar_cita'),
    path('cancelar/<int:pk>/', views.cancelar_cita, name='cancelar_cita'),
    path('estado/<int:pk>/<str:nuevo_estado>/', views.cambiar_estado_reserva, name='cambiar_estado'),
    
    # --- GESTIÓN DE DISPONIBILIDAD (ADMIN) ---
    path('gestion-dias/', views.gestionar_disponibilidad_dias, name='gestionar_dias'),
    path('gestion-dias/activar/<str:fecha_str>/', views.activar_dia_agenda, name='activar_dia'),
    path('gestion-dias/desactivar/<str:fecha_str>/', views.desactivar_dia_agenda, name='desactivar_dia'),

    # --- GESTIÓN DE RESERVAS (CLIENTES) ---
    path('crear/', views.crear_reserva, {'servicio_id': None}, name='crear_reserva_directa'),
    path('crear/promocion/<int:promocion_id>/', views.crear_reserva, name='crear_reserva_promocion'),
    path('crear/<int:servicio_id>/', views.crear_reserva, name='crear_reserva'),

    # --- CALIFICACIONES (CLIENTES) ---
    # Esta es la página con las estrellas para el cliente
    

    
    
    #calendario
    
    path(
    'api/disponibilidad/',
    views.obtener_turnos_disponibles_json,
    name='api_turnos_disponibles'
   ),

]