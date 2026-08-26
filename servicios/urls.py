from django.urls import path
from . import views


urlpatterns = [
    # Página principal → /servicios/
    path('', views.servicios, name='servicios'),

    # Crear servicio → /servicios/crear/
    path('crear/', views.crear_servicios, name='crear_servicios'),




    # Promociones → /servicios/promocion/
    
    # Seleccionar promoción
    path('editar/<int:pk>/', views.editar_servicios, name='editar-servicios'),
    path('eliminar/<int:pk>/', views.eliminar_servicios, name='eliminar-servicios'),
    path('listado/', views.listado_admin, name='listado-admin'),
    path('registro/<int:servicio_pk>/', views.registro, name='registro'),
    path('calificacion/', views.calificacion_view, name='calificacion'),
    path('calificacion/listado/', views.listado_calificacion, name='listado-calificacion'),
    path('calificacion/responder/<int:pk>/', views.responder_calificacion, name='responder-calificacion'),
    path('calificacion/enviar/', views.guardar_calificacion_view, name='enviar_calificacion'),
    path('calificacion/eliminar/<int:pk>/', views.eliminar_calificacion, name='eliminar_calificacion'),
    
   
    
    



   

    

    
]
