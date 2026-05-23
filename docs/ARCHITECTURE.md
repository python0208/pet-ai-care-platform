# ARCHITECTURE.md

# 宠物 AI 养护平台技术架构文档

---

## 1. 总体架构

```text
微信小程序 / Android App / iOS App
              |
         uni-app 前端
              |
         HTTPS REST API
              |
       Nginx / API Gateway
              |
 Django + Django REST Framework
              |
 --------------------------------------------------
 users        用户与认证
 pets         宠物档案与健康记录
 ai_chat      AI 健康咨询
 services     生活服务与预约
 shop         商城、购物车、订单
 payments     支付、回调、退款预留
 files        图片上传与对象存储
 notifications提醒、订阅消息
 common       通用工具、枚举、分页、响应格式
 --------------------------------------------------
              |
 MySQL + Redis + Celery + 对象存储 + 第三方大模型 API
```

---

## 2. 前端架构

### 2.1 技术栈

```text
uni-app
Vue3
TypeScript
Pinia
uni-ui / uView Plus / Wot Design Uni
ECharts / ucharts
```

### 2.2 选择 uni-app 的原因

1. 一套代码可以发布到微信小程序、Android App、iOS App。
2. 适合快速开发 MVP。
3. 适合本项目的页面形态：表单、列表、详情、聊天、支付、地图、上传图片。
4. Vue3 成熟度高，适合后续维护。

### 2.3 前端目录

```text
frontend/
  package.json
  src/
    pages/
      index/
      auth/
      pets/
      ai/
      services/
      shop/
      user/
    components/
    stores/
    api/
    utils/
    types/
    static/
    App.vue
    main.ts
    pages.json
    manifest.json
```

### 2.4 前端请求封装

所有接口请求必须通过：

```text
src/api/request.ts
```

要求：

1. 自动附带 token。
2. 统一处理 401。
3. 统一处理后端响应格式。
4. 统一错误提示。
5. 支持上传文件。
6. 支持请求 loading 配置。

---

## 3. 后端架构

### 3.1 技术栈

```text
Python 3.11+
Django 5.x
Django REST Framework
MySQL 8.x
Redis
Celery
SimpleJWT
django-filter
Pillow
httpx / requests
django-environ
```

### 3.2 后端目录

```text
backend/
  manage.py
  requirements.txt
  .env.example
  config/
    settings.py
    urls.py
    celery.py
    asgi.py
    wsgi.py
  apps/
    common/
    users/
    pets/
    ai_chat/
    services/
    shop/
    payments/
    files/
    notifications/
  tests/
```

---

## 4. Django App 职责

## 4.1 common

职责：

- 通用模型基类
- 统一响应格式
- 统一异常处理
- 通用分页
- 权限工具
- 枚举
- 工具函数

建议文件：

```text
apps/common/
  models.py
  responses.py
  pagination.py
  permissions.py
  exceptions.py
  enums.py
  utils.py
```

---

## 4.2 users

职责：

- 用户模型
- 邮箱注册
- 邮箱密码登录
- 微信小程序登录预留
- JWT 登录
- 用户资料
- 账号注销预留

---

## 4.3 pets

职责：

- 宠物档案
- 健康记录
- 疫苗记录
- 驱虫记录
- 就诊记录
- 过敏记录
- 体重记录

---

## 4.4 ai_chat

职责：

- AI 会话
- AI 消息
- AI 咨询结果
- 提示词模板
- 模型 provider
- AI 调用日志

---

## 4.5 services

职责：

- 服务商
- 服务项目
- 服务预约
- 附近服务
- 服务评价预留

---

## 4.6 shop

职责：

- 商品分类
- 商品
- 购物车
- 地址
- 商城订单
- 订单明细

---

## 4.7 payments

职责：

- 统一支付单
- 支付渠道 provider
- 微信支付
- 支付宝支付
- mock 支付
- 支付回调
- 支付日志
- 支付状态同步

---

## 4.8 files

职责：

- 图片上传
- 文件大小限制
- 文件类型限制
- 文件 URL 管理
- 对象存储预留

---

## 4.9 notifications

职责：

- 系统通知
- 健康提醒
- 疫苗提醒
- 驱虫提醒
- 订单通知
- 预约通知
- 小程序订阅消息预留

---

## 5. 数据库

主数据库：

```text
MySQL 8.x
```

缓存：

```text
Redis
```

异步任务：

```text
Celery + Redis
```

文件存储：

```text
开发环境：本地 MEDIA_ROOT
生产环境：阿里云 OSS / 腾讯云 COS / MinIO
```

---

## 6. 认证架构

### 6.1 登录方式

第一阶段支持：

```text
邮箱注册
邮箱密码登录
微信小程序登录预留
```

当前 MVP 不使用邮箱验证码，手机号不作为认证登录方式。手机号仅在后续收货地址、服务预约联系人等业务联系方式中使用。

### 6.2 Token

使用 JWT：

```text
access_token
refresh_token
```

前端保存 token，所有需要登录的接口带：

```text
Authorization: Bearer <access_token>
```

### 6.3 权限原则

后端永远以：

```python
request.user
```

作为当前用户来源，不可信任前端传入的 `user_id`。

---

## 7. AI 架构

### 7.1 Provider 抽象

不要在业务代码中写死模型厂商。

推荐设计：

```text
AIProviderBase
  - chat(messages, images=None, stream=False)

OpenAICompatibleProvider
DeepSeekProvider
QwenProvider
MockAIProvider
```

### 7.2 环境变量

```env
AI_PROVIDER=openai_compatible
AI_API_BASE=https://api.example.com/v1
AI_API_KEY=your-key
AI_MODEL=your-model
```

### 7.3 AI 调用流程

```text
用户选择宠物
       |
输入症状 / 上传图片
       |
后端读取宠物档案
       |
后端读取健康记录摘要
       |
拼接系统提示词
       |
调用第三方大模型
       |
解析结构化结果
       |
保存 AIMessage 和 AIConsultationResult
       |
返回前端展示
```

### 7.4 AI 输出结构

```json
{
  "risk_level": "low|medium|high|unknown",
  "summary": "症状总结",
  "possible_causes": [],
  "home_care": [],
  "need_vet": true,
  "warning_signs": [],
  "questions_to_ask": [],
  "disclaimer": "本结果仅供养宠护理参考，不能替代兽医诊断。"
}
```

---

## 8. 支付架构

### 8.1 统一支付中心

支付不要写死在商城里，必须抽象成统一支付模块。

```text
业务订单
   |
PaymentOrder
   |
支付渠道 Provider
   |
微信支付 / 支付宝支付 / Mock 支付
   |
支付回调
   |
验签 + 幂等
   |
更新 PaymentOrder
   |
同步更新业务订单
```

### 8.2 支付对象

```text
shop_order       商城订单
service_booking  服务预约，预留
vip              会员订阅，预留
```

### 8.3 支付状态

```text
pending   待支付
paid      已支付
failed    失败
closed    已关闭
refunded  已退款
```

### 8.4 幂等规则

同一个支付回调重复到达时：

1. 如果 PaymentOrder 已经是 paid，直接返回成功。
2. 不重复修改业务订单。
3. 不重复扣库存。
4. 不重复发通知。
5. 所有回调都记录日志。

---

## 9. 文件上传架构

### 9.1 支持文件

第一阶段只支持图片：

```text
jpg
jpeg
png
webp
```

### 9.2 上传场景

```text
用户头像
宠物头像
就诊记录图片
AI 咨询图片
商品图片
服务商图片
```

### 9.3 限制

```text
单文件最大 5MB
禁止上传可执行文件
生产环境建议使用对象存储
```

---

## 10. 异步任务

使用 Celery 处理：

1. 疫苗提醒；
2. 驱虫提醒；
3. 订单超时关闭；
4. 支付状态主动查询；
5. AI 慢任务预留；
6. 小程序订阅消息发送预留。

第一阶段可以先只搭架构，核心流程同步执行。

---

## 11. 环境变量示例

```env
# Django
DEBUG=True
SECRET_KEY=change-me
ALLOWED_HOSTS=127.0.0.1,localhost

# Database
DB_NAME=pet_ai_care
DB_USER=root
DB_PASSWORD=password
DB_HOST=127.0.0.1
DB_PORT=3306

# Redis
REDIS_URL=redis://127.0.0.1:6379/0

# JWT
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=60
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7

# WeChat Mini Program
WECHAT_MINI_APPID=
WECHAT_MINI_SECRET=

# AI
AI_PROVIDER=openai_compatible
AI_API_BASE=
AI_API_KEY=
AI_MODEL=

# Payment
PAYMENT_MOCK=True
WECHAT_PAY_MCH_ID=
WECHAT_PAY_API_KEY=
WECHAT_PAY_CERT_SERIAL_NO=
WECHAT_PAY_PRIVATE_KEY_PATH=
ALIPAY_APP_ID=
ALIPAY_PRIVATE_KEY_PATH=
ALIPAY_PUBLIC_KEY_PATH=

# File storage
MEDIA_URL=/media/
MEDIA_ROOT=media
```

---

## 12. 部署架构

生产环境建议：

```text
Nginx
Gunicorn / Uvicorn
Django
MySQL
Redis
Celery Worker
Celery Beat
对象存储
HTTPS
```

### 12.1 Nginx

负责：

- HTTPS；
- 反向代理 API；
- 静态文件；
- 媒体文件；
- 小程序合法域名访问。

### 12.2 Django

生产环境要求：

```text
DEBUG=False
SECRET_KEY 环境变量
ALLOWED_HOSTS 正确配置
CORS 白名单
日志配置
数据库连接池
```

---

## 13. 安全要求

1. 密钥不能入库。
2. 密钥不能提交 Git。
3. 订单金额以后端为准。
4. 支付状态以后端为准。
5. 文件上传限制类型和大小。
6. 用户数据必须隔离。
7. AI 不能作为兽医诊断。
8. 管理后台必须设置强密码。
9. 生产环境必须 HTTPS。
10. 数据库需要定期备份。
