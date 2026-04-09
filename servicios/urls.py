
from django.urls import path
from . import views

app_name = 'servicios' 

urlpatterns = [
    path('', views.servicios_view, name='servicios'),
    path('servicios/', views.servicios_view, name='servicios'),  
    path('servicios/crear/', views.crear_servicios, name='crear_servicios'),
    path('calificacion/', views.calificacion_views, name='calificacion'),
    path('promocion/', views.promocion, name='promocion'),  # ← era promocion_views, es promocion
    path('promocion/seleccionar/<str:nombre_promo>/', views.seleccionar_promocion, name='seleccionar_promocion'),
]
    