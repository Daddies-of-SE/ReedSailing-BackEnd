# 后端代码

基于django开发



## 本地部署指南

### 1、mysql安装

* 安装mysql
* 运行`mysql_secure_installation`设置root账号密码
  * 建议暂时设置为12345678，否则  请修改`backend/settings.py`中的`DATABASES['default']['password']`为实际设置的密码
* 启动mysql：`mysql.server start`（每次重启电脑后需要运行）
* 运行`mysql -u root -p`，输入密码后`create database BUAA`创建数据库

### 2、django配置

* 克隆本仓库
* 在仓库根目录下运行`pip install -r requirements.txt`
* 进入`django_backend`目录，运行`python manage.py makemigrations BUAA`
* 运行`python manage.py migrate`

### 3、运行框架

* 运行`python manage.py collectstatic`将静态文件复制到`django_backend/static`

* 运行`python manage.py createcachetable`

* 运行`python manage.py runserver`
  * 运行时不要在本地开vpn代理，会导致报错退出
  * 会在默认的`http://127.0.0.1:8000`部署服务器
  
* 检验运行是否成功：

  1. 打开小程序开发工具，进入”我的“——”我的账户“，输入邮箱地址点击”发送验证码“

  * 开发者工具中需要在”详情“——”本地配置“里勾选 ”不校验合法域名…“，否则request会无法访问
  * 此时后端console上显示”发送邮件成功“，邮箱里会收到验证码邮件
  * 小程序的`utils/interact.js`里的`getAPIUrl`指定了服务器为`http://127.0.0.1:8000`，后续部署到云端并设置域名时需要修改

  2. 打开`http://127.0.0.1:8000/docs/`，找到对应接口点击interact进行交互



## ※ 服务器部署

### 服务器基本信息

* IP：`114.116.94.235`
* 服务器账号root，密码见qq群（安全起见不写在此处）
* mysql账号root，密码12345678
* 后端文件目录：`/root/ReedSailing-BackEnd`
* alias的便捷指令
  * `pi`：封装了`pip install -i 清华源`，直接`pi numpy`即可安装
  * `upload`：封装了`git add, commit, push`，直接`upload "hello world"`即可上传
  * `run`：封装了进入后端目录、运行`runserver`的操作，直接`run`即可部署后端
* 已安装配置：git、python（pip、django及依赖库、pymysql）、mysql、vim（colorscheme等）、nginx、uwsgi




### 运行与调试

* 输入`nginx`启动nginx
* 在`~/ReedSailing-BackEnd/django_backend`下输入`uwsgi uwsgi.ini`启动uwsgi，配置文件为uwsgi.ini
* 修改nginx配置文件后要输入`nginx -s reload`使nginx重新加载配置文件
* 修改django代码后要在`~/ReedSailing-BackEnd/django_backend`下输入`touch reload`（这个命令会修改reload文件的时间戳，触发uwsgi重启服务）
* 前端调试：在自己的电脑上（首先要保证后端已经在运行上述命令）
  * ~~小程序开发工具—右上角“详情”—本地设置—勾选“不校验合法域名”~~
  * 确认`app.js`中的`server`为`http://reedsailing.xyz/api/`
  * 此时尝试编译运行，点击首页登录并查看调试器，或者直接在浏览器中输入`reedsailing.xyz/api/users/`，可以看到返回结果；后端（即服务器python运行窗口）可以看到收到的请求

### 说明

以后尽可能都直接用这个服务器上的后端，首先可以避免每个人都反复pull、migrate（理想情况下后端代码只存在于服务器上），其次可以保证数据库一致便于测试

## API接口

运行后端

在`http://reedsailing.xyz/api/docs`可以查看API接口



## 消息发送

### 定时获取access_token

由于微信小程序的消息推送需要使用`access_token`，而`access_token`两个小时过期，因此需要定期向微信服务接口发送请求获取。

定时任务需要用到`django-crontab`，运行和django无关，依赖的是linux的crontab定时服务，因此无法在windowns下运行。

安装：`pip install django-crontab`

启动定时任务
 `python manage.py crontab add`

显示定时任务
 `python manage.py crontab show`

删除定时任务
 `python manage.py crontab remove`



参考资料：https://www.cnblogs.com/linqiaobao/p/14230337.html



消息队列，异步执行：celery



## 附录

### 修改MySQL密码

在mysql命令行中依次输入以下内容（mysql命令对大小写不敏感）

```mysql
use mysql;
ALTER USER 'root'@'localhost' IDENTIFIEED WITH mysql_native_password BY "12345678";
FLUSH privileges;
quit;
```

然后用新密码重新登录。

