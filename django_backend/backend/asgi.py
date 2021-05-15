"""
ASGI config for backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""

# import os
#
# from django.core.asgi import get_asgi_application
#
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
#
# application = get_asgi_application()

# 在项目名同名的文件夹下创建routing.py文件并在该文件内提前写好以下代码
from channels.routing import ProtocolTypeRouter,URLRouter
from django.conf.urls import url
from BUAA import notification

application =ProtocolTypeRouter({
    'websocket':URLRouter([
        # websocket请求路由与视图函数的对应关系
      	url(r'^link/$',notification.ChatConsumer)
    ])
})
