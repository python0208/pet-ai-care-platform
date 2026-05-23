# API_SPEC.md

# 宠物 AI 养护平台 API 设计文档

接口统一前缀：

```text
/api/
```

---

## 1. 通用规范

### 1.1 请求头

需要登录的接口：

```text
Authorization: Bearer <access_token>
Content-Type: application/json
```

上传文件：

```text
Content-Type: multipart/form-data
```

---

### 1.2 成功响应

```json
{
  "code": 0,
  "message": "success",
  "data": {}
}
```

---

### 1.3 失败响应

```json
{
  "code": 40001,
  "message": "参数错误",
  "errors": {}
}
```

---

### 1.4 分页响应

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "count": 100,
    "page": 1,
    "page_size": 20,
    "results": []
  }
}
```

---

### 1.5 错误码

```text
0       success
40001   参数错误
40002   验证码错误
40003   验证码过期
40101   未登录
40301   无权限
40401   资源不存在
40901   状态冲突
50001   服务器错误
50002   第三方服务异常
60001   AI 服务异常
70001   支付创建失败
70002   支付回调验签失败
```

---

## 2. 健康检查

### GET /api/health/

返回：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "status": "ok"
  }
}
```

---

## 3. 用户认证 API

### POST /api/auth/sms/send/

发送验证码。

请求：

```json
{
  "phone": "13800000000",
  "scene": "login"
}
```

响应：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "debug_code": "123456"
  }
}
```

说明：

- 开发环境可返回 debug_code。
- 生产环境不能返回验证码。

---

### POST /api/auth/sms-login/

手机号验证码登录。

请求：

```json
{
  "phone": "13800000000",
  "code": "123456"
}
```

响应：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "access_token": "xxx",
    "refresh_token": "xxx",
    "user": {
      "id": 1,
      "phone": "13800000000",
      "nickname": "用户"
    }
  }
}
```

---

### POST /api/auth/wx-login/

微信小程序登录。

请求：

```json
{
  "code": "wx_login_code",
  "nickname": "微信用户",
  "avatar": "https://example.com/avatar.png"
}
```

响应：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "access_token": "xxx",
    "refresh_token": "xxx",
    "user": {}
  }
}
```

说明：

- 开发环境允许 mock code。
- 真实环境通过 code2session 获取 openid。

---

### POST /api/auth/logout/

退出登录。

响应：

```json
{
  "code": 0,
  "message": "success",
  "data": {}
}
```

---

### GET /api/users/me/

获取当前用户资料。

响应：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 1,
    "phone": "13800000000",
    "nickname": "用户",
    "avatar": "",
    "gender": "unknown"
  }
}
```

---

### PUT /api/users/me/

更新当前用户资料。

请求：

```json
{
  "nickname": "新昵称",
  "avatar": "https://example.com/avatar.png",
  "gender": "unknown"
}
```

---

## 4. 宠物档案 API

### GET /api/pets/

获取我的宠物列表。

---

### POST /api/pets/

新增宠物。

请求：

```json
{
  "name": "豆豆",
  "species": "cat",
  "breed": "英短",
  "gender": "male",
  "birthday": "2023-01-01",
  "avatar": "",
  "color": "蓝白",
  "weight": "4.20",
  "neutered": true,
  "remark": ""
}
```

---

### GET /api/pets/{id}/

获取宠物详情。

---

### PUT /api/pets/{id}/

更新宠物。

---

### DELETE /api/pets/{id}/

删除宠物。

---

### GET /api/pets/{pet_id}/health-records/

获取宠物健康记录。

查询参数：

```text
record_type=vaccine
```

---

### POST /api/pets/{pet_id}/health-records/

新增健康记录。

请求：

```json
{
  "record_type": "vaccine",
  "title": "猫三联",
  "record_date": "2026-05-01",
  "next_remind_date": "2027-05-01",
  "hospital": "某宠物医院",
  "doctor": "",
  "cost": "120.00",
  "description": "接种正常",
  "attachments": []
}
```

---

### GET /api/health-records/{id}/

健康记录详情。

---

### PUT /api/health-records/{id}/

更新健康记录。

---

### DELETE /api/health-records/{id}/

删除健康记录。

---

### GET /api/pets/{pet_id}/weight-records/

获取体重记录。

---

### POST /api/pets/{pet_id}/weight-records/

新增体重记录。

请求：

```json
{
  "weight": "4.30",
  "record_date": "2026-05-23",
  "remark": "饭前称重"
}
```

---

### DELETE /api/weight-records/{id}/

删除体重记录。

---

## 5. AI 健康咨询 API

### GET /api/ai/conversations/

获取 AI 会话列表。

---

### POST /api/ai/conversations/

创建会话。

请求：

```json
{
  "pet_id": 1,
  "title": "猫咪呕吐咨询"
}
```

---

### GET /api/ai/conversations/{id}/

获取会话详情。

---

### DELETE /api/ai/conversations/{id}/

删除会话。

---

### GET /api/ai/conversations/{id}/messages/

获取会话消息。

---

### POST /api/ai/conversations/{id}/messages/

发送消息到已有会话。

请求：

```json
{
  "message": "猫咪今天吐了两次，精神一般，应该怎么办？",
  "image_urls": []
}
```

---

### POST /api/ai/consult/

发起 AI 健康咨询。

请求：

```json
{
  "pet_id": 1,
  "conversation_id": null,
  "message": "狗狗拉稀一天了，但是精神还可以，应该怎么办？",
  "image_urls": []
}
```

响应：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "conversation_id": 10,
    "message_id": 22,
    "reply": "根据你的描述...",
    "result": {
      "risk_level": "medium",
      "summary": "宠物出现腹泻症状，当前精神尚可。",
      "possible_causes": ["饮食变化", "肠胃不适", "寄生虫或感染可能"],
      "home_care": ["观察精神和食欲", "保证饮水", "暂时避免更换食物"],
      "need_vet": true,
      "warning_signs": ["持续腹泻超过24-48小时", "便血", "精神明显变差"],
      "questions_to_ask": ["是否有呕吐？", "是否更换过食物？"],
      "disclaimer": "本结果仅供养宠护理参考，不能替代专业兽医诊断。"
    }
  }
}
```

---

## 6. 文件上传 API

### POST /api/files/upload/

上传文件。

请求：

```text
multipart/form-data
file=<image>
file_type=pet
```

响应：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 1,
    "url": "https://example.com/media/xxx.jpg"
  }
}
```

---

## 7. 生活服务 API

### GET /api/service-providers/

服务商列表。

查询参数：

```text
provider_type=hospital
keyword=宠物医院
```

---

### GET /api/service-providers/nearby/

附近服务商。

查询参数：

```text
longitude=106.55
latitude=29.56
provider_type=hospital
```

---

### GET /api/service-providers/{id}/

服务商详情。

---

### GET /api/service-providers/{id}/items/

服务项目列表。

---

### POST /api/service-bookings/

创建服务预约。

请求：

```json
{
  "pet_id": 1,
  "provider_id": 1,
  "service_item_id": 2,
  "booking_time": "2026-06-01 10:00:00",
  "contact_name": "张三",
  "contact_phone": "13800000000",
  "address": "重庆市某某区",
  "remark": "宠物比较胆小"
}
```

---

### GET /api/my/service-bookings/

我的预约列表。

---

### GET /api/my/service-bookings/{id}/

预约详情。

---

### POST /api/my/service-bookings/{id}/cancel/

取消预约。

---

## 8. 商城 API

### GET /api/shop/categories/

商品分类。

---

### GET /api/shop/products/

商品列表。

查询参数：

```text
category_id=1
keyword=猫粮
status=on_sale
```

---

### GET /api/shop/products/{id}/

商品详情。

---

### GET /api/shop/cart/

购物车列表。

---

### POST /api/shop/cart/

加入购物车。

请求：

```json
{
  "product_id": 1,
  "quantity": 2
}
```

---

### PATCH /api/shop/cart/{id}/

修改购物车数量。

请求：

```json
{
  "quantity": 3,
  "selected": true
}
```

---

### DELETE /api/shop/cart/{id}/

删除购物车商品。

---

### GET /api/shop/addresses/

地址列表。

---

### POST /api/shop/addresses/

新增地址。

请求：

```json
{
  "name": "张三",
  "phone": "13800000000",
  "province": "重庆市",
  "city": "重庆市",
  "district": "沙坪坝区",
  "detail": "某某街道 1 号",
  "is_default": true
}
```

---

### PUT /api/shop/addresses/{id}/

更新地址。

---

### DELETE /api/shop/addresses/{id}/

删除地址。

---

### POST /api/shop/orders/

创建订单。

请求：

```json
{
  "address_id": 1,
  "items": [
    {
      "product_id": 1,
      "quantity": 2
    }
  ],
  "remark": "尽快发货"
}
```

响应：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "order_id": 1,
    "order_no": "SO202605230001",
    "pay_amount": "99.00",
    "status": "pending_payment"
  }
}
```

---

### GET /api/shop/orders/

我的订单。

---

### GET /api/shop/orders/{id}/

订单详情。

---

### POST /api/shop/orders/{id}/cancel/

取消订单。

---

### POST /api/shop/orders/{id}/confirm-received/

确认收货。

---

## 9. 支付 API

### POST /api/payments/create/

创建支付单。

请求：

```json
{
  "business_type": "shop_order",
  "business_id": 1,
  "channel": "mock"
}
```

响应：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "payment_no": "P202605230001",
    "channel": "mock",
    "amount": "99.00",
    "status": "pending",
    "prepay_data": {}
  }
}
```

---

### GET /api/payments/{payment_no}/status/

查询支付状态。

---

### POST /api/payments/mock/success/

开发环境模拟支付成功。

请求：

```json
{
  "payment_no": "P202605230001"
}
```

---

### POST /api/payments/wechat/notify/

微信支付回调。

---

### POST /api/payments/alipay/notify/

支付宝支付回调。

---

## 10. 通知 API

### GET /api/notifications/

通知列表。

---

### POST /api/notifications/{id}/read/

标记已读。

---

### GET /api/reminders/

提醒列表。

---

## 11. 权限要求

必须满足：

1. 未登录不能访问私有接口；
2. 用户只能访问自己的宠物；
3. 用户只能访问自己的订单；
4. 用户只能访问自己的 AI 会话；
5. 用户只能访问自己的服务预约；
6. 用户只能访问自己的地址；
7. 后端不能根据前端传入 user_id 查询数据；
8. 后端必须使用 request.user 过滤数据。
