"""
ASGI config for MIRROR project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

#redis-server   Запустите Redis в отдельном терминале
#python manage.py runserver   Запустите Django сервер

import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MIRROR.settings')
# $env:DJANGO_SETTINGS_MODULE="MIRROR.settings"
# daphne MIRROR.asgi:application <------------- Для запуска приложения
# Проверка:
# echo $env:DJANGO_SETTINGS_MODULE должно вывести -> MIRROR.settings

django.setup()  # ⬅⬅⬅ ДО импорта модулей с моделями и т.п.

import chats.routing  # ⬅ только после django.setup()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            chats.routing.websocket_urlpatterns
        )
    ),
})
