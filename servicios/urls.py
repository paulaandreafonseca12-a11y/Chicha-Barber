from django.urls import path
from . import views

app_name = 'servicios'

urlpatterns = [
    # Página principal → /servicios/
    path('', views.servicios_view, name='servicios'),

    # Crear servicio → /servicios/crear/
    path('crear/', views.crear_servicios, name='crear_servicios'),

    # Calificación → /servicios/calificacion/
    path('calificacion/', views.calificacion_views, name='calificacion'),

    # Promociones → /servicios/promocion/
    path('promocion/', views.promocion, name='promocion'),
    
    path('crear-promocion/', views.crear_promocion, name='crear_promocion'),

    # Seleccionar promoción
    path(
        'promocion/seleccionar/<str:nombre_promo>/',
        views.seleccionar_promocion,
        name='seleccionar_promocion'
    ),
]
