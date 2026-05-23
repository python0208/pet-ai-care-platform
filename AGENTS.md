# AGENTS.md

本文件是 Codex / OpenCode / AI 编程工具在本仓库中进行开发时必须读取和遵守的规则。

---

## 1. 项目概述

本仓库是一个宠物 AI 养护平台，目标是同时支持：

```text
微信小程序
Android App
iOS App
```

项目核心能力：

```text
宠物档案管理
AI 健康咨询
生活服务预约
宠物商城
微信支付 / 支付宝支付
管理后台
```

---

## 2. 技术栈

### 后端

```text
Django
Django REST Framework
MySQL
Redis
Celery
JWT
```

### 前端

```text
uni-app
Vue3
TypeScript
Pinia
```

---

## 3. 开发总原则

1. 必须按 `docs/CODEX_EXEC_PLAN.md` 的 Phase 顺序开发。
2. 每次只执行一个 Phase，不要跨阶段一次性生成所有代码。
3. 每个 Phase 必须保证项目可启动、可测试、可回滚。
4. 修改前先阅读已有代码结构，不要重复创建同名模块。
5. 不要破坏已有接口、字段和页面。
6. 不要在代码中硬编码密钥、AppID、支付密钥、AI Key。
7. 所有密钥必须通过环境变量读取。
8. 所有用户数据必须按 user 隔离。
9. 所有涉及用户数据的接口都必须检查权限。
10. 新增模型后必须创建 migration。
11. 新增接口后必须补充 serializer、view、url 和基础测试。
12. 新增前端接口必须统一放入 `src/api/`。
13. 前端请求必须统一通过 `src/api/request.ts` 封装。
14. 不要直接相信前端传来的金额、用户 ID、订单状态、支付状态。
15. 支付状态只能以后端支付回调或主动查单为准。
16. AI 健康咨询不能写成医疗诊断，必须保留免责声明。

---

## 4. 项目目录规范

推荐结构：

```text
pet-ai-care-platform/
  README.md
  AGENTS.md
  docs/
    PRODUCT_SPEC.md
    ARCHITECTURE.md
    DATABASE_DESIGN.md
    API_SPEC.md
    CODEX_EXEC_PLAN.md

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

  frontend/
    package.json
    src/
      pages/
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

---

## 5. 后端开发规范

### 5.1 Django App 拆分

必须按业务拆分：

```text
common         通用模型、响应、分页、权限、异常
users          用户、认证、邮箱注册、邮箱密码登录、微信登录预留
pets           宠物档案、健康记录、体重记录
ai_chat        AI 会话、消息、咨询结果、提示词
services       生活服务、服务商、预约
shop           商品、购物车、订单、地址
payments       支付单、支付回调、支付日志
files          文件上传
notifications  消息提醒、疫苗驱虫提醒
```

认证模块当前统一使用邮箱注册、邮箱密码登录和微信小程序登录预留；当前 MVP 不使用邮箱验证码，手机号不作为登录方式。手机号如后续出现，只能作为收货地址、服务预约联系人等业务联系方式。

### 5.2 接口前缀

所有后端接口统一使用：

```text
/api/
```

示例：

```text
/api/auth/login/
/api/pets/
/api/ai/consult/
/api/shop/products/
/api/payments/create/
```

### 5.3 统一响应格式

成功：

```json
{
  "code": 0,
  "message": "success",
  "data": {}
}
```

失败：

```json
{
  "code": 40001,
  "message": "参数错误",
  "errors": {}
}
```

分页：

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

### 5.4 权限规则

必须满足：

1. 用户只能查看自己的宠物。
2. 用户只能查看自己的健康记录。
3. 用户只能查看自己的 AI 会话。
4. 用户只能查看自己的商城订单。
5. 用户只能查看自己的服务预约。
6. 管理员可以通过后台查看全量数据。
7. 前端传入的 `user_id` 不可信，后端必须以 `request.user` 为准。

### 5.5 支付规则

支付相关必须满足：

1. 前端不能直接修改订单支付状态。
2. 支付金额以后端订单金额为准。
3. 支付创建必须生成 `PaymentOrder`。
4. 支付回调必须记录 `PaymentNotifyLog`。
5. 支付回调必须幂等。
6. 重复回调不能重复发货、重复扣库存、重复改订单。
7. 开发环境允许 mock 支付，但 mock 支付也必须走 `PaymentOrder`。
8. 真实微信支付 / 支付宝支付 provider 通过配置启用。

### 5.6 AI 规则

AI 模块必须满足：

1. 不要在业务代码中写死某个大模型厂商。
2. 必须实现 provider 抽象层。
3. 大模型配置从环境变量读取。
4. AI 回复必须保存到数据库。
5. AI 咨询必须保留免责声明。
6. AI 输出尽量解析为结构化 JSON。
7. 模型失败时返回友好错误，不要把底层报错直接暴露给用户。
8. 不能输出明确医疗诊断、处方或药品剂量指导。

---

## 6. 前端开发规范

### 6.1 页面结构

推荐 TabBar：

```text
首页
档案
AI咨询
服务
我的
```

商城入口先放首页，后期可独立成 Tab。

### 6.2 前端目录

```text
src/
  api/
    request.ts
    auth.ts
    users.ts
    pets.ts
    ai.ts
    services.ts
    shop.ts
    payments.ts
    files.ts
  stores/
    auth.ts
    user.ts
    pet.ts
    cart.ts
  components/
    PetCard.vue
    HealthRecordItem.vue
    AiMessageBubble.vue
    ProductCard.vue
    ServiceProviderCard.vue
    EmptyState.vue
    LoadingState.vue
  utils/
    date.ts
    money.ts
    auth.ts
    upload.ts
  types/
    user.ts
    pet.ts
    ai.ts
    shop.ts
    service.ts
    payment.ts
```

### 6.3 前端体验要求

每个页面必须考虑：

1. 加载中状态；
2. 空状态；
3. 错误状态；
4. 未登录状态；
5. 无宠物状态；
6. 网络失败；
7. 按钮防重复点击；
8. 表单校验；
9. 支付失败重试；
10. AI 回复失败重试。

---

## 7. 测试要求

后端至少覆盖：

1. 未登录不能访问用户数据。
2. 用户 A 不能访问用户 B 的宠物。
3. 用户 A 不能访问用户 B 的订单。
4. 用户 A 不能访问用户 B 的 AI 会话。
5. 宠物创建参数校验。
6. 健康记录创建参数校验。
7. AI provider 失败时返回友好错误。
8. 库存不足不能下单。
9. 订单金额不能由前端伪造。
10. 支付回调幂等。

---

## 8. 禁止行为

Codex 不允许：

1. 一次性生成所有业务功能。
2. 删除已有文档。
3. 删除已有测试。
4. 硬编码 AI Key、支付密钥、数据库密码。
5. 在 AI 咨询中出现“确诊”“开药”“处方”等文案。
6. 让前端决定订单金额。
7. 让前端决定支付成功。
8. 不做权限校验就返回用户数据。
9. 将用户 A 的数据返回给用户 B。
10. 不经说明大规模重构已有代码。

---

## 9. 当前执行方式

每次接到任务时，先确认当前 Phase。

如果用户没有指定 Phase，默认从当前未完成的最早 Phase 开始。

完成每一轮后必须输出：

```text
1. 本轮完成内容
2. 修改/新增文件
3. 如何运行
4. 如何测试
5. 当前限制
6. 下一步建议
```

---

## 10. 给 Codex 的总指令

```text
你现在是本项目的工程开发助手。请严格阅读 README.md、AGENTS.md 和 docs 目录，按 Phase 逐步完成开发。

当前项目目标：开发一个宠物 AI 养护平台，支持微信小程序和 App。

后端：Django + DRF + MySQL。
前端：uni-app + Vue3 + TypeScript + Pinia。

请遵守以下规则：
1. 每次只执行一个 Phase。
2. 每次开发前先检查已有代码结构。
3. 不要破坏已有可运行功能。
4. 所有新增接口必须考虑权限。
5. 所有用户数据必须按 user 隔离。
6. AI 咨询必须保留免责声明，不能写成医疗诊断。
7. 支付必须通过后端统一 payment_order 处理。
8. 不要在代码中硬编码密钥。
9. 完成后给出变更摘要、运行命令、测试方式和下一步建议。

请从 docs/CODEX_EXEC_PLAN.md 中指定的 Phase 开始执行。
```
## Git 提交规范

1. 每个 Phase 完成并通过基础测试后，才允许创建一次 Git commit。
2. 不要在一个 Phase 未完成时频繁提交。
3. 提交前必须执行：
   - git status
   - git diff --stat
   - 后端基础测试
   - 前端类型检查或构建检查
4. 提交信息使用中文或英文均可，但必须清楚说明本次完成的 Phase。
5. 推荐提交格式：
   - chore: initialize project structure
   - feat(auth): add email auth and wechat login placeholder
   - feat(pets): add pet profile management
   - feat(ai): add AI health consultation
   - feat(shop): add product and order flow
   - feat(payment): add mock payment flow
   - feat(services): add service booking
   - docs: update project documentation
6. Codex 不要自动 push，除非用户明确要求。
7. Codex 每次提交前必须先展示本次变更摘要和测试结果。
