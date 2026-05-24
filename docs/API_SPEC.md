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

### POST /api/auth/register/

邮箱注册。本轮不使用邮箱验证码，注册成功后直接返回 JWT。

请求：

```json
{
  "email": "user@example.com",
  "password": "StrongPass123",
  "confirm_password": "StrongPass123",
  "nickname": "宠护用户"
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
      "email": "user@example.com",
      "nickname": "宠护用户",
      "avatar": "",
      "gender": "unknown",
      "is_email_verified": false
    }
  }
}
```

---

### POST /api/auth/login/

邮箱密码登录。本轮不做登录时自动注册，不要求邮箱已验证。

请求：

```json
{
  "email": "user@example.com",
  "password": "StrongPass123"
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
      "email": "user@example.com",
      "nickname": "宠护用户",
      "avatar": "",
      "gender": "unknown",
      "is_email_verified": false
    }
  }
}
```

---

### POST /api/auth/token/refresh/

刷新 access token。

请求：

```json
{
  "refresh": "xxx"
}
```

响应：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "access": "xxx"
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
    "email": "user@example.com",
    "nickname": "用户",
    "avatar": "",
    "gender": "unknown",
    "is_email_verified": false
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

本组接口均需要 JWT 登录态。后端始终使用 `request.user` 过滤数据，不接收也不信任前端传入的 `owner_id`；用户只能访问自己的宠物、健康记录和体重记录。一个用户可以拥有多个宠物档案，关系为 `User 1 - N Pet`。

### GET /api/pets/

获取我的宠物列表。接口返回当前登录用户的全部宠物，不会因为新增第二只宠物而覆盖或隐藏旧宠物。

前端档案页应维护 `pets`、`selectedPetId`、`selectedPet`、`healthRecords` 和 `weightRecords`。进入页面时先调用本接口获取全部宠物；如果本地保存的 `selectedPetId` 仍存在则优先选中，否则选中第一只宠物；切换宠物时重新请求该宠物的健康记录和体重记录。

---

### POST /api/pets/

新增宠物。后端自动将 `owner` 设置为 `request.user`，前端不能传 `owner_id`。新增宠物后应重新请求 `/api/pets/`，旧宠物必须继续保留在列表中。

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

详情包含宠物基础信息、最近一次疫苗记录、最近一次驱虫记录、最近一次体重记录、提醒列表和首页统计字段：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 1,
    "name": "豆豆",
    "species": "cat",
    "breed": "英短金渐层",
    "gender": "male",
    "birthday": "2024-01-01",
    "avatar": "",
    "color": "金色",
    "weight": "4.60",
    "neutered": true,
    "remark": "",
    "latest_vaccine_record": {},
    "latest_deworm_record": {},
    "latest_weight_record": {},
    "reminders": [
      {
        "record_type": "vaccine",
        "title": "猫三联",
        "next_remind_date": "2026-06-07",
        "days_until": 15
      }
    ],
    "record_stats": {
      "vaccine_count": 1,
      "deworm_status": "体内驱虫",
      "current_weight": "4.60"
    }
  }
}
```

---

### PUT /api/pets/{id}/

更新宠物。

---

### PATCH /api/pets/{id}/

局部更新宠物。

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

### PATCH /api/health-records/{id}/

局部更新健康记录。

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

### 前端默认宠物头像

如果 `pet.avatar` 为空，前端展示：

```text
frontend/src/static/images/default-pet-avatar.svg
```

---

## 5. AI 养宠助手 API

本组接口均需要 JWT 登录态。用户只能查看自己的 AI 会话，只能选择自己的宠物发起咨询。AI 调用由后端统一完成，前端不接触 `AI_API_KEY`。

AI 角色为“AI 养宠助手”，支持日常养护问答、健康咨询和档案记录辅助。模型不能直接写数据库；如果识别到记录意图，后端只保存 `AIActionDraft`，用户确认后才执行写入。

当前默认接入：

```text
AI_PROVIDER=ark_openai_compatible
AI_API_BASE=https://ark.cn-beijing.volces.com/api/v3
AI_MODEL=doubao-seed-2-0-mini-260428
```

真实 key 只允许写入本地 `backend/.env`。

### GET /api/ai/conversations/

获取 AI 会话列表。

响应：

```json
{
  "code": 0,
  "message": "success",
  "data": [
    {
      "id": 1,
      "pet": 1,
      "pet_name": "豆豆",
      "title": "猫咪呕吐咨询",
      "model_provider": "ark_openai_compatible",
      "model_name": "doubao-seed-2-0-mini-260428",
      "status": "active",
      "created_at": "2026-05-24T10:00:00+08:00",
      "updated_at": "2026-05-24T10:00:00+08:00"
    }
  ]
}
```

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

后端会自动读取宠物基础档案、最近健康记录和最近体重记录，并拼接为模型上下文。`pet_id` 必须属于当前登录用户。

请求：

```json
{
  "pet_id": 1,
  "conversation_id": null,
  "message": "狗狗拉稀一天了，但是精神还可以，应该怎么办？",
  "image_urls": []
}
```

模型输出如果不是合法 JSON，后端会保存原始文本并构造 fallback 结构，确保接口仍返回统一结构化 `result`。

响应：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "conversation_id": 10,
    "message_id": 22,
    "reply": "根据你的描述...",
    "mode": "health_consultation",
    "health_result": {
      "risk_level": "medium",
      "summary": "宠物出现腹泻症状，当前精神尚可。",
      "possible_causes": ["饮食变化", "肠胃不适", "寄生虫或感染可能"],
      "home_care": ["观察精神和食欲", "保证饮水", "暂时避免更换食物"],
      "need_vet": true,
      "warning_signs": ["持续腹泻超过24-48小时", "便血", "精神明显变差"],
      "questions_to_ask": ["是否有呕吐？", "是否更换过食物？"],
      "disclaimer": "本结果由 AI 根据你提供的信息生成，仅供养宠护理参考，不能替代专业兽医诊断。如宠物出现持续呕吐、呼吸困难、抽搐、大量出血、精神极差、误食毒物等情况，请立即联系线下宠物医院。"
    },
    "action_drafts": [],
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

`mode` 可能为 `daily_care`、`health_consultation`、`record_intent`、`mixed`、`unknown`。为兼容旧前端，响应仍保留 `result` 字段；新前端优先读取 `health_result` 和 `action_drafts`。

### GET /api/ai/conversations/{id}/action-drafts/

获取某会话下的动作草稿。

### POST /api/ai/action-drafts/{id}/confirm/

确认执行动作草稿。后端会再次校验 `request.user` 与宠物归属。

支持：

```text
create_weight_record
create_health_record
```

### POST /api/ai/action-drafts/{id}/cancel/

取消待确认动作草稿。已保存的动作不能重复执行，也不能取消。

---

## 6. 文件上传 API

### POST /api/files/upload/

上传图片文件。必须登录，使用 `multipart/form-data`，当前用于宠物头像等图片场景。

限制：

```text
允许类型：jpg / jpeg / png / webp
最大大小：5MB
文件字段：file
宠物头像 file_type：pet
```

请求：

```text
multipart/form-data
file=<image>
file_type=pet
```

上传成功后，前端将响应中的 `url` 写入 `Pet.avatar`。不要把 `uni.chooseImage` 返回的本地临时路径保存到数据库。

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

失败时保持统一错误格式：

```json
{
  "code": 40001,
  "message": "参数错误",
  "errors": {}
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
