"""
ASGI config for backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""

# 在项目名同名的文件夹下创建routing.py文件并在该文件内提前写好以下代码
from django.urls import path
from django.urls import re_path as url
from channels.auth import AuthMiddlewareStack  # channels的认证中间件
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from BUAA import notification


application = ProtocolTypeRouter({

    'websocket' : AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter([
                url(r'^ws/link/(?P<user_id>\d+)/$', notification.NotificationConsumer),

                # url(r'^ws/link/1/$', notification.NotificationConsumer),
            ])
        )
    )
})