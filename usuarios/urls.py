"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# usuarios/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Inicio / Registro
    path('registro/', views.registro_view, name='registro'),

    # LOGIN: Usamos la vista integrada de Django para evitar errores
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    
    # LOGOUT: También es importante tenerlo
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # LISTA UNIFICADA: Esta reemplaza a 'clientes' y 'barberos'
    path('lista/', views.lista_usuarios, name='lista_usuarios'),
    path('crear/', views.crear_usuario_admin, name='crear_usuario'),
    path('editar/<int:pk>/', views.editar_usuario, name='editar_usuario'),
]