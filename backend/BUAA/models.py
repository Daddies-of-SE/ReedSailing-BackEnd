from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class WXUser(models.Model):
    openid = models.CharField(unique=True,verbose_name="微信id",primary_key=True)
    name = models.CharField(max_length=30, verbose_name="昵称")
    avatar = models.CharField(max_length=500, null=True, blank=True, verbose_name="头像")
    email = models.EmailField(max_length=100, null=True, verbose_name="邮箱")
    sign = models.CharField(max_length=200, null=True, blank=True, verbose_name="个性签名")

class Organization(models.Model):
    blockType = (
        ('CLUB','社团'),
        ('LECTURE','博雅'),
        ('VOLUNTEER', '志愿'),
        ('UNION','学生会'),
        ('PERSONAL','个人'),
    )
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, xunique=True,verbose_name="组织名称")
    description = models.CharField(max_length=500, null=True, blank=True, verbose_name="组织描述")
    create_time = models.DateTimeField(auto_now_add=True,verbose_name="创建时间")
    owner = models.ForeignKey('WXUser', on_delete=models.CASCADE,verbose_name="负责人")
    block = models.CharField(max_length=20,choices=blockType,default='社团',verbose_name="版块")
    avatar = models.CharField(max_length=500, null=True, blank=True, verbose_name="头像")
    #avatar = models.FileField(upload_to='avatar')  文件形式传到服务器，char则是一个地址路径，不确定


class Activity(models.Model):
    classType = (
        ('SPORT', '体育'),
        ('SPEECH', '讲座'),
        ('VOLUNTEER', '志愿'),
        ('COMP', '竞赛'),
        ('SOCIAL', ' 社交'),
        ('SHOW', '演出'),
    )
    blockType = (
        ('CLUB','社团'),
        ('LECTURE','博雅'),
        ('VOLUNTEER', '志愿'),
        ('UNION','学生会'),
        ('PERSONAL','个人'),
    )
    name = models.CharField(max_length=100, unique=True,verbose_name="活动名称")
    type = models.CharField(max_length=20, choices=classType, default='体育',verbose_name="分类")
    beginTime = models.DateTimeField(verbose_name="开始时间")
    endTime = models.DateTimeField(verbose_name="结束时间")
    pubTime = models.DateTimeField(auto_now_add=True,verbose_name="发布时间")
    contain = models.IntegerField(verbose_name="人数限制", default=0)
    location = models.CharField(verbose_name="地理位置", default="116°23′17”")
    description = models.CharField(max_length=500, null=True, blank=True, verbose_name="活动描述")
    isPersonal = models.BooleanField(verbose_name="是否个人活动",default=True)
    org = models.ForeignKey('Organization',on_delete=models.CASCADE)
    person = models.ForeignKey('WXUser',on_delete=models.CASCADE)
    block = models.CharField(max_length=20,choices=blockType,default='个人',verbose_name="板块")#组织需要与组织模块保证一致

class Comment(models.Model):
    act = models.ForeignKey('Activity',on_delete=models.CASCADE)
    user = models.ForeignKey('WXUser',on_delete=models.CASCADE)
    content = models.CharField(max_length=500)
    pubTime = models.DateTimeField(auto_now_add=True)


class SuperAdmin(User):
    name = models.CharField(max_length=100,unique=True)

class Log(models.Model):
    content = models.CharField(max_length=500)
    pubTime = models.DateTimeField(auto_now_add=True)

class ManagerApply(models.Model):
    org = models.ForeignKey('Organization',on_delete=models.CASCADE)
    user = models.ForeignKey('WXUser',on_delete=models.CASCADE)
    content = models.CharField(max_length=500,null=True,blank=True)
    pubTime = models.DateTimeField(auto_now_add=True)

class OrgApply(models.Model):
    blockType = (
        ('CLUB', '社团'),
        ('LECTURE', '博雅'),
        ('VOLUNTEER', '志愿'),
        ('UNION', '学生会'),
        ('PERSONAL', '个人'),
    )
    name = models.CharField(max_length=50, xunique=True, verbose_name="组织名称")
    description = models.CharField(max_length=500, verbose_name="申请描述")
    user = models.ForeignKey('WXUser', on_delete=models.CASCADE, verbose_name="申请人")
    block = models.CharField(max_length=20, choices=blockType, default='社团',verbose_name="版块")
    pubTime = models.DateTimeField(auto_now_add=True)

class JoinAct(models.Model):
    act = models.ForeignKey('Activity', on_delete=models.CASCADE)
    user = models.ForeignKey('WXUser', on_delete=models.CASCADE)

class FollowOrg(models.Model):
    org = models.ForeignKey('Organization',on_delete=models.CASCADE)
    user = models.ForeignKey('WXUser', on_delete=models.CASCADE)

class OrgManager(models.Model):
    org = models.ForeignKey('Organization', on_delete=models.CASCADE)
    user = models.ForeignKey('WXUser', on_delete=models.CASCADE)



