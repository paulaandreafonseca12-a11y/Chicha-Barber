from django.urls import path
from . import views

urlpatterns = [
    # =========================
    # 📥 ADQUISICIONES / COMPRAS
    # =========================
    path('', views.lista_adquisiciones, name='lista_adquisiciones'),
    path('adquisicion/crear/', views.registrar_adquisicion, name='registrar_adquisicion'),
    path('adquisicion/editar/<int:pk>/', views.editar_adquisicion, name='editar_adquisicion'),
    path('adquisicion/eliminar/<int:pk>/', views.eliminar_adquisicion, name='eliminar_adquisicion'),

    # Rutas alias para compatibilidad
    path('compras/', views.lista_adquisiciones, name='lista_compras'),
    path('compras/crear/', views.registrar_adquisicion, name='crear_compra'),
    path('compras/editar/<int:pk>/', views.editar_adquisicion, name='editar_compra'),
    path('compras/eliminar/<int:pk>/', views.eliminar_adquisicion, name='eliminar_compra'),
]
