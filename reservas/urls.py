from django.urls import path
from . import views

# Definimos app_name para usar namespaces (ej: 'reservas:crear_reserva')


urlpatterns = [
    path('', views.reservas_view, name='reservas'),
    path('calificacion/', views.calificacion_view, name='calificacion'),
    path('calificacion/crear/', views.calificacion_view, name='crear_calificacion'),
    path('cancelar/<int:pk>/', views.cancelar_cita, name='cancelar_cita'),
    path('agenda/', views.ver_agenda, name='ver_agenda'),
    path('crear/', views.crear_reserva, name='crear_reserva'),
    path('crear/<int:servicio_id>/', views.crear_reserva_user, name='crear_reserva'),  # ← nombre distinto
    path('cambiar-estado/<int:pk>/<str:nuevo_estado>/', views.cambiar_estado_reserva, name='cambiar_estado'),
    path('reprogramar/<int:pk>/', views.reprogramar_cita, name='reprogramar_cita'),
    # Gestión de reservas
    path('', views.ver_agenda, name='reservas_index'), # Cambiado para evitar conflicto
    path('agenda/crear/', views.crear_reserva_admin, name='crear_reserva_admin'), # Nombre directo
    path('crear/<int:servicio_id>/', views.crear_reserva, name='crear_reserva'),

    
    # Agenda y Estados
    path('agenda/', views.ver_agenda, name='ver_agenda'),
    path('cancelar/<int:pk>/', views.cancelar_cita, name='cancelar_cita'),
    path('reprogramar/<int:pk>/', views.reprogramar_cita, name='reprogramar_cita'),
    path('cambiar-estado/<int:pk>/<str:nuevo_estado>/', views.cambiar_estado_reserva, name='cambiar_estado'),
    
    
    # Calificaciones
    path('calificacion/', views.calificacion_view, name='calificacion'),
    path('calificacion/editar/<int:pk>/', views.editar_calificacion, name='editar_calificacion'),
]