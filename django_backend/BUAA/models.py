from django.db import models
from django.contrib.auth.models import User


# Create your models here.


# 用户
class WXUser(models.Model):
    openid = models.CharField(unique=True, verbose_name="微信openid", max_length=500, help_text="微信openid --string")
    name = models.CharField(max_length=30, verbose_name="昵称", help_text="昵称 --string")
    avatar = models.CharField(max_length=500, null=True, blank=True, verbose_name="头像", help_text="头像 --string")
    email = models.EmailField(max_length=100, null=True, verbose_name="邮箱", help_text="邮箱 --string")
    sign = models.CharField(max_length=200, null=True, blank=True, verbose_name="个性签名", help_text="个性签名 --string")


# 活动
class Activity(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="活动名称", help_text="活动名称 --string")
    begin_time = models.DateTimeField(verbose_name="开始时间", help_text="开始时间")
    end_time = models.DateTimeField(verbose_name="结束时间")
    pub_time = models.DateTimeField(auto_now_add=True, verbose_name="发布时间")
    contain = models.IntegerField(verbose_name="人数限制", default=0)
    description = models.CharField(max_length=500, null=True, blank=True, verbose_name="活动描述")
    review = models.BooleanField(verbose_name="是否需要审核", default=False)
    # is_personal = models.BooleanField(verbose_name="是否个人活动", default=True)

    owner = models.ForeignKey('WXUser', on_delete=models.CASCADE, verbose_name="发起者")
    type = models.ForeignKey('Category', on_delete=models.CASCADE, verbose_name="分类")
    org = models.ForeignKey('Organization', on_delete=models.CASCADE, verbose_name="所属组织")
    location = models.ForeignKey('Address', on_delete=models.CASCADE, verbose_name="活动地点")
    # block = models.ForeignKey('Block', on_delete=models.CASCADE, verbose_name="所属版块")  # 组织需要与组织模块保证一致

    # person = models.ManyToManyField('WXUser', verbose_name="报名人员")


class JoinedAct(models.Model):
    act = models.ForeignKey('Activity',on_delete=models.CASCADE,verbose_name='活动')
    person = models.ForeignKey('WXUser', verbose_name="报名人员",on_delete=models.CASCADE)


# 分类
class Category(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="分类名称")


# 地址
class Address(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="地址名称")
    longitude = models.DecimalField(max_digits=10,decimal_places=6,verbose_name="经度")
    latitude = models.DecimalField(max_digits=10,decimal_places=6,verbose_name="纬度")


# 组织
class Organization(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="组织名称")
    description = models.CharField(max_length=500, null=True, blank=True, verbose_name="组织描述")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    avatar = models.CharField(max_length=500, null=True, blank=True, verbose_name="头像")

    owner = models.ForeignKey('WXUser', on_delete=models.CASCADE, verbose_name="负责人")
    block = models.ForeignKey('Block', on_delete=models.CASCADE, verbose_name="所属版块")


# 组织管理员
class OrgManager(models.Model):
    org = models.ForeignKey('Organization', verbose_name='组织', on_delete=models.CASCADE)
    person = models.ForeignKey('WXUser', verbose_name="组织管理员", on_delete=models.CASCADE)


# 关注组织
class FollowedOrg(models.Model):
    org = models.ForeignKey('Organization',verbose_name='关注的组织', on_delete=models.CASCADE)
    person = models.ForeignKey('WXUser', verbose_name="用户", on_delete=models.CASCADE)


# 评价
class Comment(models.Model):
    content = models.CharField(max_length=500, null=True, verbose_name="内容")
    pub_time = models.DateTimeField(auto_now_add=True, verbose_name="发布时间")
    score = models.IntegerField(verbose_name="评分")

    act = models.ForeignKey('Activity', on_delete=models.CASCADE, verbose_name="所属活动")
    user = models.ForeignKey('WXUser', on_delete=models.CASCADE, verbose_name="所属用户")


# 版块
class Block(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="版块名称")


# 超级管理员
class SuperAdmin(User):
    name = models.CharField(max_length=100, unique=True)


# 组织管理员申请
class ManagerApplication(models.Model):
    org = models.ForeignKey('Organization', on_delete=models.CASCADE, verbose_name="组织")
    user = models.ForeignKey('WXUser', on_delete=models.CASCADE, verbose_name="申请用户")
    content = models.CharField(max_length=500, null=True, blank=True, verbose_name="理由")
    pub_time = models.DateTimeField(auto_now_add=True, verbose_name="申请时间")


# Log
class Log(models.Model):
    content = models.CharField(max_length=500, verbose_name="操作内容")
    pub_time = models.DateTimeField(auto_now_add=True, verbose_name="操作时间")


# 用户反馈
class UserFeedback(models.Model):
    content = models.CharField(max_length=500, verbose_name="反馈内容")
    pub_time = models.DateTimeField(auto_now_add=True, verbose_name="反馈时间")

    user = models.ForeignKey('WXUser', on_delete=models.CASCADE, verbose_name="用户名")


# 组织申请
class OrgApplication(models.Model):
    STATUS = (
        (0, '待审批'),
        (1, '审批通过'),
        (2, '审批未通过')
    )
    name = models.CharField(max_length=50, verbose_name="组织名称")
    description = models.CharField(max_length=500, verbose_name="申请描述")
    pub_time = models.DateTimeField(auto_now_add=True, verbose_name="申请时间")
    status = models.SmallIntegerField(choices=STATUS, default=0, verbose_name="审批状态")

    user = models.ForeignKey('WXUser', on_delete=models.CASCADE, verbose_name="申请人")
    block = models.ForeignKey('Block', on_delete=models.CASCADE, verbose_name="所属版块")


# 加入活动申请
class JoinActApplication(models.Model):
    act = models.ForeignKey('Activity', on_delete=models.CASCADE, verbose_name="申请活动")
    user = models.ForeignKey('WXUser', on_delete=models.CASCADE, verbose_name="申请人")

