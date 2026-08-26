from django.urls import path
from . import views

urlpatterns = [
    # =========================
    # 📜 BITÁCORA
    # =========================
    path('bitacora/', views.lista_bitacora, name='lista_bitacora'),
    path('bitacora/editar/<int:pk>/', views.editar_bitacora, name='editar_bitacora'),
]
