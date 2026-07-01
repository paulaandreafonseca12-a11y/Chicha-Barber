from django.urls import path
from . import views

urlpatterns = [
    path('', views.vista_chat_ia, name='chat_ia'),
]