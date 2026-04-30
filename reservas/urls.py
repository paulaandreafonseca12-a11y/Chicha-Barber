from django.urls import path
from . import views

urlpatterns = [
    # --- Gestión de Agenda (ADMIN) ---
    path('', views.ver_agenda, name='reservas_index'), 
    path('agenda/', views.ver_agenda, name='ver_agenda'),
    path('agenda/crear/', views.crear_reserva_admin, name='crear_reserva_admin'), # Este es el de tu botón
    path('cambiar-estado/<int:pk>/<str:nuevo_estado>/', views.cambiar_estado_reserva, name='cambiar_estado'),
    path('reprogramar/<int:pk>/', views.reprogramar_cita, name='reprogramar_cita'),
    path('cancelar/<int:pk>/', views.cancelar_cita, name='cancelar_cita'),

    # --- Gestión de Reservas (CLIENTES) ---
    # Usamos la misma función de tu views.py ajustada para recibir o no el ID
    path('crear/', views.crear_reserva, name='crear_reserva_directa'), 
    path('crear/<int:servicio_id>/', views.crear_reserva, name='crear_reserva'),

    
    # Agenda y Estados
    path('agenda/', views.ver_agenda, name='ver_agenda'),
    path('agenda/crear/', views.crear_reserva_admin, name='crear_reserva_admin'), # Este es el de tu botón
    path('cambiar-estado/<int:pk>/<str:nuevo_estado>/', views.cambiar_estado_reserva, name='cambiar_estado'),
    path('reprogramar/<int:pk>/', views.reprogramar_cita, name='reprogramar_cita'),
    path('cancelar/<int:pk>/', views.cancelar_cita, name='cancelar_cita'),

    # --- Gestión de Reservas (CLIENTES) ---
    # Usamos la misma función de tu views.py ajustada para recibir o no el ID
    path('crear/', views.crear_reserva, name='crear_reserva_directa'), 
    path('crear/<int:servicio_id>/', views.crear_reserva, name='crear_reserva'),

    # --- Calificaciones ---
    path('calificacion/', views.calificacion_view, name='calificacion'),
    path('calificacion/crear/', views.calificacion_view, name='crear_calificacion'),
    path('calificacion/editar/<int:pk>/', views.editar_calificacion, name='editar_calificacion'),
]