from django.urls import path
from . import views

urlpatterns = [
    # --- GESTIÓN DE SERVICIOS ---
    # Página principal → /servicios/
    path('', views.servicios_view, name='servicios'),
    
    # Listado para administración
    path('listado/', views.listado_admin, name='listado-admin'),
    
    # Crear, Editar y Eliminar servicios
    path('crear/', views.crear_servicios, name='crear_servicios'),
    path('editar/<int:pk>/', views.editar_servicios, name='editar-servicios'),
    path('eliminar/<int:pk>/', views.eliminar_servicios, name='eliminar-servicios'),


    # --- CALIFICACIONES ---
    # Esta es la ruta que faltaba y causaba el error en el aside
    path('calificacion/', views.calificacion_view, name='calificacion'),


    # --- PROMOCIONES ---
    # Vistas principales de promociones
    path('promocion/', views.promocion, name='promocion'),
    path('promocion/listado/', views.listado_promocion, name='listado-promocion'),
    
    # Crear, Editar y Eliminar promociones
    path('crear-promocion/', views.crear_promocion, name='crear_promocion'),
    path('promocion/editar/<int:pk>/', views.editar_promocion, name='editar-promocion'),
    path('promocion/eliminar/<int:pk>/', views.eliminar_promocion, name='eliminar-promocion'),
]