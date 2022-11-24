# SmarterWMS--开源智能仓储系统
---

## 项目介绍：

完全智能开源仓储管理软件，遵循MIT协议，前后端分离，且完全开源，API使用restful协议，方便二次开发，前端代码使用quasar进行构建，后端使用Python Django3.1，利用API，可以支持多仓，波次发货，合并拣货，Milk-Run等业务模型。

- GitHub地址：[GitHub](https://github.com/heqixi/smarterwms.git)
- 邮箱：heqixi4821@gmail.com

---
## 项目初衷：
目前国内有大量的中小微型企业需要管理商品，SKU，库存等，而市面上的软件/Sass设计原型都是针对大型仓储系统的，现在智能软件硬件的发展，打造一款免费开源的工业级智能Sass的想法

- 愿景：用智能化，去中心化软件系统帮助中小微型实体。

## Supplier 供应商子服务介绍以及构建指南

此工程是对接smarterwms的平台的一个基础服务，提供供应商管理和库存采购能力

## 开发环境：

- Python 版本为 V 3.9.5 +

- Django 版本为 V 3.1.12 +

- Django-rest-framework  V 3.12.2 +

- djangogrpcframework  V 0.2.1 +

- Django-silk 版本为 V 4.1.0 (如果是部署上线，请关闭silk，silk仅为调试API接口速度用，有可能会泄露用户信息)

- API，遵循 RESTful 架构

---

## 构建命令：

- 下载代码：

~~~shell
git clone https://github.com/heqixi/smarterwms.git
~~~

- 安装Python库：

~~~python
pip install -r requirements.txt
~~~

注意：`安装需要Twisted库，这个库有时候会安装不上，需要下载下来本地安装`

- 下载地址：[TWISTED](https://www.lfd.uci.edu/~gohlke/pythonlibs/#twisted)

~~~python
pip install Twisted{你下载下来的版本名称}
~~~

注意：`本地安装需要注意路径`

- 初始化数据库：

~~~python
python manage.py makemigrations
~~~

- 迁移数据库：

~~~python
python manage.py migrate
~~~

Django默认使用sqlite3作为数据库，如果需要mysql数据库，请在smarterwms/settings.py里面配置DATABASE

### 开发服务器运行：

- 运行后端服务，用于处理Http/Https请求：

~~~python
daphne -b 0.0.0.0 -p 8008 greaterwms.asgi:application
~~~

-运行grpc服务器，接受gprc请求, 参数 --dev 表示在开发环境下运行
~~~python
python ./manage.py runserver --dev your_ip:port
~~~

## 开发指南：

### Django-silk

- django-silk为开发时的调试工具，可以统计每个接口的响应速度，如果需要部署到生产环境，请删除Django-silk相关配置，因为会有泄露用户信息的风险，或者直接修改Django-silk库，让用户只能看到自己的请求数据

### 关于数据传输

- 需要在所有的Http/Https请求头headers里面加入token值，这个值就是用户的数据唯一标识OPENID
- 所有的数据传输需要设定content-type为application/json

### OPENID

- OPENID是注册用户数据的唯一标识，当管理员直接注册时，会有developer=1这个管理员标识。
- 你可以根据developer标识来做自定义二次开发

### APPID

- APPID是用户数据组唯一标识
- 如果需要多公司运营，或者多仓运营，可以通过APPID做统一链接，来实现多公司，多仓操作

## 业务流程：
待补充