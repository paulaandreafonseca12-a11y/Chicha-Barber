from django.urls import path
from . import views

urlpatterns = [
    path('carrusel/', views.carrusel_view, name='carrusel'),
    path('carrusel/crear/', views.crear_carrusel, name='crear_carrusel'),
]