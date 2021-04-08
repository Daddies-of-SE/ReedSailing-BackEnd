# 后端代码

基于django开发



## 部署指南

### 1、mysql安装

* 安装mysql
* 运行`mysql_secure_installation`设置root账号密码
  * 建议暂时设置为12345678，否则请修改`backend/settings.py`中的`DATABASES['default']['password']`为实际设置的密码
* 运行`mysql -u root -p`，输入密码后`create database BUAA`创建数据库

### 2、django配置

* 使用pip安装django、pymysql
* 克隆本仓库
* 进入`django_backend`目录，运行`python manage.py makemigrations BUAA`
* 运行`python manage.py migrate`

### 3、运行框架

* 运行`pyhton manage.py createcachetable`
* 运行`python manage.py runserver`
  * 运行时不要在本地开vpn代理，会导致报错退出
  * 会在默认的`http://127.0.0.1:8000`部署服务器
* 检验运行是否成功：打开小程序开发工具，进入”我的“——”我的账户“，输入邮箱地址点击”发送验证码“
  * 开发者工具中需要在”详情“——”本地配置“里勾选 ”不校验合法域名…“，否则request会无法访问
  * 此时后端console上显示”发送邮件成功“，邮箱里会收到验证码邮件
  * 小程序的`utils/interact.js`里的`getAPIUrl`指定了服务器为`http://127.0.0.1:8000`，后续部署到云端并设置域名时需要修改

