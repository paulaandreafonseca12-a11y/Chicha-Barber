from django.urls import path
from . import views

# EL ERROR: Cambia 'pathpatterns' por 'urlpatterns'
urlpatterns = [
    path('carrusel/', views.carrusel_view, name='carrusel'),
]
    