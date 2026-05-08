# C:\Users\Natalia\Documents\GitHub\Django.py\reservas\urls.py
from django.urls import path
from . import views

urlpatterns = [

    # =========================
    # 🔧 ADMIN
    # =========================

    path('', views.ver_agenda, name='reservas_index'),

    path(
        'agenda/',
        views.ver_agenda,
        name='ver_agenda'
    ),

    path(
        'agenda/crear/',
        views.crear_reserva_admin,
        name='crear_reserva_admin'
    ),

    path(
        'cambiar-estado/<int:pk>/<str:nuevo_estado>/',
        views.cambiar_estado_reserva,
        name='cambiar_estado'
    ),

    path(
        'reprogramar/<int:pk>/',
        views.reprogramar_cita,
        name='reprogramar_cita'
    ),

    path(
        'cancelar/<int:pk>/',
        views.cancelar_cita,
        name='cancelar_cita'
    ),

    # =========================
    # 👤 CLIENTES
    # =========================

    path(
        'crear/<int:servicio_id>/',
        views.crear_reserva,
        name='crear_reserva'
    ),

    # =========================
    # ⭐ CALIFICACIONES
    # =========================

    path(
        'calificacion/',
        views.calificacion_view,
        name='calificacion'
    ),

    path(
        'calificacion/editar/<int:pk>/',
        views.editar_calificacion,
        name='editar_calificacion'
    ),
    
    #calendario
    
    path(
    'api/disponibilidad/', 
    views.obtener_disponibilidad_json, 
    name='api_disponibilidad'
   ),
]