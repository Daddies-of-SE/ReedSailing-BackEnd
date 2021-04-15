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
    # path('admin/', admin.site.urls),
    # 用户端
    path('sendVerify/', send_email),
    path('verify/', verify_email),
    path('login/', code2Session),
    url(r'^docs/', include_docs_urls(title='一苇以航API接口')),

    url(r'^blocks/orgs/(?P<pk>.*)/$', BlockOrgsViewSet.as_view()),

    url(r'^organizations/managers/$', OrgMangerViewSet.as_view()),
    url(r'^organizations/managers/(?P<pk>.*)$', OrgMangerViewSet.as_view()),
    # url(r'^users/$', WXUserViewSet.as_view()),
    # url(r'^users/(\?id\=.*)$', WXUserViewSet.as_view()),
    url(r'^users/organizations/$',OrgMangerViewSet.as_view()),

    # 版块
    url(r'^blocks/$', BlockViewSet.as_view({"get": "list", "post": "create"})),
    url(r'^blocks/(?P<pk>\d+)/$', BlockViewSet.as_view({"put": "update", "delete": "destroy"})),

    # 用户
    url(r'^users/$', WXUserViewSet.as_view({"get": "list"})),
    url(r'^users/(?P<pk>\d+)/$', WXUserViewSet.as_view({"get": "retrieve", "delete": "destroy", "put": "update"})),

    # 组织申请
    url(r'^organizations/applications/$', OrgApplicationViewSet.as_view({"post": "create", "get": "list"})),
    url(r'^organizations/applications/(?P<pk>\d+)/$', OrgApplicationViewSet.as_view({"delete": "destroy"})),
    url(r'^users/organizations/applications/(?P<user_id>\d+)/$', OrgApplicationViewSet.as_view({"get": "user_get_all"})),
    url(r'^organizations/applications/verifications/(?P<pk>\d+)/$', OrgApplicationViewSet.as_view({"put": "verify"})),

    # 组织
    url(r'^organizations/$', OrganizationModelViewSet.as_view({"post": "create"})),
    url(r'^organizations/(?P<pk>\d+)/$', OrganizationModelViewSet.as_view({"get": "retrieve", "put": "update", "delete": "destroy"})),
    url(r'^blocks/organizations/(?P<block_id>\d+)/$', OrganizationModelViewSet.as_view({"get": "get_org_by_block"})),

    # 关注组织
    url(r'^users/followed_organizations/$', FollowedOrgViewSet.as_view({"post": "create", "delete": "destroy"})),
    url(r'^users/followed_organizations/(?P<pk>\d+)/$', FollowedOrgViewSet.as_view({"get": "get_followed_org_by_user"})),
    # 测试使用
    url(r'^test/users/$', WXUserViewSet.as_view({"post": "create"})),
]

router = SimpleRouter()
# router.register('organizations', OrganizationModelViewSet)

router.register('categories', CategoryViewSet)
router.register('addresses', AddressViewSet)
router.register('comments', CommentViewSet)
router.register('feedbacks', UserFeedbackViewSet)
router.register('activities', ActivityViewSet)
# router.register('organizations/managers', OrgMangerViewSet)
router.register('organizations/followers', FollowedOrgViewSet)
router.register('activities/join_applications', JoinActApplicationViewSet)
router.register('activities/participants', JoinedActViewSet)

urlpatterns += router.urls


