
from django.contrib import admin # type: ignore
from django.urls import include, path # type: ignore

from . import views

urlpatterns = [
    path('', views.servicios_view, name='servicios'),
    path('servicios/crear/',views.crear_servicios, name='crear_servicios'),
    path('calificacion/', views.calificacion_views, name='calificacion'),
    path('promocion/', views.promocion_views, name='promocion'),
    
]




