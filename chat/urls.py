from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('chat/<int:character_id>/', views.chat_page, name='chat_page'),
    path('api/chat/<int:character_id>/', views.chat_api, name='chat_api'),
]
