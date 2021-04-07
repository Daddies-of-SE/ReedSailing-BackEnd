# Generated by Django 3.1 on 2021-04-08 01:06

import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='活动名称')),
                ('begin_time', models.DateTimeField(verbose_name='开始时间')),
                ('end_time', models.DateTimeField(verbose_name='结束时间')),
                ('pub_time', models.DateTimeField(auto_now_add=True, verbose_name='发布时间')),
                ('contain', models.IntegerField(default=0, verbose_name='人数限制')),
                ('description', models.CharField(blank=True, max_length=500, null=True, verbose_name='活动描述')),
                ('review', models.BooleanField(default=False, verbose_name='是否需要审核')),
            ],
        ),
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='地址名称')),
                ('longitude', models.DecimalField(decimal_places=6, max_digits=10, verbose_name='经度')),
                ('latitude', models.DecimalField(decimal_places=6, max_digits=10, verbose_name='纬度')),
            ],
        ),
        migrations.CreateModel(
            name='Block',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='版块名称')),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='分类名称')),
            ],
        ),
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.CharField(max_length=500, verbose_name='操作内容')),
                ('pub_time', models.DateTimeField(auto_now_add=True, verbose_name='操作时间')),
            ],
        ),
        migrations.CreateModel(
            name='SuperAdmin',
            fields=[
                ('user_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='auth.user')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            bases=('auth.user',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='WXUser',
            fields=[
                ('openid', models.CharField(max_length=500, primary_key=True, serialize=False, unique=True, verbose_name='微信id')),
                ('name', models.CharField(max_length=30, verbose_name='昵称')),
                ('avatar', models.CharField(blank=True, max_length=500, null=True, verbose_name='头像')),
                ('email', models.EmailField(max_length=100, null=True, verbose_name='邮箱')),
                ('sign', models.CharField(blank=True, max_length=200, null=True, verbose_name='个性签名')),
            ],
        ),
        migrations.CreateModel(
            name='UserFeedback',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.CharField(max_length=500, verbose_name='反馈内容')),
                ('pub_time', models.DateTimeField(auto_now_add=True, verbose_name='反馈时间')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='BUAA.wxuser', verbose_name='用户名')),
            ],
        ),
        migrations.CreateModel(
            name='OrgApply',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='组织名称')),
                ('description', models.CharField(max_length=500, verbose_name='申请描述')),
                ('pub_time', models.DateTimeField(auto_now_add=True, verbose_name='申请时间')),
                ('block', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='BUAA.block', verbose_name='所属版块')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='BUAA.wxuser', verbose_name='申请人')),
            ],
        ),
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='组织名称')),
                ('description', models.CharField(blank=True, max_length=500, null=True, verbose_name='组织描述')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('avatar', models.CharField(blank=True, max_length=500, null=True, verbose_name='头像')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='BUAA.wxuser', verbose_name='负责人')),
            ],
        ),
        migrations.CreateModel(
            name='ManagerApply',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.CharField(blank=True, max_length=500, null=True, verbose_name='理由')),
                ('pub_time', models.DateTimeField(auto_now_add=True, verbose_name='申请时间')),
                ('org', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='BUAA.organization', verbose_name='组织')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='BUAA.wxuser', verbose_name='申请用户')),
            ],
        ),
        migrations.CreateModel(
            name='ManageOrg',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('org', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='BUAA.organization', verbose_name='组织')),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='BUAA.wxuser', verbose_name='组织管理员')),
            ],
        ),
        migrations.CreateModel(
            name='JoinActApply',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('act', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='BUAA.activity', verbose_name='申请活动')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='BUAA.wxuser', verbose_name='申请人')),
            ],
        ),
        migrations.CreateModel(
            name='JoinAct',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('act', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='BUAA.activity', verbose_name='活动')),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='BUAA.wxuser', verbose_name='报名人员')),
            ],
        ),
        migrations.CreateModel(
            name='FollowOrg',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('org', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='BUAA.organization', verbose_name='组织')),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='BUAA.wxuser', verbose_name='组织管理员')),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.CharField(max_length=500, verbose_name='内容')),
                ('pub_time', models.DateTimeField(auto_now_add=True, verbose_name='发布时间')),
                ('score', models.IntegerField(verbose_name='评分')),
                ('act', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='BUAA.activity', verbose_name='所属活动')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='BUAA.wxuser', verbose_name='所属用户')),
            ],
        ),
        migrations.AddField(
            model_name='activity',
            name='location',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='BUAA.address', verbose_name='活动地点'),
        ),
        migrations.AddField(
            model_name='activity',
            name='org',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='BUAA.organization', verbose_name='所属组织'),
        ),
        migrations.AddField(
            model_name='activity',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='BUAA.wxuser', verbose_name='发起者'),
        ),
        migrations.AddField(
            model_name='activity',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='BUAA.category', verbose_name='分类'),
        ),
    ]