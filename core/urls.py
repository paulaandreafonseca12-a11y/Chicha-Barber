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
