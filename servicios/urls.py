
from django.urls import path
from . import views


urlpatterns = [
    path('', views.servicios_view, name='servicios'),
    path('servicios/', views.servicios_view, name='servicios'),  
    path('panel/servicios/', views.servicios_admin_view, name='servicios'),  
    path('servicios/crear/', views.crear_servicios, name='crear-servicios'),
    path('calificacion/', views.calificacion_views, name='calificacion'),
    path('promocion/', views.promocion, name='promocion'),  # ← era promocion_views, es promocion
    path('promocion/crear/', views.crear_promocion, name='crear-promocion'),
    path('promocion/seleccionar/<str:nombre_promo>/', views.seleccionar_promocion, name='seleccionar_promocion'),
    path('panel/listado/', views.listado, name='listado'),
    path('panel/listado/promocion/', views.promocion, name='listado-promocion')

    ]
    