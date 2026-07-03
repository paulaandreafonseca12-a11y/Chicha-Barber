from django.urls import path
from . import views


urlpatterns = [
    path('', views.ayuda_home, name='ayuda_home'),
    path('nuevo-ticket/', views.crear_ticket, name='crear_ticket'),
]