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
from usuarios import views 
from django.contrib import admin # type: ignore
from django.urls import include, path # type: ignore
from django.contrib.auth import views as auth_views
from usuarios.views import inicio 
from usuarios.forms import RegistroForm 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', inicio, name='inicio'),
    path ('servicios/', include('servicios.urls')),
    path('reservas/', include('reservas.urls')),
    path('usuarios/', include('usuarios.urls')),  
      
    
    
    path('', include('productos.urls')),
    # urls.py (Carpeta principal del proyecto)
    path('', views.inicio, name='index'), 

    path('usuarios/', include('usuarios.urls')),
    


    # --- RUTAS DE AUTENTICACIÓN ---
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # 1. Formulario para pedir el cambio (El que ya tienes con fondo de barbería)
    path('recuperar-password/', 
         auth_views.PasswordResetView.as_view(template_name='registration/recuperar.html'), 
         name='password_reset'),

    # 2. Pantalla que dice "Revisa tu correo"
    path('recuperar-password/enviado/', 
         auth_views.PasswordResetDoneView.as_view(template_name='registration/recuperar_enviado.html'), 
         name='password_reset_done'),

    # 3. El link que llega al correo (ESTA ES LA QUE TE DABA EL ERROR)
    path('recuperar/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='registration/recuperar_confirmar.html'), 
         name='password_reset_confirm'),

    # 4. Pantalla de "¡Listo! Contraseña cambiada"
    path('recuperar/completo/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='registration/recuperar_completo.html'), 
         name='password_reset_complete'),
    
]