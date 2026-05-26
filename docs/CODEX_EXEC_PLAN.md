# CODEX_EXEC_PLAN.md

# Codex 分阶段执行计划

本文件是 Codex 必须严格遵守的开发计划。

原则：

```text
一次只做一个 Phase
每个 Phase 可运行、可测试、可验收
不要跳阶段
不要一次性生成所有功能
```

---

## Phase 0：项目初始化

### 目标

搭建可运行的前后端基础工程。

### 后端任务

1. 创建 `backend/` 目录。
2. 初始化 Django 项目。
3. 创建 `config/` 配置目录。
4. 配置 Django REST Framework。
5. 配置 JWT。
6. 配置 CORS。
7. 配置 MySQL。
8. 配置环境变量读取。
9. 创建 `apps/common/`。
10. 实现统一响应格式。
11. 实现统一异常处理。
12. 实现通用分页。
13. 实现基础模型 `TimeStampedModel`。
14. 创建 `/api/health/` 接口。
15. 创建 `requirements.txt`。
16. 创建 `.env.example`。
17. 配置基础测试。

### 前端任务

1. 创建 `frontend/` 目录。
2. 初始化 uni-app + Vue3 + TypeScript 项目。
3. 配置 Pinia。
4. 配置基础页面。
5. 配置 TabBar。
6. 封装 `src/api/request.ts`。
7. 首页请求 `/api/health/`。
8. 首页显示后端连接状态。

### 验收标准

1. 后端可启动。
2. `/api/health/` 返回：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "status": "ok"
  }
}
```

3. 前端可启动。
4. 前端首页能显示后端连接状态。
5. README 中有启动说明。

### 给 Codex 的提示词

```text
请阅读 README.md、AGENTS.md 和 docs 目录。

现在执行 Phase 0：项目初始化。

要求：
1. 创建 backend Django 项目结构。
2. 配置 DRF、JWT、CORS、MySQL、环境变量读取。
3. 创建 common app，加入统一响应格式、统一异常处理、分页类、基础模型。
4. 创建 /api/health/ 接口，返回 { code: 0, message: "success", data: { status: "ok" } }。
5. 创建 frontend uni-app 项目结构，配置 Vue3、TypeScript、Pinia、request 封装、TabBar 基础页面。
6. 前端首页调用 /api/health/ 并显示连接状态。
7. 补充 README 中的本地启动方式。
8. 不要实现业务功能，先保证前后端基础工程可运行。

完成后请总结：
- 新增了哪些文件；
- 如何启动后端；
- 如何启动前端；
- 如何测试；
- 当前还有哪些未完成事项。
```

---

## Phase 1：邮箱注册与登录认证

### 目标

完成邮箱注册、邮箱密码登录、JWT 登录态、微信小程序登录预留和用户资料接口。当前 MVP 不使用邮箱验证码，手机号不作为认证登录方式。

### 后端任务

1. 创建 `apps/users/`。
2. 实现自定义 User 模型。
3. User 以 email 作为唯一登录标识，不包含 phone 认证字段。
4. 实现邮箱注册接口 `/api/auth/register/`。
5. 实现邮箱密码登录接口 `/api/auth/login/`。
6. 注册和登录是两个明确动作，不做登录时自动注册。
7. 不创建 SmsCode、EmailCode 或 EmailVerificationCode 模型。
8. 不实现手机号验证码或邮箱验证码接口。
9. 实现微信小程序登录接口预留。
10. 真实微信 code2session 逻辑通过 provider 封装。
11. mock 微信登录通过环境变量控制。
12. 实现 JWT token 返回和刷新接口。
13. 实现 `/api/users/me/`。
14. 实现用户资料更新。
15. 添加权限测试。

### 前端任务

1. 登录页。
2. 注册页或登录/注册 Tab。
3. 邮箱、密码表单。
4. token 保存。
5. 登录拦截。
6. 我的页面显示默认头像、昵称、邮箱。
7. 退出登录。

### 验收标准

1. 邮箱和密码可以注册。
2. 邮箱和密码可以登录。
2. 登录后返回 access_token 和 refresh_token。
3. 登录后可以访问 `/api/users/me/`。
4. 未登录访问 `/api/users/me/` 返回 401。
5. 前端可以完成注册/登录并进入我的页面。
6. 项目中没有短信验证码或邮箱验证码登录入口。

### 给 Codex 的提示词

```text
请在当前项目基础上执行 Phase 1：邮箱注册与登录认证。

要求：
1. 后端创建 users app。
2. 实现自定义 User 模型，至少包含 email、nickname、avatar、gender、wx_openid、wx_unionid、app_openid、is_email_verified、is_active、is_staff。
3. email 必须唯一，使用 Django 密码哈希机制保存密码。
4. 实现邮箱注册接口 /api/auth/register/，注册成功返回 access_token、refresh_token 和 user 信息。
5. 实现邮箱密码登录接口 /api/auth/login/，登录成功返回 access_token、refresh_token 和 user 信息。
6. 实现 /api/auth/token/refresh/。
7. 实现微信小程序登录接口，先允许 mock code 登录，真实 code2session 逻辑通过 provider 封装并读取环境变量。
8. 实现 /api/users/me/ 获取和更新用户资料。
9. 所有需要登录的接口必须使用 JWT 鉴权。
10. 前端实现登录/注册页面、token 保存、登录拦截、我的页面显示默认头像、昵称和邮箱。
11. 不创建 SmsCode、EmailCode、EmailVerificationCode 模型，不实现短信或邮箱验证码接口。
12. 补充必要的后端测试。

验收：
- 邮箱和密码可以注册。
- 邮箱和密码可以登录。
- 登录后可以访问 /api/users/me/。
- 未登录访问 /api/users/me/ 返回 401。
- 登录/注册页没有手机号和验证码入口。
```

---

## Phase 2：宠物档案管理

### 目标

完成宠物档案、健康记录、体重记录。本阶段只开发 pets app，不开发 AI、商城、支付、生活服务预约等业务逻辑。

### 后端任务

1. 创建 `apps/pets/`。
2. 实现 Pet 模型。
3. 实现 HealthRecord 模型。
4. 实现 WeightRecord 模型。
5. 实现宠物 CRUD。
6. 实现健康记录 CRUD。
7. 实现体重记录接口。
8. 实现用户数据隔离。
9. 宠物头像本阶段保存 URL；如果为空，前端使用默认头像。
10. 添加权限测试。

### 前端任务

1. 宠物列表页。
2. 宠物新增页。
3. 宠物编辑页。
4. 宠物详情页。
5. 健康记录列表。
6. 健康记录新增 / 编辑。
7. 体重记录页。
8. 体重曲线。
9. 首页展示当前宠物卡片。
10. 首页展示最近提醒。

### 验收标准

1. 用户可以创建多个宠物。
2. 用户可以编辑宠物资料。
3. 用户可以添加疫苗、驱虫、就诊、过敏记录。
4. 用户可以添加体重记录。
5. 前端能显示体重曲线。
6. 用户 A 不能访问用户 B 的宠物。

### 给 Codex 的提示词

```text
请执行 Phase 2：宠物档案管理。

要求：
1. 后端创建 pets app。
2. 实现 Pet、HealthRecord、WeightRecord 模型。
3. 实现宠物 CRUD 接口。
4. 实现健康记录 CRUD 接口。
5. 实现体重记录接口。
6. 实现权限：用户只能访问自己的宠物和记录。
7. 实现宠物头像上传或复用 files app 上传接口。
8. 前端实现宠物列表、宠物详情、新增/编辑宠物、健康记录、体重曲线页面。
9. 首页展示当前宠物卡片和最近提醒。
10. 补充测试：用户不能访问其他用户宠物。
11. 默认宠物头像路径：`frontend/src/static/images/default-pet-avatar.svg`。

验收：
- 用户可以创建多个宠物。
- 用户可以添加疫苗、驱虫、就诊、过敏记录。
- 用户可以记录体重并看到体重曲线展示区域。
- 其他用户数据不可访问。
```

---

## Phase 2.1：宠物头像本地上传与档案页美化

### 目标

补齐宠物头像本地上传能力，并按照 `docs/page/archive_page.png` 重构档案管理页视觉。

### 后端任务

1. 创建 `apps/files/`。
2. 实现 `UploadedFile` 模型。
3. 实现 `POST /api/files/upload/`。
4. 上传接口必须登录，只支持 multipart/form-data。
5. 仅允许 jpg、jpeg、png、webp 图片。
6. 单文件最大 5MB。
7. 上传成功返回文件 URL。
8. DEBUG 模式支持访问 `MEDIA_URL`。
9. `media/` 和 `staticfiles/` 不进入 Git。
10. 补充上传接口测试。

### 前端任务

1. 宠物新增/编辑页支持点击头像选择本地图片。
2. 使用 `uni.chooseImage` 选择相册或相机图片。
3. 使用 `uni.uploadFile` 上传到 `/api/files/upload/`。
4. 上传时带 `Authorization: Bearer <access_token>`。
5. 上传成功后将返回 URL 写入 `Pet.avatar`。
6. 不能保存本地临时路径。
7. 档案管理页使用 `archive_page_assets_pack/` 资源，运行时复制到 `frontend/src/static/icons/archive/`。
8. 档案页包含宠物资料主卡片、6 个档案模块、近期记录、体重趋势。
9. 默认宠物头像 fallback 为 `frontend/src/static/images/default-pet-avatar.svg`。

---

## Phase 2.2：档案页体验修复与多宠物档案支持

### 目标

修复档案管理页字体、卡片布局和中文溢出问题，并让一个用户可以清晰管理多只宠物。

### 后端检查

1. `Pet.owner` 必须保持 `ForeignKey`，关系为 `User 1 - N Pet`。
2. `GET /api/pets/` 必须返回当前登录用户的全部宠物。
3. 新增第二只宠物不能覆盖第一只宠物。
4. 编辑或删除某一只宠物不能影响同一用户的其他宠物。
5. 用户 A 不能看到用户 B 的宠物。

### 前端任务

1. 档案页维护 `pets`、`selectedPetId`、`selectedPet`、`healthRecords`、`weightRecords`。
2. 进入档案页时请求 `/api/pets/`，默认选中上次保存的 `selectedPetId`；如果不存在，则选中第一只宠物。
3. 档案页增加横向宠物头像切换区域，包含全部宠物和“新增”入口。
4. 切换宠物时刷新主卡片、档案模块、近期记录和体重趋势。
5. 新增/编辑宠物成功后回到档案页并重新加载列表。
6. 删除当前宠物后自动切换到剩余第一只宠物；没有宠物时显示空状态。
7. UI 需适配 375px、390px、414px 常见手机宽度，长中文使用省略号，避免图标、文字和按钮互相挤压。

---

## Phase 3：AI 健康咨询

### 目标

完成 AI 聊天闭环。

### 后端任务

1. 创建 `apps/ai_chat/`。
2. 实现 AIConversation。
3. 实现 AIMessage。
4. 实现 AIConsultationResult。
5. 实现 PromptTemplate。
6. 实现 AI provider 抽象层。
7. 支持 OpenAI-compatible API。
8. 支持 MockAIProvider。
9. 通过环境变量配置 AI。
10. 实现 `/api/ai/consult/`。
11. 自动读取宠物档案和健康记录摘要。
12. 拼接系统提示词。
13. 调用模型。
14. 解析结构化 JSON。
15. 保存用户消息和 AI 回复。
16. 模型失败时返回友好错误。

### 当前实现补充

Phase 3 默认通过 OpenAI-compatible Provider 接入火山方舟 Doubao：

```text
AI_PROVIDER=ark_openai_compatible
AI_API_BASE=https://ark.cn-beijing.volces.com/api/v3
AI_MODEL=doubao-seed-2-0-mini-260428
AI_TIMEOUT_SECONDS=60
AI_TEMPERATURE=0.3
AI_MAX_TOKENS=1200
```

`AI_API_KEY` 只能手动写入本地 `backend/.env`，不得写入代码、文档、测试文件或前端。`DEBUG=True` 且 key 为空时允许回退到 `MockAIProvider`；生产环境 key 缺失时应返回配置错误。AI 咨询必须读取当前用户自己的宠物档案上下文，用户不能使用其他用户的宠物发起咨询。

### 前端任务

1. AI 会话列表。
2. AI 聊天页。
3. 宠物选择。
4. 快捷问题标签。
5. 图片上传。
6. AI 回复展示。
7. 风险等级卡片。
8. 免责声明展示。
9. AI 失败重试。

### 验收标准

1. 用户可以选择宠物发起咨询。
2. 后端可以调用 mock 或真实模型。
3. AI 回复保存到历史会话。
4. 结果卡片包含风险等级、可能原因、护理建议、就医建议。
5. 模型失败时前端显示友好错误。
6. 文案不能出现“确诊”“开药”“处方”。

---

## Phase 3.1：AI 聊天体验优化 + 养宠助手能力扩展 + 档案记录动作草稿

### 目标

在 Phase 3 的 AI 健康咨询基础上，扩展为 AI 养宠助手，并支持用户确认后写入宠物档案记录。

### 后端任务

1. 升级默认 system prompt 为“宠护星球 AI 养宠助手”。
2. 支持 `daily_care`、`health_consultation`、`record_intent`、`mixed`、`unknown`。
3. 新增 `AIActionDraft`。
4. 实现动作草稿列表、确认、取消接口。
5. 确认 `create_weight_record` 时写入 `WeightRecord`。
6. 确认 `create_health_record` 时写入 `HealthRecord`。
7. 所有确认动作必须校验 `request.user` 和宠物归属。

### 前端任务

1. 优化 AI 聊天页移动端布局。
2. 展示已上传图片和历史图片消息。
3. 展示动作确认卡片。
4. 支持确认保存和取消动作草稿。
5. 增加健康咨询、日常养护、档案记录快捷问题。

### 验收标准

1. AI 可以回答日常养护问题。
2. AI 可以生成体重记录和健康记录动作草稿。
3. 用户确认后才能写入数据库。
4. 用户不能确认别人的动作草稿。
5. 用户不能通过动作草稿给别人的宠物写记录。
6. 图片消息在聊天中可见。

---

## Phase 3.2：AI 聊天页面体验修复与动作草稿状态修正

### 目标

修复 AI 聊天页移动端布局、滚动区域、底部输入栏遮挡、快捷问题溢出、图片消息展示和动作草稿状态展示问题。

### 前端任务

1. 顶部区域保持紧凑，免责声明改为轻量提示条。
2. 宠物选择区改为横向轻量头像切换条。
3. 快捷问题改为分组 tab + 单行横向滚动 chip。
4. 消息滚动区为页面主体，并为固定输入栏、图片预览和 safe area 预留底部空间。
5. 用户消息、AI 回复、健康结果卡片和动作草稿卡片保持清晰层级。
6. 图片消息在发送前、发送后和历史消息中都可见。
7. action draft 状态以前端收到的后端 `status` 为准，`pending` 显示待确认，`executed` 才显示已保存。

### 后端检查

1. `AIActionDraft` 默认状态为 `pending`。
2. `/api/ai/consult/` 创建草稿后返回 `pending`。
3. 只有确认接口会执行写库。
4. 确认后状态为 `executed`，取消后状态为 `cancelled`。
5. 已保存和已取消的草稿不能重复执行。
6. 用户不能确认别人的草稿，也不能通过草稿写入别人的宠物档案。

### 验收标准

1. 375px / 390px / 414px 常见手机宽度不明显错位。
2. 快捷问题不裁切、不横向溢出。
3. 底部输入栏不遮挡最后一条消息或动作草稿卡片。
4. pending 草稿不显示“已保存”，点击确认成功后才显示“已保存”。
5. 当前阶段仍使用非流式 HTTP 请求，不做 SSE/WebSocket 流式输出。

---

## Phase 3.3：AI 咨询首页单页结构压缩与移动端体验优化

### 目标

按 `docs/page/ai_page.png` 原型重构 AI 咨询首页，压缩单页结构，降低首屏压力，让历史咨询更早出现，并修复快捷问题展开过多、TabBar 遮挡和移动端横向溢出风险。

### 前端任务

1. 保持 `pages/ai/index` 为单页滚动结构，不拆分路由。
2. 优先使用 `ai_consult_page_icon_pack/` 中的图标资源，并将运行时使用的 PNG 复制到 `frontend/src/static/icons/ai/`。
3. 顶部 Hero 区、机器人插画和免责声明按原型改为轻量紧凑样式。
4. 宠物选择区改为横向轻量头像列表，支持多宠物切换和添加入口。
5. 新咨询入口改为输入式入口，点击后带上当前 `selectedPetId` 进入聊天详情页。
6. 快捷问题改为分类 tab + 当前分类 chips。
7. 历史咨询区提前展示，列表项显示标题、宠物名称、日期、类型标签和待确认记录提示。
8. 页面底部为 TabBar 和 safe area 预留空间，避免最后一条历史记录被遮挡。

### 后端轻量补充

1. 会话列表可在不破坏旧字段的前提下补充 `pending_action_count`。
2. 不重构 `/api/ai/consult/`，不影响聊天详情页、图片消息和 action draft 确认流程。

### 验收标准

1. AI 咨询首页仍是同一个页面。
2. 快捷问题只展示当前分类，chip 不被裁切。
3. 宠物切换后，新咨询和快捷问题使用当前宠物。
4. 历史咨询比之前更早出现，最后一条不被 TabBar 遮挡。
5. 375px / 390px / 414px 宽度下不明显错位。
6. 当前阶段仍使用非流式 HTTP 请求，不做 SSE/WebSocket 流式输出。

---

## Phase 3.4：我的页面 UI 完善 + 微信登录预留/小程序登录实现

### 目标

完善“我的”页面，并把 Phase 1 的微信登录预留补齐为可用的小程序登录能力。当前不开发商城、支付、生活服务预约，也不恢复手机号登录。

### 后端任务

1. `POST /api/auth/wx-login/` 支持 `platform=miniapp`。
2. 小程序端使用 `WECHAT_MINI_APPID`、`WECHAT_MINI_SECRET` 调微信 code2session 换取 openid。
3. `DEBUG=True` 且 `WECHAT_LOGIN_MOCK_ENABLED=true` 时支持 mock 微信登录。
4. App 微信登录仅配置预留，未配置时返回“App 微信登录暂未配置”。
5. 已登录用户调用 wx-login 时可绑定微信 openid；同一 openid 不能绑定多个用户。
6. 不向前端返回 `session_key`。
7. `/api/users/me/` 返回 `has_wechat_bound` 和 `auth_providers`。
8. 新增 `/api/users/me/summary/`，统计当前用户宠物数、AI 会话数和待确认动作草稿数。

### 前端任务

1. 重构 `pages/user/index`，未登录展示登录引导，已登录展示头像、昵称、邮箱、微信绑定状态和登录方式标签。
2. 我的页面展示“我的宠物 / 咨询记录 / 待确认记录”三项统计。
3. 功能入口分为养宠管理、服务与商城、设置；未实现功能只提示“功能开发中”。
4. 登录页增加微信登录入口：微信小程序显示“微信一键登录”，开发模式可显示 mock 登录。
5. 不出现手机号登录、短信验证码、邮箱验证码入口。
6. 退出登录需要二次确认，并清理本地 token。

### 验收标准

1. 邮箱注册和邮箱密码登录仍可用。
2. 微信小程序登录接口可用，mock 微信登录可用于本地开发。
3. 没有真实微信配置时系统不崩溃。
4. 我的页面在 375px / 390px / 414px 下布局正常，底部 TabBar 不遮挡内容。
5. App 微信登录仅说明预留，不假装真实可用。
6. 不提交 `.env`，不把 AppID、Secret 写入代码或文档。

### 给 Codex 的提示词

```text
请执行 Phase 3：AI 健康咨询模块。

要求：
1. 后端创建 ai_chat app。
2. 实现 AIConversation、AIMessage、AIConsultationResult、PromptTemplate 模型。
3. 实现 AI provider 抽象层，支持 OpenAI-compatible API 和 MockAIProvider。
4. 通过环境变量配置 AI_API_BASE、AI_API_KEY、AI_MODEL。
5. 实现 /api/ai/consult/ 接口：用户传入 pet_id、message、image_urls，后端读取宠物档案并拼接提示词，调用模型。
6. AI 输出必须尽量解析为结构化 JSON，包含 risk_level、summary、possible_causes、home_care、need_vet、warning_signs、disclaimer。
7. 保存用户消息和 AI 回复。
8. 前端实现 AI 会话列表和聊天页面。
9. 支持选择宠物、输入文字、上传图片、显示 AI 回复、显示风险等级卡片。
10. 必须展示免责声明。
11. 模型失败时要有友好错误提示。

注意：
不要把 AI 功能写成医疗诊断，不要出现“确诊”“开药”“处方”等表达。
```

---

## Phase 4.0：商品后台管理与 Excel 批量导入

### 目标

先完成商城模块的数据管理基础能力，供管理员在 Django Admin 中维护商品，并通过 Excel 批量导入商品、库存和商品图片。本阶段不开发商城前端商品展示、购物车、订单、支付、优惠券或物流。

### 后端任务

1. 创建 `apps/shop/`。
2. 实现 `ProductCategory`、`Product`、`ProductInventory`、`ProductImportBatch`、`ProductImportRow`。
3. 注册 Django Admin，可管理分类、商品、库存、导入批次和导入明细。
4. 在 Admin 中增加“商品 Excel 批量导入”入口。
5. 支持上传 `.xlsx` 文件，字段为：图片、名称、单位、进货价、规格、零售价、条码、重量、直营店序号、分类、保质期（月）、当前库存。
6. 使用 `openpyxl` 解析 Excel 和嵌入图片。
7. 商品图片保存到 `media/products/`，原始 Excel 保存到 `media/imports/products/`，数据库只保存路径。
8. `barcode` 作为商品唯一识别字段，新增或更新 Product。
9. `Product` 与 `ProductInventory` 分表；同一 `product + store_code` 只有一条库存。
10. “直营店序号”允许为空，空值归入默认库存，内部 `store_code=DEFAULT`，后台展示“默认库存”。
11. 行级失败写入 `ProductImportRow`，不影响其他行继续导入。

### 验收标准

1. 后端可启动，数据库迁移成功。
2. Admin 可看到商品分类、商品、库存、导入批次和导入明细。
3. staff / superuser 可访问导入入口，普通用户不能访问。
4. 可以上传 `.xlsx` 并解析商品字段。
5. 条码不存在时新增商品，条码存在时更新商品。
6. 当前库存写入 `ProductInventory`。
7. 直营店序号为空时写入 `DEFAULT` 默认库存，重复导入更新同一条库存。
8. Excel 嵌入图片保存到 `media/products/`，图片文件不进入 Git。
9. 本阶段不做购物车、订单、支付。

---

## Phase 4：商城模块

### 目标

完成商品浏览、购物车、地址、订单创建。

---

## Phase 4.1：商城商品展示接口与前端商城页面

### 目标

基于 Phase 4.0 已导入的商品数据，提供用户端商品只读接口和移动端商城展示页面。本阶段不开发购物车、订单、支付、优惠券、物流、售后、评价或库存扣减。

### 后端任务

1. 实现 `GET /api/shop/categories/`，只返回启用分类。
2. 实现 `GET /api/shop/products/`，只返回 `status=active` 商品。
3. 商品列表支持 `q`、`category_id`、`barcode`、分页和价格/最新排序。
4. 实现 `GET /api/shop/products/{id}/`。
5. 商品列表和详情返回 `cover_image_url`、`total_stock`、`stock_status`。
6. 用户端接口不返回 `purchase_price`、导入批次或导入明细。
7. 普通用户不能通过商品 API 创建、修改、删除商品。

### 前端任务

1. TabBar 第四项从“服务”改为“商城”，页面路径为 `pages/shop/index`。
2. 服务页面保留，但暂不作为主 Tab 入口。
3. 新增 `frontend/src/api/shop.ts`。
4. 新增商城首页 `pages/shop/index`，参考 `docs/page/shop.png`。
5. 新增商品详情页 `pages/shop/detail`。
6. 将 `shop_page/header.png` 和 `shop_page/center.png` 复制到 `frontend/src/static/images/shop/`。
7. 新增默认商品图 `frontend/src/static/images/default-product.svg`。
8. 首页“精选商城”接入真实商品数据，接口失败不影响首页其他模块。

### Phase 4.1.1：商城页面 UI 体验修复与商品图片显示修复

目标是在不开发购物车、订单、支付、优惠券、物流和售后的前提下，修复商城真实图片展示和移动端体验问题。

1. 后端 `cover_image_url` 兼容 `products/xxx`、`/media/products/xxx`、完整 URL，并避免向前端暴露本地文件系统路径。
2. 商品列表、商品详情和首页精选商城优先使用 `cover_image_url`，图片加载失败时回退 `default-product.svg`。
3. 商城商品卡片优化为紧凑两列布局，商品名最多两行省略，价格和有货/缺货标签底部对齐。
4. 商城页滚动容器增加 TabBar 与 safe area 底部留白，避免最后一行商品被底部导航遮挡。
5. 顶部 Header、精选好物 Banner、分类 Tab、搜索框和扫码占位入口按 `docs/page/shop.png` 继续精修。
6. 补充商品加载中、接口失败、搜索无结果、分类加载失败和图片加载失败 fallback 状态。
7. 当前阶段仍不做真实购物车、下单、支付、售后或库存扣减。

### Phase 4.1.2：商城列表分页加载更多与商品图片路径修复

目标是让商城可以浏览超过第一页的商品，并稳定展示后台导入到 `media/products/` 的条码图片。

1. `GET /api/shop/products/` 支持 `page`、`page_size`，分页响应包含 `count`、`page`、`page_size`、`total_pages`、`has_next`、`has_previous` 和 `results`。
2. 商城首页首次加载第一页，滚动到底部根据 `has_next` 加载下一页并追加到列表。
3. 下拉刷新、分类切换、搜索、清空搜索时重置 `page=1`，清空旧列表并重新请求。
4. 加载更多时展示底部 loading，失败时可点击重试，没有更多时展示“没有更多商品了”。
5. 商品图片 URL 兼容 `products/<barcode>.jpg`、`/media/products/<barcode>.jpg`、`media/products/<barcode>.jpg`、`.jpeg`、`.png`、`.webp` 和完整 URL。
6. 当 `cover_image` 为空或文件不存在时，后端按 `media/products/<barcode>.jpg|jpeg|png|webp` 查找兜底；仍未找到则返回空，前端使用默认商品图。
7. 前端统一通过 `resolveProductImage()` 处理商品图，并将 localhost/127.0.0.1 media 图片地址改写到当前 API_ORIGIN，避免移动端访问本机回环地址失败。
8. 当前阶段仍不做购物车、订单、支付、物流、售后或库存扣减。

### 验收标准

1. 商品分类、列表、详情接口可用。
2. 商品图片 URL 前端可展示。
3. 商品列表和详情不显示进货价。
4. 商城 Tab 可进入商城页面。
5. 分类 Tab、搜索、详情跳转可用。
6. 加入购物车按钮只提示开发中。
7. 不影响首页、档案、AI 咨询、我的页面。

### 后端任务

1. 创建 `apps/shop/`。
2. 实现 ShopCategory。
3. 实现 Product。
4. 实现 CartItem。
5. 实现 Address。
6. 实现 ShopOrder。
7. 实现 ShopOrderItem。
8. 实现商品分类接口。
9. 实现商品列表和详情。
10. 实现购物车。
11. 实现地址管理。
12. 实现订单创建。
13. 实现库存校验。
14. 实现金额后端计算。
15. 实现订单查询。

### 前端任务

1. 商城首页。
2. 分类页。
3. 商品列表。
4. 商品详情。
5. 购物车。
6. 地址列表。
7. 地址编辑。
8. 订单确认。
9. 我的订单。
10. 订单详情。

### 验收标准

1. 用户可以浏览商品。
2. 用户可以加入购物车。
3. 用户可以选择地址。
4. 用户可以创建订单。
5. 库存不足时不能下单。
6. 订单金额以后端计算为准。
7. 用户只能查看自己的订单。

### 给 Codex 的提示词

```text
请执行 Phase 4：商城模块。

要求：
1. 后端创建 shop app。
2. 实现 ShopCategory、Product、CartItem、Address、ShopOrder、ShopOrderItem 模型。
3. 实现商品分类、商品列表、商品详情接口。
4. 实现购物车增删改查。
5. 实现地址管理。
6. 实现订单创建接口，订单金额必须以后端商品价格计算为准。
7. 实现订单列表和订单详情。
8. 实现库存校验，库存不足不能下单。
9. 前端实现商城首页、商品列表、商品详情、购物车、地址、订单确认、我的订单。
10. 管理后台可管理分类、商品和订单。

验收：
- 用户可以浏览商品并加入购物车。
- 用户可以选择地址并创建订单。
- 库存不足时下单失败。
- 用户只能查看自己的订单。
```

---

## Phase 5：支付模块

### 目标

完成统一支付架构和 mock 支付。

### 后端任务

1. 创建 `apps/payments/`。
2. 实现 PaymentOrder。
3. 实现 PaymentNotifyLog。
4. 实现统一支付创建接口。
5. 实现 mock 支付 provider。
6. 预留微信支付 provider。
7. 预留支付宝支付 provider。
8. 实现支付状态查询。
9. 实现 mock 支付成功接口。
10. 实现支付回调结构。
11. 实现幂等处理。
12. 支付成功后同步更新业务订单。

### 前端任务

1. 订单确认页创建支付单。
2. 拉起 mock 支付。
3. 支付结果页。
4. 订单详情显示支付状态。
5. 支付失败重试。

### 验收标准

1. 开发环境可以 mock 支付成功。
2. 支付成功后商城订单状态变为 paid。
3. 重复调用 mock 支付成功不会重复处理。
4. 前端不能直接修改订单支付状态。

### 给 Codex 的提示词

```text
请执行 Phase 5：支付模块。

要求：
1. 后端创建 payments app。
2. 实现 PaymentOrder、PaymentNotifyLog 模型。
3. 实现统一支付创建接口 /api/payments/create/。
4. 支持 business_type=shop_order 和 service_booking。
5. 实现 mock 支付 provider，开发环境可模拟支付成功。
6. 预留 WeChatPayProvider 和 AlipayProvider，不需要真实密钥也能运行。
7. 实现微信支付回调接口和支付宝支付回调接口的结构，真实验签逻辑可用 TODO 标记，但必须有幂等处理框架。
8. 支付成功后更新 PaymentOrder 状态，并同步更新业务订单支付状态。
9. 前端订单确认页接入支付创建接口。
10. 前端实现支付结果页。

验收：
- 开发环境可以 mock 支付成功。
- 支付成功后商城订单状态变为 paid。
- 重复调用 mock 支付成功不会重复处理。
- 前端不能直接修改订单支付状态。
```

---

## Phase 6：生活服务模块

### 目标

完成服务商展示和预约。

### 后端任务

1. 创建 `apps/services/`。
2. 实现 ServiceProvider。
3. 实现 ServiceItem。
4. 实现 ServiceBooking。
5. 实现服务商列表。
6. 实现附近服务商。
7. 实现服务商详情。
8. 实现服务项目列表。
9. 实现服务预约。
10. 实现我的预约。
11. 管理后台可维护服务商和预约状态。

### 前端任务

1. 服务首页。
2. 服务商列表。
3. 服务商详情。
4. 服务预约页。
5. 我的预约。
6. 预约详情。
7. 取消预约。

### 验收标准

1. 用户可以浏览宠物医院、美容、寄养、上门喂养服务。
2. 用户可以为自己的宠物提交预约。
3. 用户只能查看自己的预约。
4. 管理员可以修改预约状态。

### 给 Codex 的提示词

```text
请执行 Phase 6：生活服务模块。

要求：
1. 后端创建 services app。
2. 实现 ServiceProvider、ServiceItem、ServiceBooking 模型。
3. 实现服务商列表、附近服务商、服务商详情、服务项目列表接口。
4. 实现服务预约接口和我的预约接口。
5. 用户只能查看自己的预约。
6. 管理后台可以维护服务商、服务项目、预约状态。
7. 前端实现服务首页、服务商列表、服务商详情、预约页面、我的预约。

验收：
- 用户可以浏览宠物医院、美容、寄养、上门喂养服务。
- 用户可以为自己的宠物提交预约。
- 管理员可以修改预约状态。
```

---

## Phase 7：管理后台与上线准备

### 目标

项目具备基本运营和上线条件。

### 后端任务

1. 优化 Django Admin。
2. 商品后台管理。
3. 订单后台管理。
4. 用户后台管理。
5. 宠物后台管理。
6. AI 记录后台查看。
7. 服务商后台管理。
8. 预约后台管理。
9. 支付记录后台管理。
10. 首页配置预留。
11. 用户协议接口或静态页面。
12. 隐私政策接口或静态页面。

### 前端任务

1. 用户协议页面。
2. 隐私政策页面。
3. 关于我们页面。
4. 账号注销入口。
5. App 打包配置。
6. 微信小程序提审配置检查。
7. 空状态、错误状态、加载状态完善。

### 验收标准

1. 管理员可以维护商品、订单、服务商。
2. 管理员可以查看 AI 咨询记录。
3. 管理员可以处理预约。
4. 用户协议和隐私政策可访问。
5. 项目具备小程序提审基础条件。

---

## 8. 每轮完成后的固定输出格式

Codex 每轮完成后必须输出：

```text
## 本轮完成内容

## 新增/修改文件

## 如何运行后端

## 如何运行前端

## 如何测试

## 当前限制

## 下一步建议
```

---

## 9. 最终 MVP 验收流程

最终必须能演示：

```text
用户打开微信小程序
→ 使用邮箱注册或邮箱密码登录
→ 创建一只宠物
→ 添加疫苗/驱虫/体重记录
→ 进入 AI 健康咨询
→ 选择宠物并描述症状
→ AI 返回风险等级和护理建议
→ 用户进入商城
→ 选择商品加入购物车
→ 提交订单
→ mock 支付成功
→ 订单变为已支付
→ 用户进入服务页面
→ 选择宠物医院或美容服务
→ 提交预约
→ 管理后台查看订单、预约、AI 记录
```
