# HANDOFF_TO_NEXT_CODEX.md

## 1. 当前项目目标

本项目是一个宠物 AI 养护平台，目标面向微信小程序、Android App、iOS App 等移动端场景。

当前技术栈：

- 后端：Django + Django REST Framework + MySQL + JWT
- 前端：uni-app + Vue3 + TypeScript + Pinia
- 当前已落地核心功能：邮箱注册、邮箱密码登录、JWT 登录态、用户资料、宠物档案、健康记录、体重记录、宠物头像上传、档案页、多宠物切换
- 后续核心功能：AI 健康咨询、生活服务预约、宠物商城、支付闭环、管理后台

## 2. 当前已完成 Phase

### Phase 0：项目初始化与首页原型

状态：已完成并提交。

已完成内容：

- 创建 `backend/`，初始化 Django 项目与 `config/` 配置目录。
- 接入 Django REST Framework、CORS、SimpleJWT 基础配置。
- MySQL 配置从环境变量读取。
- 创建 `apps/common/`，包含 `TimeStampedModel`、统一响应、统一异常处理、分页、健康检查。
- 实现 `GET /api/health/`，返回统一响应格式。
- 创建 `frontend/`，初始化 uni-app + Vue3 + TypeScript + Pinia。
- 配置 `src/api/request.ts`。
- 创建首页、档案、AI 咨询、服务、我的等基础页面和底部 TabBar。
- 首页按 `docs/page/home_page.png` 初始化静态原型。
- 首页资源来自 `home_page_icon_pack/`，已复制到 `frontend/src/static/icons/` 下。

### Phase 1：邮箱注册与登录认证

状态：已完成并提交。

已完成内容：

- 创建 `apps/users/`。
- 实现自定义 `User` 模型。
- 实现邮箱注册 `POST /api/auth/register/`。
- 实现邮箱密码登录 `POST /api/auth/login/`。
- 接入 JWT access / refresh token。
- 实现 token refresh：`POST /api/auth/token/refresh/`。
- 实现用户资料接口：`GET /api/users/me/`、`PUT /api/users/me/`。
- 实现退出登录：`POST /api/auth/logout/`。
- 实现微信小程序登录预留：`POST /api/auth/wx-login/`，当前为 mock/provider 预留。
- 前端实现登录/注册页面、token 存储、请求携带 `Authorization: Bearer <access_token>`。
- 前端我的页面展示头像、昵称、邮箱。
- 创建默认用户头像：`frontend/src/static/images/default-user-avatar.svg`。
- 文档已清理手机号登录、短信验证码、邮箱验证码相关规则。

重要决策：

- 不使用手机号登录。
- 不使用短信验证码。
- 当前 MVP 不使用邮箱验证码。
- 注册和登录是两个明确动作，不做登录时自动注册。

### Phase 2：宠物档案管理

状态：已完成并提交。

已完成内容：

- 创建 `apps/pets/`。
- 实现 `Pet` 模型。
- 实现 `HealthRecord` 模型。
- 实现 `WeightRecord` 模型。
- 实现宠物 CRUD。
- 实现健康记录列表、创建、详情、更新、删除。
- 实现体重记录列表、创建、删除。
- 所有宠物、健康记录、体重记录都绑定当前登录用户。
- 用户只能访问自己的宠物数据。
- 首页宠物卡片逐步接入真实宠物数据。
- 档案 Tab 接入宠物列表、宠物详情、新增/编辑、健康记录、体重记录页面。
- 创建默认宠物头像：`frontend/src/static/images/default-pet-avatar.svg`。

### Phase 2.1：宠物头像上传与档案页美化

状态：已完成并提交。

已完成内容：

- 创建 `apps/files/`。
- 实现 `UploadedFile` 模型。
- 实现文件上传接口：`POST /api/files/upload/`。
- 上传接口要求登录，使用 `multipart/form-data`，文件字段为 `file`。
- 当前只允许图片类型：`jpg`、`jpeg`、`png`、`webp`。
- 单文件大小限制为 5MB。
- 配置 `MEDIA_URL`、`MEDIA_ROOT`。
- `DEBUG=True` 时通过 Django 开发服务器访问 media 文件。
- `.gitignore` 已忽略 `media/` 和 `staticfiles/`。
- 前端通过 `uni.chooseImage` 选择相册或相机图片。
- 前端通过 `uni.uploadFile` 上传宠物头像。
- 上传成功后将后端返回 URL 写入 `Pet.avatar`。
- 档案页参考 `docs/page/archive_page.png` 进行视觉重构。
- 档案页资源来自 `archive_page_assets_pack/`，运行时资源复制到 `frontend/src/static/icons/archive/`。

### Phase 2.2：多宠物档案支持与 UI 适配

状态：已完成并提交。

最近相关提交：

```text
1349de9 fix(pets): improve archive UI and multi-pet switching
```

已完成内容：

- 后端确认 `Pet.owner` 是 `ForeignKey`，即 `User 1 - N Pet`。
- `GET /api/pets/` 返回当前登录用户的全部宠物。
- 补充测试覆盖同一用户创建多只宠物、列表返回全部宠物、编辑/删除单只宠物不影响其他宠物。
- 前端档案页维护：
  - `pets`
  - `selectedPetId`
  - `selectedPet`
  - `healthRecords`
  - `weightRecords`
  - loading / error / empty 状态
- 档案页新增横向宠物头像切换区。
- 当前选中宠物高亮，最后一个入口为“新增”。
- 切换宠物后，主卡片、档案模块、近期记录、体重趋势都会刷新。
- 新增/编辑宠物成功后保存 `selected_pet_id` 并返回档案 Tab。
- 删除当前宠物后清理已保存的 `selected_pet_id`，回到档案页后自动选中剩余宠物或展示空状态。
- UI 字体层级、卡片圆角、卡片间距、长文本省略号、模块宫格尺寸均做过优化。
- 目标适配 375px、390px、414px 常见手机宽度；已通过代码层面的响应约束和构建检查，但未在真实多机型小程序设备上逐一实测。

### Phase 3：AI 健康咨询

状态：已完成并提交。

当前真实状态：

- 已创建 `apps/ai_chat/`。
- 已实现 `AIConversation`、`AIMessage`、`AIConsultationResult`、`PromptTemplate`。
- 已实现 `AIProviderBase`、`OpenAICompatibleProvider`、`MockAIProvider` 和 `ProviderFactory`。
- 已接入火山方舟 Doubao，默认模型 `doubao-seed-2-0-mini-260428`。
- 已实现 `/api/ai/consult/`、会话列表、会话消息接口。
- 已实现宠物档案上下文注入、结构化 JSON 解析和 fallback。
- 前端已实现 AI 会话入口、聊天页、风险等级卡片、免责声明。

### Phase 3.1：AI 聊天体验优化 + 养宠助手能力扩展 + 档案记录动作草稿

状态：已完成并提交。

已完成内容：

- AI 角色从健康咨询助手升级为 AI 养宠助手。
- 支持日常养护问答、健康咨询和档案记录意图识别。
- 新增 `AIActionDraft` 模型和迁移。
- 新增动作草稿列表、确认、取消接口。
- 确认动作草稿后可写入 `WeightRecord` 或 `HealthRecord`。
- 后端测试覆盖动作草稿权限、重复执行、取消、非法 payload、图片 URL 保存等场景。
- 前端聊天页优化布局、图片消息展示、历史图片展示和动作确认卡片。

### Phase 3.2：AI 聊天页面体验修复与动作草稿状态修正

状态：已完成，未提交。

本轮目标：

- AI 聊天页顶部改为紧凑结构，避免标题、免责声明、宠物切换和快捷问题占据过多首屏高度。
- 快捷问题改为分组 tab + 横向滚动 chip，避免按钮截断、半截露出或横向溢出。
- 消息区为页面主体，固定底部输入栏并为 safe area 和输入区高度预留滚动空间，避免动作草稿卡片被遮挡。
- 图片消息需要在发送前、发送后和历史消息中展示，`/media/` 相对地址通过前端 API base origin 拼接。
- action draft 状态以前端收到的后端 `status` 为准：`pending` 显示待确认和操作按钮，`executed` 显示已保存，`cancelled` 显示已取消，`failed` 显示保存失败。
- 当前阶段仍使用非流式 HTTP 请求返回完整 AI 结果，不做 SSE/WebSocket 流式输出。

### Phase 3.3：AI 咨询首页单页结构压缩与移动端体验优化

状态：本轮进行中，未提交。

本轮目标：

- AI 咨询首页仍保持为 `pages/ai/index` 单页滚动结构，不拆分路由。
- 按 `docs/page/ai_page.png` 原型重构 AI 首页视觉。
- 优先使用 `ai_consult_page_icon_pack/` 图标资源，运行时图标复制到 `frontend/src/static/icons/ai/`。
- 顶部 Hero、免责声明和宠物选择区压缩为轻量结构，减少首屏高度占用。
- 宠物选择区改为横向轻量头像列表，并保留添加入口。
- 新咨询入口改为输入式入口，点击后带当前 `selectedPetId` 进入聊天详情页。
- 快捷问题改为“健康咨询 / 日常养护 / 档案记录”分类 tab + 当前分类横向 chips，避免三类问题全部展开。
- 历史咨询区提前展示，列表显示会话标题、宠物名称、日期、类型标签和待确认记录提示。
- 页面底部为 TabBar 和 safe area 预留空间，避免最后一条历史咨询被遮挡。
- 会话列表轻量补充 `pending_action_count`，不破坏旧字段和 `/api/ai/consult/`。
- 当前阶段仍不做 SSE/WebSocket 流式输出。

### Phase 3.4：我的页面 UI 完善 + 微信登录预留/小程序登录实现

状态：已完成，未提交。

本轮目标：

- “我的”页面升级为完整个人中心：未登录引导、已登录资料卡、微信绑定状态、登录方式标签、三项统计、分组功能入口和二次确认退出。
- 登录页保留邮箱登录/注册，并增加微信登录区域；微信小程序端使用 `uni.login`，开发模式可使用 mock 微信登录。
- 后端微信登录从预留升级为 provider 架构：小程序真实 code2session、开发 mock、App 端明确预留。
- 新增 `/api/users/me/summary/`，统计当前用户宠物数、AI 会话数和待确认动作草稿数。
- `/api/users/me/` 返回 `has_wechat_bound`、`auth_providers`，微信登录用户不向前端展示内部占位邮箱。
- 当前仍不做手机号登录、短信验证码、邮箱验证码、商城下单、支付或生活服务预约。

### Phase 4.0：商品后台管理与 Excel 批量导入

状态：本轮进行中，未提交。

本轮目标：

- 创建 `apps/shop/`，先完成商品数据管理基础能力。
- 新增 `ProductCategory`、`Product`、`ProductInventory`、`ProductImportBatch`、`ProductImportRow`。
- Django Admin 可管理商品分类、商品、库存、导入批次和导入明细。
- Admin 增加“商品 Excel 批量导入”入口，仅 staff / superuser 可访问。
- Excel 字段固定为：图片、名称、单位、进货价、规格、零售价、条码、重量、直营店序号、分类、保质期（月）、当前库存。
- 条码 `barcode` 作为商品唯一识别字段；条码不存在新增商品，条码已存在更新商品。
- Product 和 ProductInventory 分表；同一 `product + store_code` 只有一条库存。
- 直营店序号允许为空，空值导入默认库存，内部 `store_code=DEFAULT`，后台显示“默认库存”。
- Excel 嵌入图片提取后保存到 `media/products/`，原始 Excel 保存到 `media/imports/products/`，数据库只保存路径。
- 行级失败写入 `ProductImportRow`，不影响其他行继续导入。
- 本轮不开发商城前端、购物车、订单、支付、优惠券、物流。

### Phase 4.1：商城商品展示接口与前端商城页面

状态：本轮进行中，未提交。

本轮目标：

- 基于已导入商品数据实现用户端只读接口：`GET /api/shop/categories/`、`GET /api/shop/products/`、`GET /api/shop/products/{id}/`。
- 商品接口只返回启用分类和 `status=active` 商品，不返回进货价、导入批次或导入明细。
- 商品接口返回 `cover_image_url`、`total_stock`、`stock_status`，前端可直接展示商品图片。
- 前端新增 `src/api/shop.ts`、`pages/shop/index.vue`、`pages/shop/detail.vue` 和 `types/shop.ts`。
- TabBar 第四项从“服务”改为“商城”，服务页面保留但不作为主入口。
- 商城首页参考 `docs/page/shop.png`，资源 `shop_page/header.png`、`shop_page/center.png` 已复制到 `frontend/src/static/images/shop/`。
- 新增默认商品图 `frontend/src/static/images/default-product.svg`。
- 首页“精选商城”模块接入真实商品数据，失败或无数据时不影响首页其他模块。
- 当前仍不做购物车、订单、支付、优惠券、物流、评价、售后或库存扣减。

### Phase 4.1.1：商城页面 UI 体验修复与商品图片显示修复

状态：本轮进行中，未提交。

本轮目标：

- 修复商品真实图片展示：后端 `cover_image_url` 兼容完整 URL、`/media/products/xxx`、`products/xxx` 和误存本地路径时的 `/media/` 截取，前端列表/详情优先使用 `cover_image_url`，失败回退 `default-product.svg`。
- 优化商城商品卡片：两列网格更紧凑，图片区浅蓝白背景，商品名两行省略，价格红橙突出，有货/缺货标签底部对齐。
- 修复底部 TabBar 遮挡：商城滚动内容增加 `tabbar + safe-area + 额外空间` 的底部留白，最后一行商品完整可见。
- 优化 Header、精选好物 Banner、分类 Tab、搜索框和扫码占位入口，保持接近 `docs/page/shop.png` 的浅蓝白风格。
- 补充加载、接口失败、搜索无结果、分类失败和图片失败 fallback 状态。
- 当前仍不开发购物车、订单、支付、优惠券、物流、评价、售后或库存扣减。

### Phase 4.1.2：商城列表分页加载更多与商品图片路径修复

状态：本轮进行中，未提交。

本轮目标：

- 商品列表接口分页响应增加 `total_pages`、`has_next`、`has_previous`，前端根据 `has_next` 滚动加载更多。
- 商城首页首次加载第一页；下拉刷新、分类切换、搜索和清空搜索都会清空旧列表并从第一页重新加载。
- 加载更多时追加商品，底部展示“加载中...”“加载失败，点击重试”“没有更多商品了”。
- 商品图片路径兼容 `.jpg/.jpeg/.png/.webp`，后端会在 `cover_image` 为空或文件不存在时按 `media/products/<barcode>.*` 查找兜底。
- 列表、详情和首页精选商城统一使用前端 `resolveProductImage()`；该方法会将后端返回的 localhost/127.0.0.1 media 地址改写到当前 API_ORIGIN，图片失败时回退 `default-product.svg`。
- 当前仍不开发购物车、订单、支付、优惠券、物流、评价、售后或库存扣减。

下一窗口如果执行 Phase 3，应使用以下规划信息：

- Provider 需要可替换模型。
- 火山方舟 OpenAI-compatible base url 计划为 `https://ark.cn-beijing.volces.com/api/v3`。
- 计划模型名称：`doubao-seed-2-0-mini-260428`。
- `AI_API_KEY` 必须从 `backend/.env` 读取，不能写入代码、文档或前端。
- 需要 MockAIProvider fallback。
- AI 健康咨询必须注入宠物上下文，并保留免责声明。

## 3. 当前仓库结构

当前真实顶层结构：

```text
AGENTS.md
README.md
QUICK_START_FOR_CODEX.md
backend/
docs/
frontend/
home_page_icon_pack/
archive_page_assets_pack/
```

后端关键结构：

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
    files/
  tests/
    test_auth.py
    test_files.py
    test_health.py
    test_pets.py
```

前端关键结构：

```text
frontend/
  package.json
  src/
    App.vue
    main.ts
    manifest.json
    pages.json
    api/
      auth.ts
      files.ts
      pets.ts
      request.ts
    pages/
      index/index.vue
      auth/index.vue
      pets/index.vue
      pets/edit.vue
      pets/detail.vue
      pets/health-records.vue
      pets/health-record-edit.vue
      pets/weight.vue
      ai/index.vue
      services/index.vue
      user/index.vue
    stores/
      app.ts
      auth.ts
    types/
      pet.ts
      user.ts
    utils/
      auth.ts
      upload.ts
    static/
      icons/
      images/
```

文档与资源：

```text
docs/
  API_SPEC.md
  ARCHITECTURE.md
  CODEX_EXEC_PLAN.md
  DATABASE_DESIGN.md
  PRODUCT_SPEC.md
  page/
    home_page.png
    archive_page.png

home_page_icon_pack/
  png/
  svg/
  manifest.json
  README.md

archive_page_assets_pack/
  png/
  svg/
  manifest.json
  README.md
```

注意：

- `backend/.env` 存在于本地，但被 Git 忽略，不能提交。
- `backend/.venv/` 存在于本地，但被 Git 忽略，不能提交。
- `backend/media/` 存在本地上传文件，但被 Git 忽略，不能提交。
- `frontend/node_modules/` 与 `frontend/dist/` 存在本地生成内容，但被 Git 忽略，不能提交。

## 4. 后端当前状态

### 4.1 依赖

`backend/requirements.txt` 当前关键依赖：

```text
Django>=5.0,<6.0
djangorestframework>=3.15,<4.0
djangorestframework-simplejwt>=5.3,<6.0
django-cors-headers>=4.3,<5.0
django-environ>=0.11,<1.0
PyMySQL>=1.1,<2.0
celery>=5.3,<6.0
redis>=5.0,<6.0
```

### 4.2 settings 重要配置

当前 `backend/config/settings.py` 已配置：

- `AUTH_USER_MODEL = "users.User"`
- MySQL 数据库从 `.env` 读取。
- DRF JWT 认证。
- 统一异常处理：`apps.common.exceptions.custom_exception_handler`
- 统一分页：`apps.common.pagination.StandardResultsSetPagination`
- CORS allowed origins 从环境变量读取。
- `MEDIA_URL`、`MEDIA_ROOT`
- `DEBUG=True` 时 `config.urls` 暴露 media 文件访问。

当前 `INSTALLED_APPS`：

```text
apps.common
apps.users
apps.pets
apps.files
```

尚未实现：

```text
apps.ai_chat
apps.services
apps.shop
apps.payments
apps.notifications
```

### 4.3 数据库配置方式

后端数据库配置必须通过 `backend/.env`：

```text
DB_HOST=
DB_PORT=
DB_NAME=
DB_USER=
DB_PASSWORD=
```

不要把真实数据库密码写入 README、AGENTS、docs、代码或提交记录。

### 4.4 当前 API 路由

根路由 `backend/config/urls.py`：

```text
/api/ -> apps.common.urls
/api/ -> apps.users.urls
/api/ -> apps.pets.urls
/api/ -> apps.files.urls
```

当前后端 app 路由文件：

```text
apps/common/urls.py
apps/users/urls.py
apps/pets/urls.py
apps/files/urls.py
```

### 4.5 当前模型列表

已实现模型：

- `users.User`
- `pets.Pet`
- `pets.HealthRecord`
- `pets.WeightRecord`
- `files.UploadedFile`

通用基础模型：

- `common.TimeStampedModel`

### 4.6 当前 migration 状态

已存在 migration：

```text
backend/apps/users/migrations/0001_initial.py
backend/apps/pets/migrations/0001_initial.py
backend/apps/pets/migrations/0002_alter_pet_avatar.py
backend/apps/files/migrations/0001_initial.py
```

`apps/common` 没有业务表 migration。

### 4.7 当前测试情况

当前测试文件：

```text
backend/tests/test_health.py
backend/tests/test_auth.py
backend/tests/test_pets.py
backend/tests/test_files.py
```

本交接前执行结果：

```text
cd backend
.venv\Scripts\python.exe manage.py test tests
```

结果：

```text
Found 35 test(s).
Ran 35 tests.
OK
```

注意：测试中出现 `InsecureKeyLengthWarning`，原因是本地开发 `SECRET_KEY` 较短；不影响测试通过，但后续应在真实环境中使用足够长度的密钥。

### 4.8 后端启动命令

Windows / PowerShell：

```text
cd backend
.venv\Scripts\activate
python manage.py migrate
python manage.py runserver
```

如果未创建虚拟环境：

```text
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## 5. 前端当前状态

### 5.1 技术栈

当前前端为 uni-app + Vue3 + TypeScript + Pinia。

`frontend/package.json` 关键脚本：

```text
npm run dev:h5
npm run dev:mp-weixin
npm run build:h5
npm run build:mp-weixin
npm run type-check
```

本交接前执行结果：

```text
cd frontend
npm run type-check
npm run build:h5
```

结果：

- `vue-tsc --noEmit` 通过。
- `uni build -p h5` 通过。

### 5.2 页面目录

当前页面：

```text
pages/index/index.vue              首页
pages/auth/index.vue               登录/注册
pages/pets/index.vue               档案页
pages/pets/edit.vue                新增/编辑宠物
pages/pets/detail.vue              宠物详情
pages/pets/health-records.vue      健康记录列表
pages/pets/health-record-edit.vue  新增/编辑健康记录
pages/pets/weight.vue              体重记录
pages/ai/index.vue                 AI 咨询占位页
pages/services/index.vue           服务占位页
pages/user/index.vue               我的页面
```

### 5.3 API 封装目录

当前 API 封装：

```text
src/api/request.ts
src/api/auth.ts
src/api/pets.ts
src/api/files.ts
```

`request.ts`：

- 默认 API 地址为 `http://127.0.0.1:8000/api`。
- 支持通过 `VITE_API_BASE_URL` 覆盖。
- 自动从本地存储读取 `access_token` 并添加 `Authorization`。
- 401 时会清理 token。
- `resolveMediaUrl()` 用于将 `/media/...` 拼成完整访问地址。

### 5.4 store 状态管理

当前 Pinia store：

```text
src/stores/app.ts
src/stores/auth.ts
```

认证 token 主要仍通过 uni storage 使用。

### 5.5 静态资源目录

首页资源：

```text
frontend/src/static/icons/png/
frontend/src/static/icons/svg/
frontend/src/static/icons/manifest.json
```

档案页资源：

```text
frontend/src/static/icons/archive/
```

默认头像：

```text
frontend/src/static/images/default-user-avatar.svg
frontend/src/static/images/default-pet-avatar.svg
```

### 5.6 首页实现状态

首页已完成 Phase 0 视觉原型，并在 Phase 2 接入真实宠物数据：

- 登录用户有宠物时展示第一只或当前数据。
- 无宠物时显示添加引导。
- 展示健康提醒、快捷入口、精选商城静态卡片。
- 调用 `/api/health/` 检查后端连接状态。

### 5.7 登录/注册实现状态

登录/注册页面已实现：

- 邮箱输入。
- 密码输入。
- 注册昵称可选。
- 注册确认密码。
- 协议勾选提示。
- 不包含手机号、验证码、获取验证码、短信登录、邮箱验证码文案。
- 注册或登录成功后保存 token 并进入已登录状态。

### 5.8 我的页面实现状态

我的页面已实现：

- 展示默认头像 fallback。
- 展示昵称、邮箱。
- 不展示手机号。
- 提供“我的宠物”入口。
- 支持退出登录。

### 5.9 档案页实现状态

档案页已实现：

- 多宠物横向头像切换。
- 当前宠物主卡片。
- 6 个档案模块卡片。
- 近期记录。
- 体重趋势简易展示或空状态。
- 新增宠物入口。
- 无宠物空状态。
- 使用 `archive_page_assets_pack/` 复制后的运行时资源。
- 视觉风格为浅蓝白背景、大圆角、柔和阴影、蓝色主色。

### 5.10 AI 页面实现状态

AI 页面尚未实现真实业务：

- `frontend/src/pages/ai/index.vue` 目前是占位页。
- 仅显示 AI 咨询入口文案和图标。
- 仅做 `requireAuth()` 登录态检查。

### 5.11 前端启动命令

```text
cd frontend
npm install
npm run dev:h5
```

微信小程序：

```text
cd frontend
npm install
npm run dev:mp-weixin
```

构建检查：

```text
cd frontend
npm run type-check
npm run build:h5
```

## 6. 环境变量说明

环境变量写入 `backend/.env`。`.env` 不应提交 Git。

当前 `.env.example` 已包含 DB、JWT、微信 mock、media 等基础变量；下一阶段做 AI 时需要补充 AI 相关变量示例。

示例占位，不要写真实密码或真实 Key：

```text
DEBUG=True
SECRET_KEY=replace-with-local-secret
ALLOWED_HOSTS=127.0.0.1,localhost
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

DB_HOST=example-db-host
DB_PORT=3306
DB_NAME=example_db_name
DB_USER=example_user
DB_PASSWORD=example_password

REDIS_URL=redis://127.0.0.1:6379/0

JWT_ACCESS_TOKEN_LIFETIME_MINUTES=60
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7

WECHAT_LOGIN_MOCK=True
WECHAT_MINI_APPID=example_appid
WECHAT_MINI_SECRET=example_secret

MEDIA_URL=/media/
MEDIA_ROOT=media

AI_PROVIDER=mock
AI_API_BASE=https://example-ai-base-url
AI_API_KEY=example_ai_api_key
AI_MODEL=example_model_name
AI_TIMEOUT_SECONDS=30
AI_TEMPERATURE=0.3
AI_MAX_TOKENS=1200
```

重要：

- 不要提交 `backend/.env`。
- 不要把真实数据库密码写入任何文档。
- 不要把真实 AI API Key 写入任何文档。
- 前端不能读取或保存 AI API Key。

## 7. 已完成的重要接口

### common

- `GET /api/health/`：已完成。

### auth / users

- `POST /api/auth/register/`：已完成，邮箱注册，成功返回 token 和 user。
- `POST /api/auth/login/`：已完成，邮箱密码登录。
- `POST /api/auth/token/refresh/`：已完成。
- `POST /api/auth/wx-login/`：已完成预留，当前可 mock。
- `POST /api/auth/logout/`：已完成。
- `GET /api/users/me/`：已完成，需要 JWT。
- `PUT /api/users/me/`：已完成，需要 JWT。

### pets

- `GET /api/pets/`：已完成，返回当前用户全部宠物。
- `POST /api/pets/`：已完成，创建宠物，owner 自动取 `request.user`。
- `GET /api/pets/{id}/`：已完成，只能访问自己的宠物。
- `PUT /api/pets/{id}/`：已完成，只能更新自己的宠物。
- `PATCH /api/pets/{id}/`：已完成，只能更新自己的宠物。
- `DELETE /api/pets/{id}/`：已完成，只能删除自己的宠物。
- `GET /api/pets/{pet_id}/health-records/`：已完成。
- `POST /api/pets/{pet_id}/health-records/`：已完成。
- `GET /api/health-records/{id}/`：已完成。
- `PUT /api/health-records/{id}/`：已完成。
- `PATCH /api/health-records/{id}/`：已完成。
- `DELETE /api/health-records/{id}/`：已完成。
- `GET /api/pets/{pet_id}/weight-records/`：已完成。
- `POST /api/pets/{pet_id}/weight-records/`：已完成。
- `DELETE /api/weight-records/{id}/`：已完成。

### files

- `POST /api/files/upload/`：已完成，需要 JWT，当前用于宠物头像上传。

### AI

AI 相关接口尚未实现。

## 8. 当前重要设计决策

1. 不使用手机号登录。
2. 不使用短信验证码。
3. 当前 MVP 不使用邮箱验证码。
4. 认证方式是邮箱注册 + 邮箱密码登录。
5. 手机号只可能在后期收货地址、服务预约联系人中作为业务字段出现。
6. 一个用户可以有多个宠物。
7. `Pet` 与 `User` 是 1:N。
8. 宠物头像通过 `/api/files/upload/` 上传。
9. 上传图片保存在 `media/`，`media/` 不进 Git。
10. `Pet.avatar` 保存后端返回的 URL，不保存前端本地临时路径。
11. AI Key 只能写在 `backend/.env`。
12. 前端不能接触 AI Key。
13. AI 健康咨询不能作为医疗诊断。
14. AI 回复必须保留免责声明。
15. Provider 架构必须可替换模型。
16. 所有用户数据后端必须以 `request.user` 为准隔离。

## 9. 已知问题和待修复事项

当前已知事项：

- Phase 3 尚未开始，AI 咨询页仍是占位页。
- 尚未创建 `apps/ai_chat/`，AI 数据模型、provider、接口、前端聊天页都未实现。
- `backend/.env.example` 当前尚未包含 AI 相关变量，Phase 3 开始时应补充示例占位。
- 服务页仍是占位页。
- 商城、支付、生活服务、管理后台尚未开发。
- 首页“精选商城”等内容仍为静态展示，未接真实商城数据。
- 小程序端头像上传尚未在真实微信开发者工具或真机上完整验证。
- 多宠物切换已通过代码和构建检查，后端测试覆盖多宠物数据隔离；但 375px、390px、414px 的真实视觉适配尚未用浏览器/设备截图逐一归档。
- 本交接前从仓库根目录执行 `backend\.venv\Scripts\python.exe backend\manage.py test tests` 会触发 unittest 路径发现问题；正确方式是在 `backend/` 目录下执行 `.venv\Scripts\python.exe manage.py test tests`。
- 当前测试通过，但本地开发 `SECRET_KEY` 较短，测试时会有 JWT key length warning；生产或共享环境应配置更强密钥。

当前 Git 状态：

```text
On branch master
Your branch is up to date with 'origin/master'.
nothing to commit, working tree clean
```

最近提交：

```text
1349de9 fix(pets): improve archive UI and multi-pet switching
6fbec17 feat(pets): add pet avatar upload and archive UI
53193fe feat(pets): add pet profile management
bff65a4 feat(auth): add email authentication
1c35671 chore: initialize project structure and homepage prototype
0ed60ef docs: add Codex project planning documents
```

本交接文档创建前 `git diff --stat` 为空；创建本文档后会出现 `docs/HANDOFF_TO_NEXT_CODEX.md` 为未提交新增文件。

## 10. 下一窗口推荐开发顺序

根据当前真实状态，下一窗口应从 Phase 3 开始，而不是进入商城模块。

推荐顺序：

1. 阅读 `AGENTS.md`、`README.md`、`docs/HANDOFF_TO_NEXT_CODEX.md`、`docs/CODEX_EXEC_PLAN.md`、`docs/API_SPEC.md`、`docs/DATABASE_DESIGN.md`。
2. 执行 `git status` 和 `git log --oneline -10`，确认当前状态。
3. 补充 Phase 3 需要的文档与 `.env.example` AI 变量示例。
4. 创建 `apps/ai_chat/`。
5. 实现 AIConversation、AIMessage、AIConsultationResult、PromptTemplate。
6. 实现 Provider 抽象层，包含 MockAIProvider 和 OpenAI-compatible provider。
7. 接入火山方舟 Doubao，配置从 `.env` 读取：
   - `AI_API_BASE`
   - `AI_API_KEY`
   - `AI_MODEL`
   - `AI_TIMEOUT_SECONDS`
   - `AI_TEMPERATURE`
   - `AI_MAX_TOKENS`
8. 实现 AI 咨询接口，必须校验用户只能咨询自己的宠物。
9. 注入宠物基础资料、健康记录摘要、体重记录摘要作为上下文。
10. 固定智能体提示词应放在后端可维护位置，例如 provider/prompt service 或 PromptTemplate 初始化逻辑。
11. AI 输出必须包含免责声明，不能输出明确医疗诊断、处方或药品剂量指导。
12. 前端实现 AI 聊天页面、宠物选择、消息列表、风险等级卡片、免责声明。
13. 补充后端测试和前端构建检查。

Phase 3 完成并通过测试后，才建议进入 Phase 4：商城模块。

## 11. 下一窗口给 Codex 的启动提示词

```text
请先阅读：
1. AGENTS.md
2. README.md
3. docs/HANDOFF_TO_NEXT_CODEX.md
4. docs/CODEX_EXEC_PLAN.md
5. docs/API_SPEC.md
6. docs/DATABASE_DESIGN.md

然后根据 HANDOFF_TO_NEXT_CODEX.md 判断当前项目完成到哪个阶段。

不要重复开发已完成内容。
不要破坏已有邮箱登录、宠物档案、多宠物切换、头像上传功能。
不要提交 .env、.venv、node_modules、dist、unpackage、media、staticfiles。

请先执行：
git status
git log --oneline -10

然后总结你对当前项目状态的理解，再等待我指定下一步任务。
```
