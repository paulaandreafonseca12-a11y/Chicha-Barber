from django.urls import path
from . import views

urlpatterns = [
    path('carrusel/', views.carrusel_view, name='carrusel'),
    path('carrusel/crear/', views.crear_carrusel, name='crear_carrusel'),
    path('carrusel/editar/<int:pk>/', views.editar_carrusel, name='editar_carrusel'),
    path('carrusel/eliminar/<int:pk>/', views.eliminar_carrusel, name='eliminar_carrusel'),
    path('carrusel/toggle/<int:pk>/', views.toggle_carrusel, name='toggle_carrusel'),
]