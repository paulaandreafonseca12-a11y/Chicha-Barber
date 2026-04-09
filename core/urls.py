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
from django.contrib import admin
from django.urls import include, path
from django.contrib.auth import views as auth_views
from core.views import inicio, inicio_admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', inicio, name='inicio'),
    
    # --- APPS DEL PROYECTO ---
    path('servicios/', include('servicios.urls')),
    path('reservas/', include('reservas.urls')),  # Solo el include aquí
    path('usuarios/', include('usuarios.urls')),
    path('productos/', include('productos.urls')),
    
    path('panel/', inicio_admin, name='inicio_admin'),
    # ... resto de tus urls

    # --- AUTENTICACIÓN Y PASSWORD RESET ---
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('recuperar-password/', auth_views.PasswordResetView.as_view(template_name='registration/recuperar.html'), name='password_reset'),
    path('recuperar-password/enviado/', auth_views.PasswordResetDoneView.as_view(template_name='registration/recuperar_enviado.html'), name='password_reset_done'),
    path('recuperar/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/recuperar_confirmar.html'), name='password_reset_confirm'),
    path('recuperar/completo/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/recuperar_completo.html'), name='password_reset_complete'),
]