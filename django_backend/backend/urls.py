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
from django.urls import path, include
from BUAA.views import *
from BUAA.superUser import *
from django.urls import re_path as url
from rest_framework.documentation import include_docs_urls
from rest_framework.routers import SimpleRouter

urlpatterns = [
    path('api/', include([
        path('admin/', admin.site.urls),
        path('rank/', lines), 
        # 用户端
        path('sendVerify/', send_email),
        path('verify/', verify_email),
        path('userLogin/', user_login),
        path('userRegister/', user_register),
        path('adminLogIn/', sudo_login),
        path('register/', sudo_register),
        path('userOrgRelation/', user_org_relation),
        path('userActRelation/', user_act_relation),
        path('qrcode/', get_page_qrcode),
#        path('boyaFollowers/', get_boya_followers),

        # 管理端
        path('identify/', web_token_identify),

        # 自动生成接口文档
        url(r'^docs/', include_docs_urls(title='一苇以航API接口')),

        # 版块
        url(r'^blocks/$',
            BlockViewSet.as_view({"get": "list", "post": "create"})),
        url(r'^blocks/(?P<pk>\d+)/$',
            BlockViewSet.as_view({"get": "retrieve", "put": "update", "delete": "destroy"})),

        # 用户
        url(r'^users/$', WXUserViewSet.as_view({"get": "list"})),
        url(r'^users/(?P<pk>\d+)/$', WXUserViewSet.as_view(
            {"get": "retrieve", "delete": "destroy", "put": "update"})),
        url(r'^users/boya_followers/', WXUserViewSet.as_view({"get": "get_boya_followers"})),
        url(r'^users/search/$',WXUserViewSet.as_view({"get": "search_user"})),
        

        # 组织申请
        url(r'^organizations/applications/$',
            OrgApplicationViewSet.as_view({"post": "create", "get": "list"})),
        url(r'^organizations/applications/(?P<pk>\d+)/$',
            OrgApplicationViewSet.as_view({"delete": "destroy", "get": "retrieve"})),
        # url(r'^users/organizations/applications/(?P<user_id>\d+)/$',
        #     OrgApplicationViewSet.as_view({"get": "user_get_all"})),
        url(r'^organizations/applications/verifications/(?P<pk>\d+)/$',
            OrgApplicationViewSet.as_view({"put": "verify"})),

        # 组织
        url(r'^organizations/$',
            OrganizationModelViewSet.as_view({"post": "create", "get": "list"})),
        url(r'^organizations/(?P<pk>\d+)/$', OrganizationModelViewSet.as_view(
            {"get": "retrieve", "put": "update", "delete": "destroy"})),
        url(r'^blocks/organizations/(?P<block_id>\d+)/$',
            OrganizationModelViewSet.as_view({"get": "get_org_by_block"})),
        url(r'^organizations/owner/(?P<pk>\d+)/$',
            OrganizationModelViewSet.as_view({"post": "change_org_owner"})),
        url(r'^organizations/search/$',
            OrganizationModelViewSet.as_view({"post":"search_all"})),
        url(r'^blocks/organizations/search/(?P<block_id>\d+)/$',
            OrganizationModelViewSet.as_view({"post": "search_org_by_block"})),

        # 关注组织
        url(r'^users/followed_organizations/$',
            FollowedOrgViewSet.as_view({"post": "create", "delete": "destroy"})),
        url(r'^users/followed_organizations/(?P<pk>\d+)/$',
            FollowedOrgViewSet.as_view({"get": "get_followed_org"})),

        # 组织管理
        url(r'^organizations/managers/$',
            OrgManageViewSet.as_view({"post": "create_wrapper", "delete": "destroy", })),
        url(r'^organizations/managers/(?P<pk>\d+)/$',
            OrgManageViewSet.as_view({"get": "get_all_managers"})),
        url(r'^users/managed_organizations/(?P<pk>\d+)/$',
            OrgManageViewSet.as_view({"get": "get_managed_org"})),
        url(r'^users/managed_organizations/search/(?P<pk>\d+)/$',
            OrgManageViewSet.as_view({"post": "search_managed_org"})),

        # 活动分类
        url(r'^activities/categories/$',
            CategoryViewSet.as_view({"get": "list", "post": "create"})),
        url(r'^activities/categories/(?P<pk>\d+)/$',
            CategoryViewSet.as_view({"put": "update", "delete": "destroy"})),

        # 活动地址
        url(r'^activities/addresses/$',
            AddressViewSet.as_view({"get": "list", "post": "create"})),
        url(r'^activities/addresses/(?P<pk>\d+)/$',
            AddressViewSet.as_view({"put": "update", "delete": "destroy"})),

        # 用户反馈
        url(r'^feedbacks/$',
            UserFeedbackViewSet.as_view({"get": "list", "post": "create"})),
        url(r'^feedbacks/(?P<pk>\d+)/$',
            UserFeedbackViewSet.as_view({"get": "retrieve", "delete": "destroy"})),
        url(r'^feedbacks/search/$',
            UserFeedbackViewSet.as_view({"get":"search_all_feedback"})),
        url(r'^feedbacks/user/(?P<user_id>\d+)/search/$',
            UserFeedbackViewSet.as_view({"get":"search_user_feedback"})),

        # 活动
        url(r'^activities/$',
            ActivityViewSet.as_view({"post": "create", "get": "list"})),
        url(r'^activities/(?P<pk>\d+)/$', ActivityViewSet.as_view(
            {"get": "retrieve", "delete": "destroy_wrapper", "put": "update_wrapper"})),
#         url(r'^activities/(?P<pk>\d+)/$', ActivityViewSet.as_view(
#             {"get": "retrieve", "delete": "destroy", "put": "update"})),
        url(r'^activities/search/$',
            ActivityViewSet.as_view({"post":"search_all"})),
        
        url(r'^organizations/activities/(?P<org_id>\d+)/$',
            ActivityViewSet.as_view({"get": "get_org_act"})),
        url(r'^organizations/activities/search/(?P<org_id>\d+)/$',
            ActivityViewSet.as_view({"post": "search_act_by_org"})),

        url(r'^users/released_activities/(?P<user_id>\d+)/$',
            ActivityViewSet.as_view({"get": "get_user_act"})),
        url(r'^users/released_activities/search/(?P<user_id>\d+)/$',
            ActivityViewSet.as_view({"post": "search_user_released_act"})),

        url(r'^blocks/activities/(?P<block_id>\d+)/$',
            ActivityViewSet.as_view({"get": "get_block_act"})),
        url(r'^blocks/activities/search/(?P<block_id>\d+)/$',
           ActivityViewSet.as_view({"post": "search_act_by_block"})),

        # 活动参与
        url(r'activities/participants/$',
            JoinedActViewSet.as_view({"post": "create", "delete": "destroy_wrapper"})),
        url(r'activities/(?P<act_id>\d+)/participants/$',
            JoinedActViewSet.as_view({"get": "get_act_participants"})),
        url(r'users/joined_acts/(?P<user_id>\d+)/$',
            JoinedActViewSet.as_view({"get": "get_user_joined_act"})),
        url(r'users/joined_acts/search/(?P<user_id>\d+)/$',
            JoinedActViewSet.as_view({"post": "search_user_joined_act"})),
        url(r'activities/joined_numbers/(?P<act_id>\d+)/$',
            JoinedActViewSet.as_view({"get": "get_act_participants_number"})),
        url(r'users/joined_acts/(?P<user_id>\d+)/(?P<year>\d+)/(?P<month>\d+)/$',
            JoinedActViewSet.as_view({"get": "get_user_joined_act_begin_order"})),

        # 活动评论
        url(r'activities/comments/$',
            CommentViewSet.as_view({"get": "list", "post": "create_wrapper"})),
        url(r'activities/(?P<act_id>\d+)/comments/$',
            CommentViewSet.as_view({"get": "get_act_comments"})),
        url(r'activities/(?P<act_id>\d+)/users/(?P<user_id>\d+)/comments',
            CommentViewSet.as_view({"get": "get_user_comment"})),
        url(r'activities/comments/(?P<pk>\d+)/$', CommentViewSet.as_view(
            {"delete": "destroy", "put": "update_wrapper", "get": "retrieve"})),
        url(r'activities/comments/search/$',
            CommentViewSet.as_view({"get":"search_all_comment"})),
        url(r'activities/(?P<act_id>\d+)/comments/search/$',
            CommentViewSet.as_view({"get":"search_by_act"})),
        url(r'activities/users/(?P<user_id>\d+)/comments/search/$',
            CommentViewSet.as_view({"get":"search_by_user"})),

        # 个性化推荐
        url(r'recommended/activities/(?P<user_id>\d+)/$',
            ActivityViewSet.as_view({"get": "get_recommended_act"})),
        url(r'recommended/organizations/(?P<user_id>\d+)/$',
            OrganizationModelViewSet.as_view({"get": "get_recommended_org"})),

        # 关注组织发布的活动
        url(r'users/followed_organizations/activities/(?P<user_id>\d+)/$',
            ActivityViewSet.as_view({"get": "get_followed_org_act"})),
        
        # 上传图片
        url(r'activities/(?P<act_id>\d+)/avatar/$',
            ImageUploadViewSet.as_view({"post": "upload_act_avatar", "delete" : "remove_act_avatar"})),
        url(r'organizations/(?P<org_id>\d+)/avatar/$',
            ImageUploadViewSet.as_view({"post": "upload_org_avatar"})),


        # 通知
        url(r'^notifications/read/(?P<user_id>\d+)/$', SentNotifViewSet.as_view({"put": "read_notification"})),

        # 测试使用
        url(r'^test/users/$', WXUserViewSet.as_view({"post": "create"})),
        url(r'^test/notifications/', NotificationViewSet.as_view({"post": "create", "get": "list"})),
        url(r'^test/read/notifications/', SentNotifViewSet.as_view({"post": "create",  "get": "list"})),
        # wzk优化
        url(r'users/joined_acts/status/(?P<user_id>\d+)/$', JoinedActViewSet.as_view({"get": "get_user_joined_act_status"})),
        url(r'^users/released_activities/status/(?P<user_id>\d+)/$', ActivityViewSet.as_view({"get": "get_user_act_status"})),
        url(r'^organizations/activities/status/(?P<org_id>\d+)/$', ActivityViewSet.as_view({"get": "get_org_act_status"})),
        url(r'^blocks/activities/status/(?P<block_id>\d+)/$', ActivityViewSet.as_view({"get": "get_block_act_status"})),
    ]))


]

# router = SimpleRouter()
# router.register('activities/join_applications', JoinActApplicationViewSet)
# urlpatterns += router.urls
        
        
        