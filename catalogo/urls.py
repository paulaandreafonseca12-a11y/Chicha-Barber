
from django.urls import path
from . import views



path('promocion/', views.promocion, name='promocion'),
    
path('crear-promocion/', views.crear_promocion, name='crear_promocion'),

path('promocion/listado/', views.listado_promocion, name='listado-promocion'),
path('promocion/editar/<int:pk>/', views.editar_promocion, name='editar-promocion'),
path('promocion/eliminar/<int:pk>/', views.eliminar_promocion, name='eliminar-promocion'),