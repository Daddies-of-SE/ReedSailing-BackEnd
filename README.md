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
* 已安装配置：git、python（pip、django及依赖库、pymysql）、mysql、vim（colorscheme等）

* 待安装配置：nginx、uwsgi（域名部署相关，后期需要完成）



### ※ 如何运行

* 后端维护：在服务器上运行
  * 直接输入`run`命令即可
  * `run`原理阐释：进入后端目录下`django_backend`，运行`python manage.py runserver 0:80`（注意这里的ip必须写0:80）

* 前端调试：在自己的电脑上（首先要保证后端已经在运行上述命令）
  * 小程序开发工具—右上角“详情”—本地设置—勾选“不校验合法域名”
  * 确认`app.js`中的`server`为`http://rs.test/`（不要尝试改成reedsailing.xyz，会因未备案被墙，后端显示broken pipe）
  * 修改hosts文件
    * 路径：mac/linux下为`/etc/hosts`，windows下为`C:\Windows\System32\drivers\etc\hosts`
    * 在该文件最后增加一行`114.116.94.235 rs.test`
  * 此时尝试编译运行，点击首页登录并查看调试器，或者直接在浏览器中输入`rs.test/users/`，可以看到返回结果；后端（即服务器python运行窗口）可以看到收到的请求

### 说明

以后尽可能都直接用这个服务器上的后端，首先可以避免每个人都反复pull、migrate（理想情况下后端代码只存在于服务器上），其次可以保证数据库一致便于测试

现在实际上使用了nginx，从而使IP地址可以解析到后端目录下的django项目，但后续上线到手机端时需要配置后端到域名（使用nginx和uwsgi）



## API接口

运行后端

在`http://127.0.0.1:8000/docs`可以查看API接口



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

