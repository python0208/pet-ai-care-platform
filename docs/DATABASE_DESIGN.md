# DATABASE_DESIGN.md

# 宠物 AI 养护平台数据库设计

数据库：MySQL 8.x

---

## 1. 核心关系

```text
User 1 - N Pet
Pet 1 - N HealthRecord
Pet 1 - N WeightRecord

User 1 - N AIConversation
Pet 1 - N AIConversation
AIConversation 1 - N AIMessage
AIConversation 1 - 1 AIConsultationResult

User 1 - N CartItem
User 1 - N Address
User 1 - N ShopOrder
ShopOrder 1 - N ShopOrderItem

ServiceProvider 1 - N ServiceItem
User 1 - N ServiceBooking
Pet 1 - N ServiceBooking

PaymentOrder 1 - 1 ShopOrder 或 ServiceBooking
```

---

## 2. users app

## 2.1 User

用户表。

字段建议：

```text
id                  bigint / uuid
email               varchar(254), unique
nickname            varchar(64)
avatar              varchar/url
gender              varchar(20)
wx_openid           varchar(128), unique, nullable
wx_unionid          varchar(128), nullable
app_openid          varchar(128), nullable
is_email_verified   bool
is_active           bool
is_staff            bool
is_superuser        bool
last_login          datetime
created_at          datetime
updated_at          datetime
```

说明：

- 第一阶段可以使用 Django 自定义用户模型。
- 登录以 email 和密码为主，同时支持微信小程序 openid 登录或绑定。
- 微信登录创建的用户如果没有邮箱，可使用系统内部占位邮箱保存唯一约束；接口对前端返回空邮箱，不伪造成真实邮箱。
- `wx_openid` 一个 openid 只能绑定一个用户；已登录用户调用 `/api/auth/wx-login/` 时可绑定微信。
- 当前 MVP 不使用邮箱验证码，is_email_verified 默认 false 且不影响登录。
- 手机号不属于认证模块字段，只能在收货地址、服务预约联系人等业务联系方式中出现。
- 用户资料不要和宠物资料混在一起。
- “我的”页面统计不单独建表，来自当前用户的 `Pet`、`AIConversation`、`AIActionDraft` 聚合查询。

---

## 3. pets app

## 3.1 Pet

宠物表。

```text
id          bigint
owner_id    fk users.User
name        varchar(64)
species     varchar(20)    # cat/dog/other
breed       varchar(64)
gender      varchar(20)    # male/female/unknown
birthday    date, nullable
avatar      varchar/url, blank
color       varchar(64), blank
weight      decimal(6,2), nullable
neutered    bool
remark      text
created_at  datetime
updated_at  datetime
```

规则：

- owner_id 必须来自 request.user。
- 用户只能访问自己的宠物。
- `Pet.owner_id` 是外键关系，一个用户可以拥有多只宠物；不得改成 OneToOne，也不得对 owner 做唯一约束。
- 新增第二只宠物不能覆盖第一只宠物；编辑或删除某一只宠物不应影响同一用户的其他宠物。
- 删除宠物可先物理删除，后期改软删除。
- pet.avatar 可为空；如果有值，保存 `/api/files/upload/` 返回的 URL，不能保存前端本地临时路径。
- 前端默认头像为 `frontend/src/static/images/default-pet-avatar.svg`。

---

## 3.2 HealthRecord

健康记录表。

```text
id                bigint
pet_id            fk pets.Pet
record_type       varchar(32)  # vaccine/deworm/medical/allergy/other
title             varchar(128)
record_date       date
next_remind_date  date, nullable
hospital          varchar(128), nullable
doctor            varchar(64), nullable
cost              decimal(10,2), nullable
description       text
attachments       json
created_at        datetime
updated_at        datetime
```

record_type：

```text
vaccine   疫苗
deworm    驱虫
medical   就诊
allergy   过敏
other     其他
```

规则：

- 健康记录必须属于某只宠物。
- 用户只能操作自己宠物下的健康记录。
- attachments 存储图片 URL 列表。
- 当前健康记录附件暂不做页面上传；文件上传能力先用于宠物头像。

---

## 3.3 WeightRecord

体重记录表。

```text
id          bigint
pet_id      fk pets.Pet
weight      decimal(6,2)
record_date date
remark      varchar/text
created_at  datetime
```

规则：

- 用于生成体重曲线。
- 同一天可以允许多条，也可以后期限制一条。
- 前端按 record_date 排序展示。
- 用户只能操作自己宠物下的体重记录。

---

## 4. ai_chat app

## 4.1 AIConversation

AI 会话表。

```text
id              bigint
user_id         fk users.User
pet_id          fk pets.Pet, nullable
title           varchar(128)
model_provider  varchar(64)
model_name      varchar(128)
status          varchar(32)  # active/archived/deleted
created_at      datetime
updated_at      datetime
```

规则：

- 用户只能查看自己的会话。
- pet_id 可为空，但建议健康咨询必须选择宠物。
- title 可以用用户第一句话自动生成。

---

## 4.2 AIMessage

AI 消息表。

```text
id              bigint
conversation_id fk ai_chat.AIConversation
role            varchar(20)   # system/user/assistant
content         text
image_urls      json
token_count     int
raw_response    json
created_at      datetime
```

规则：

- role 只能是 system/user/assistant。
- 用户上传图片时 image_urls 存 URL 列表。
- raw_response 保存模型原始返回，方便调试。

---

## 4.3 AIConsultationResult

AI 咨询结构化结果表。

```text
id              bigint
conversation_id fk ai_chat.AIConversation
risk_level      varchar(20)  # low/medium/high/unknown
summary         text
possible_causes json
home_care       json
warning_signs   json
questions_to_ask json
need_vet        bool
disclaimer      text
raw_json        json
created_at      datetime
```

规则：

- risk_level 必须限制枚举。
- 如果模型返回不是合法 JSON，后端也要保存文本回复，并尽量构造 fallback 结构。

---

## 4.4 PromptTemplate

提示词模板表。

```text
id          bigint
name        varchar(128)
scene       varchar(64)   # pet_health_consult
content     text
is_active   bool
version     varchar(32)
created_at  datetime
updated_at  datetime
```

规则：

- 同一 scene 只能有一个 active 模板。
- 提示词可以由后台维护。
- 第一阶段也可先通过 seed 数据初始化。
- Phase 3 默认 seed `pet_health_consult` 提示词，内容来自后端 `apps/ai_chat/prompts.py`。
- 当前 MySQL 环境不依赖条件唯一约束；应用层读取当前 scene 下第一个 active 模板。

---

## 4.5 AIActionDraft

AI 动作草稿表。

```text
id              bigint
user_id         fk users.User
pet_id          fk pets.Pet
conversation_id fk ai_chat.AIConversation
source_message_id fk ai_chat.AIMessage, nullable
action_type     varchar(64)  # create_weight_record/create_health_record
display_title   varchar(128)
confirm_text    varchar(255)
payload         json
status          varchar(32)  # pending/confirmed/cancelled/executed/failed
result_ref_type varchar(64)
result_ref_id   bigint, nullable
error_message   varchar(255)
created_at      datetime
updated_at      datetime
executed_at     datetime, nullable
```

规则：

- 模型只能生成动作草稿，不能直接写数据库。
- 用户确认后，后端再次以 `request.user` 校验宠物归属。
- 已 executed 的草稿不能重复执行，cancelled 的草稿不能执行。
- 当前支持写入体重记录和健康记录。

---

## 5. services app

## 5.1 ServiceProvider

服务商表。

```text
id              bigint
name            varchar(128)
provider_type   varchar(32)  # hospital/grooming/boarding/feeding/walking
logo            varchar/url
images          json
address         varchar(255)
longitude       decimal(10,7)
latitude        decimal(10,7)
phone           varchar(32)
business_hours  varchar(128)
description     text
rating          decimal(3,2)
status          varchar(32)  # active/inactive/pending
created_at      datetime
updated_at      datetime
```

provider_type：

```text
hospital  宠物医院
grooming  宠物美容
boarding  宠物寄养
feeding   上门喂养
walking   遛狗服务
```

---

## 5.2 ServiceItem

服务项目表。

```text
id                bigint
provider_id       fk services.ServiceProvider
name              varchar(128)
price             decimal(10,2)
duration_minutes  int
description       text
status            varchar(32)  # active/inactive
created_at        datetime
updated_at        datetime
```

---

## 5.3 ServiceBooking

服务预约表。

```text
id              bigint
user_id         fk users.User
pet_id          fk pets.Pet
provider_id     fk services.ServiceProvider
service_item_id fk services.ServiceItem
booking_time    datetime
contact_name    varchar(64)
contact_phone   varchar(32)
address         varchar(255)
remark          text
status          varchar(32)  # pending/confirmed/completed/cancelled
pay_status      varchar(32)  # unpaid/paid/refunded
amount          decimal(10,2)
created_at      datetime
updated_at      datetime
```

规则：

- 用户只能查看自己的预约。
- 管理员后台可以修改预约状态。
- 第一阶段可不强制支付服务预约，但结构要预留。

---

## 6. shop app

## 6.1 ShopCategory

商品分类表。

```text
id          bigint
name        varchar(64)
parent_id   fk self, nullable
sort_order  int
is_active   bool
created_at  datetime
updated_at  datetime
```

---

## 6.2 Product

商品表。

```text
id              bigint
category_id     fk shop.ShopCategory
name            varchar(128)
cover           varchar/url
images          json
price           decimal(10,2)
original_price  decimal(10,2)
stock           int
sales_count     int
description     text
status          varchar(32)  # draft/on_sale/off_sale
created_at      datetime
updated_at      datetime
```

规则：

- 第一阶段不做 SKU，单商品单价格。
- 后期可扩展 ProductSku。

---

## 6.3 CartItem

购物车表。

```text
id          bigint
user_id     fk users.User
product_id  fk shop.Product
quantity    int
selected    bool
created_at  datetime
updated_at  datetime
```

规则：

- 同一个用户同一个商品只保留一条购物车记录。
- quantity 必须大于 0。

---

## 6.4 Address

收货地址表。

```text
id          bigint
user_id     fk users.User
name        varchar(64)
phone       varchar(32)
province    varchar(64)
city        varchar(64)
district    varchar(64)
detail      varchar(255)
is_default  bool
created_at  datetime
updated_at  datetime
```

规则：

- 用户只能管理自己的地址。
- 同一用户只能有一个默认地址。

---

## 6.5 ShopOrder

商城订单表。

```text
id                bigint
user_id           fk users.User
order_no          varchar(64), unique
total_amount      decimal(10,2)
pay_amount        decimal(10,2)
freight_amount    decimal(10,2)
status            varchar(32)  # pending_payment/paid/shipped/completed/cancelled/refunded
pay_status        varchar(32)  # unpaid/paid/refunded
address_snapshot  json
remark            text
paid_at           datetime
created_at        datetime
updated_at        datetime
```

规则：

- order_no 后端生成。
- 金额以后端商品价格计算。
- 地址必须保存快照。
- 用户只能查看自己的订单。

---

## 6.6 ShopOrderItem

订单明细表。

```text
id              bigint
order_id        fk shop.ShopOrder
product_id      fk shop.Product
product_name    varchar(128)
product_cover   varchar/url
price           decimal(10,2)
quantity        int
subtotal        decimal(10,2)
created_at      datetime
```

规则：

- 必须保存商品快照。
- 不要只依赖 product_id 实时读取商品，因为商品价格和名称后续可能变化。

---

## 7. payments app

## 7.1 PaymentOrder

统一支付单表。

```text
id              bigint
user_id         fk users.User
payment_no      varchar(64), unique
business_type   varchar(32)  # shop_order/service_booking/vip
business_id     bigint
channel         varchar(32)  # wechat/alipay/mock
amount          decimal(10,2)
status          varchar(32)  # pending/paid/failed/closed/refunded
transaction_id  varchar(128)
prepay_data     json
paid_at         datetime
created_at      datetime
updated_at      datetime
```

规则：

- business_type + business_id 指向业务订单。
- amount 必须等于业务订单待支付金额。
- payment_no 后端生成。
- 支付状态变更必须幂等。

---

## 7.2 PaymentNotifyLog

支付回调日志表。

```text
id              bigint
channel         varchar(32)
payment_no      varchar(64)
raw_body        text/json
headers         json
verified        bool
process_result  text
created_at      datetime
```

规则：

- 所有支付回调必须记录。
- 验签失败也要记录。
- 便于排查支付问题。

---

## 8. files app

## 8.1 UploadedFile

上传文件表。

```text
id            bigint
user_id       fk users.User
file          file/path
file_url      varchar/url
file_type     varchar(32)  # avatar/pet/medical/ai/product/service
content_type  varchar(64)
size          int
created_at    datetime
```

规则：

- 限制图片类型。
- 只支持 jpg、jpeg、png、webp。
- 限制单文件大小为 5MB。
- 上传文件保存在 `MEDIA_ROOT/uploads/`，`media/` 不进入 Git。
- 宠物头像上传时 `file_type=pet`，Pet.avatar 保存返回的 file_url。
- 生产环境建议使用对象存储。

---

## 9. notifications app

## 9.1 Notification

通知表。

```text
id                 bigint
user_id            fk users.User
title              varchar(128)
content            text
notification_type  varchar(32)
is_read            bool
related_type       varchar(32)
related_id         bigint
created_at         datetime
```

---

## 9.2 ReminderTask

提醒任务表。

```text
id            bigint
user_id       fk users.User
pet_id        fk pets.Pet
title         varchar(128)
remind_at     datetime
remind_type   varchar(32)  # vaccine/deworm/medical/order/service
status        varchar(32)  # pending/sent/cancelled
created_at    datetime
updated_at    datetime
```

---

## 10. 索引建议

建议添加索引：

```text
User.email
User.wx_openid

Pet.owner_id

HealthRecord.pet_id
HealthRecord.record_type
HealthRecord.next_remind_date

WeightRecord.pet_id
WeightRecord.record_date

AIConversation.user_id
AIConversation.pet_id

AIMessage.conversation_id

Product.category_id
Product.status

CartItem.user_id
CartItem.product_id

ShopOrder.user_id
ShopOrder.order_no
ShopOrder.status

ServiceProvider.provider_type
ServiceProvider.status

ServiceBooking.user_id
ServiceBooking.pet_id
ServiceBooking.status

PaymentOrder.payment_no
PaymentOrder.business_type + business_id
PaymentOrder.status
```

---

## 11. 数据隔离要求

所有用户私有数据都必须通过 request.user 限制：

```text
Pet
HealthRecord
WeightRecord
AIConversation
AIMessage
ShopOrder
CartItem
Address
ServiceBooking
PaymentOrder
Notification
ReminderTask
```

必须测试用户 A 不能访问用户 B 的数据。
