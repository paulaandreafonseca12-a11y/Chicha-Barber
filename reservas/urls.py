# C:\Users\Natalia\Documents\GitHub\Django.py\reservas\urls.py
from django.urls import path
from . import views


urlpatterns = [
    # --- GESTIÓN DE AGENDA (ADMIN) ---
    path('agenda/', views.ver_agenda, name='ver_agenda'),
    path('agenda/crear/', views.crear_reserva_admin, name='crear_reserva_admin'),
    path('reprogramar/<int:pk>/', views.reprogramar_cita, name='reprogramar_cita'),
    path('cancelar/<int:pk>/', views.cancelar_cita, name='cancelar_cita'),

    # --- GESTIÓN DE RESERVAS (CLIENTES) ---
    path('crear/', views.crear_reserva, {'servicio_id': None}, name='crear_reserva_directa'), 
    path('crear/<int:servicio_id>/', views.crear_reserva, name='crear_reserva'),

    # --- CALIFICACIONES (CLIENTES) ---
    # Esta es la página con las estrellas para el cliente
    path('calificacion/', views.calificacion_view, name='calificacion'),

    # --- CALIFICACIONES (ADMIN) ---
    # Esta es la ruta que corregirá tu primera imagen (la tabla de administración)
    path('calificacion/listado/', views.listado_calificaciones_admin, name='listado_calificaciones_admin'),
    
    #calendario
    
    path(
    'api/disponibilidad/', 
    views.obtener_disponibilidad_json, 
    name='api_disponibilidad'
   ),
    # Edición (si la necesitas)
    path('calificacion/editar/<int:pk>/', views.editar_calificacion, name='editar_calificacion'),
]