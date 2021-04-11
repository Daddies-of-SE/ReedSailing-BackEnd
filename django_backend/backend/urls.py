"""backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from BUAA.views import *
from django.conf.urls import url
from rest_framework.documentation import include_docs_urls
from rest_framework.routers import SimpleRouter

urlpatterns = [
    path('admin/', admin.site.urls),
    path('sendVerify/', send_email),
    path('verify/', verify_email),
    path('login/', code2Session),
    url(r'^docs/', include_docs_urls(title='一苇以航API接口')),
]

router = SimpleRouter()
router.register('organizations', OrganizationModelViewSet)
router.register('users', WXUserViewSet)
router.register('categories', CategoryViewSet)
router.register('addresses', AddressViewSet)
router.register('comments', CommentViewSet)
router.register('blocks', BlockViewSet)
router.register('feedbacks', UserFeedbackViewSet)
router.register('organizations/applications', OrgApplicationViewSet)
router.register('activities', ActivityViewSet)
router.register('organizations/managers', OrgMangerViewSet)
router.register('organizations/followers', FollowedOrgViewSet)
router.register('activities/join_applications', JoinActApplicationViewSet)
router.register('activities/participants', JoinedActViewSet)
urlpatterns += router.urls


