from django.urls import path
from . import views


app_name = 'chats'


urlpatterns = [
    path('', views.chat_main, name='chat_detail'),
    path('<int:chat_id>/', views.get_chat, name='get_chat'),
    path('<int:chat_id>/send/', views.send_message, name='send_message'),
    path('create/', views.chat_create, name='chat_create'),
]