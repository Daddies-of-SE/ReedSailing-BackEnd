from django.db import models
from django.contrib.auth.models import User


# Create your models here.


# 用户
class WXUser(models.Model):
    openid = models.CharField(unique=True, verbose_name="微信id", primary_key=True)
    name = models.CharField(max_length=30, verbose_name="昵称")
    avatar = models.CharField(max_length=500, null=True, blank=True, verbose_name="头像")
    email = models.EmailField(max_length=100, null=True, verbose_name="邮箱")
    sign = models.CharField(max_length=200, null=True, blank=True, verbose_name="个性签名")
    follow_org = models.ManyToManyField('Organization', verbose_name="关注组织")


# 版块
class Block(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, xunique=True, verbose_name="版块名称")


# 组织
class Organization(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, xunique=True, verbose_name="组织名称")
    description = models.CharField(max_length=500, null=True, blank=True, verbose_name="组织描述")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    owner = models.ForeignKey('WXUser', on_delete=models.CASCADE, verbose_name="负责人")
    manager = models.ManyToManyField('WXUser', verbose_name="组织管理员")
    block = models.ForeignKey('Block', on_delete=models.CASCADE, verbose_name="所属版块")
    avatar = models.CharField(max_length=500, null=True, blank=True, verbose_name="头像")
    # avatar = models.FileField(upload_to='avatar')  文件形式传到服务器，char则是一个地址路径，不确定


# 分类
class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, xunique=True, verbose_name="分类名称")


# 活动
class Activity(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="活动名称")
    beginTime = models.DateTimeField(verbose_name="开始时间")
    endTime = models.DateTimeField(verbose_name="结束时间")
    pubTime = models.DateTimeField(auto_now_add=True, verbose_name="发布时间")
    contain = models.IntegerField(verbose_name="人数限制", default=0)
    description = models.CharField(max_length=500, null=True, blank=True, verbose_name="活动描述")
    isPersonal = models.BooleanField(verbose_name="是否个人活动", default=True)
    type = models.ForeignKey('Category', on_delete=models.CASCADE, verbose_name="分类")
    org = models.ForeignKey('Organization', on_delete=models.CASCADE, verbose_name="所属组织")
    person = models.ManyToManyField('WXUser', verbose_name="报名人员")
    block = models.ForeignKey('Block', on_delete=models.CASCADE, verbose_name="所属版块")  # 组织需要与组织模块保证一致


# 地址
class Address(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="地址名称")
    latitude = models.DecimalField(verbose_name="经度")
    longitude = models.DecimalField(verbose_name="维度")
    location = models.ForeignKey('Activity', on_delete=models.CASCADE, verbose_name="活动地址")


# 评论
class Comment(models.Model):
    act = models.ForeignKey('Activity', on_delete=models.CASCADE)
    user = models.ForeignKey('WXUser', on_delete=models.CASCADE)
    content = models.CharField(max_length=500)
    pubTime = models.DateTimeField(auto_now_add=True)


# 超级管理员
class SuperAdmin(User):
    name = models.CharField(max_length=100, unique=True)


# Log
class Log(models.Model):
    content = models.CharField(max_length=500)
    pubTime = models.DateTimeField(auto_now_add=True)


# 用户反馈
class UserFeedback(models.Model):
    content = models.CharField(max_length=500)
    user = models.ForeignKey('WXUser', on_delete=models.CASCADE)


# 组织管理员申请
class ManagerApply(models.Model):
    org = models.ForeignKey('Organization', on_delete=models.CASCADE)
    user = models.ForeignKey('WXUser', on_delete=models.CASCADE)
    content = models.CharField(max_length=500, null=True, blank=True)
    pubTime = models.DateTimeField(auto_now_add=True)


# 组织申请
class OrgApply(models.Model):
    name = models.CharField(max_length=50, xunique=True, verbose_name="组织名称")
    description = models.CharField(max_length=500, verbose_name="申请描述")
    user = models.ForeignKey('WXUser', on_delete=models.CASCADE, verbose_name="申请人")
    block = models.ForeignKey('Block', on_delete=models.CASCADE, verbose_name="所属版块")
    pubTime = models.DateTimeField(auto_now_add=True)


# 加入活动申请
class JoinActApply(models.Model):
    act = models.ForeignKey('Activity', on_delete=models.CASCADE)
    user = models.ForeignKey('WXUser', on_delete=models.CASCADE)
