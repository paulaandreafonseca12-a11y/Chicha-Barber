from django.urls import path
from . import views


urlpatterns = [
    # Página principal → /servicios/
    path('', views.servicios, name='servicios'),

    # Crear servicio → /servicios/crear/
    path('crear/', views.crear_servicios, name='crear_servicios'),

    # Calificación → /servicios/calificacion/


    # Promociones → /servicios/promocion/
    path('promocion/', views.promocion, name='promocion'),
    
    path('crear-promocion/', views.crear_promocion, name='crear_promocion'),

    # Seleccionar promoción
    path('editar/<int:pk>/', views.editar_servicios, name='editar-servicios'),
    path('eliminar/<int:pk>/', views.eliminar_servicios, name='eliminar-servicios'),
    path('listado/', views.listado_admin, name='listado-admin'),
    path('promocion/listado/', views.listado_promocion, name='listado-promocion'),
    path('promocion/editar/<int:pk>/', views.editar_promocion, name='editar-promocion'),
    path('promocion/eliminar/<int:pk>/', views.eliminar_promocion, name='eliminar-promocion'),
    path('calificacion/listado/', views.listado_calificacion, name='listado_calificacion'),
]
