
from django.contrib import admin # type: ignore
from django.urls import include, path # type: ignore

from core.views import inicio, inicio_admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', inicio, name='inicio'),
    path ('servicios/', include('servicios.urls')),
    path('reservas/', include('reservas.urls')),
    path('usuarios/', include('usuarios.urls')),  
    path('panel/', inicio_admin, name='inicio_admin'),
    path('productos/', include('productos.urls')), 
    
    
]
