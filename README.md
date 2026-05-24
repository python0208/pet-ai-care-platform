# Pet AI Care Platform

宠物 AI 养护平台，面向养猫、养狗用户，提供宠物档案管理、AI 健康咨询、生活服务预约、宠物用品商城与支付闭环。

本仓库计划采用前后端分离结构：

```text
pet-ai-care-platform/
  backend/     # Django + Django REST Framework + MySQL
  frontend/    # uni-app + Vue3 + TypeScript + Pinia
  docs/        # 项目方案、架构、接口、数据库、执行计划
  AGENTS.md    # Codex / AI 编程工具必须读取的开发规范
```

---

## 1. 项目定位

本项目不是单纯的宠物商城，也不是单纯的 AI 聊天工具，而是一套：

```text
宠物档案数据沉淀
+ AI 健康咨询入口
+ 生活服务预约
+ 宠物商城交易闭环
```

核心目标是帮助用户完成以下事情：

1. 管理宠物健康档案；
2. 记录疫苗、驱虫、体重、就诊、过敏史；
3. 使用 AI 进行宠物健康咨询；
4. 查找附近宠物医院、美容、寄养、上门喂养等服务；
5. 购买宠物用品；
6. 使用微信支付 / 支付宝支付完成订单闭环。

---

## 2. 第一阶段 MVP 范围

第一阶段只做核心闭环：

```text
邮箱注册 / 邮箱密码登录
→ 创建宠物档案
→ 记录健康信息
→ 使用 AI 健康咨询
→ 浏览商城商品
→ 提交订单
→ 支付或 mock 支付
→ 查看附近服务
→ 提交服务预约
→ 管理后台查看订单、预约、AI 记录
```

---

## 3. 第一阶段必须实现

### 3.1 用户认证

- 邮箱注册
- 邮箱密码登录
- 微信小程序登录
- JWT 登录态
- 用户资料查看与修改
- 我的页面资料卡、统计卡和功能入口
- 用户协议 / 隐私政策页面
- 账号注销入口预留

微信小程序登录由前端通过 `uni.login` 获取 code，后端通过 `WECHAT_MINI_APPID` 和 `WECHAT_MINI_SECRET` 调用微信 code2session 换取 openid；`session_key` 不返回前端。`DEBUG=True` 且 `WECHAT_LOGIN_MOCK_ENABLED=true` 时支持开发模式 mock 微信登录。App 端微信登录仅做开放平台配置预留，H5 当前不做微信网页授权登录。当前 MVP 不使用邮箱验证码，手机号不作为登录方式；手机号只会在后续收货地址、服务预约联系人等业务联系方式中出现。

### 3.2 宠物档案

- 新增宠物
- 编辑宠物
- 删除宠物
- 宠物详情
- 宠物头像本地相册/相机选择、后端上传与前端默认头像 fallback
- 疫苗记录
- 驱虫记录
- 就诊记录
- 过敏史记录
- 体重记录
- 体重成长曲线
- 用户只能访问自己的宠物、健康记录和体重记录
- 一个用户可以拥有多个宠物档案，`GET /api/pets/` 返回当前用户全部宠物
- 档案页支持横向宠物头像切换，当前宠物通过 `selectedPetId` 维护

当前默认宠物头像资源路径：

```text
frontend/src/static/images/default-pet-avatar.svg
```

宠物头像通过 `/api/files/upload/` 上传，当前只支持 `jpg`、`jpeg`、`png`、`webp`，单文件最大 5MB。`Pet.avatar` 只保存上传接口返回的 URL，不能保存前端本地临时路径；本地上传文件落在 `media/`，该目录不进入 Git。档案管理页按 `docs/page/archive_page.png` 重构，运行时使用复制到 `frontend/src/static/icons/archive/` 的 `archive_page_assets_pack/` 资源。

档案管理页必须展示当前用户的全部宠物，新增第二只宠物不会覆盖旧宠物。页面默认选中上次访问的 `selectedPetId`，若该宠物已被删除则自动切换到列表第一只；切换宠物时同步刷新健康记录统计、近期记录和体重趋势。移动端 UI 需适配 375px、390px、414px 常见宽度，中文长文本使用省略号处理，避免卡片和按钮文字溢出。

### 3.3 AI 健康咨询

- 独立 AI 聊天页面
- 用户选择宠物后发起咨询
- 支持文字输入
- 支持图片上传
- 后端调用第三方大模型
- 后端自动拼接宠物档案上下文
- AI 返回风险等级、可能原因、护理建议、是否建议就医
- 保存历史会话
- 必须展示免责声明
- 后端已通过 OpenAI-compatible Provider 接入火山方舟 Doubao，默认模型为 `doubao-seed-2-0-mini-260428`
- AI 配置只从后端环境变量读取，前端不会接触 `AI_API_KEY`
- AI 咨询会读取当前用户自己的宠物档案、健康记录摘要和体重记录摘要作为上下文
- AI 角色已扩展为“AI 养宠助手”，支持日常养护问答、健康咨询和档案记录辅助
- 对话中识别到体重、疫苗、驱虫、就诊、过敏史等记录意图时，只生成待确认动作草稿，不直接写数据库
- 用户确认动作草稿后，后端再次校验权限并写入体重记录或健康记录
- 图片消息会保存到 AIMessage.image_urls，并在聊天窗口展示

### 3.4 生活服务

- 服务商列表
- 服务商详情
- 服务项目
- 附近服务推荐
- 服务预约
- 我的预约
- 后台管理服务商和预约

### 3.5 商城

- 商品分类
- 商品列表
- 商品详情
- 购物车
- 收货地址
- 提交订单
- 我的订单
- 后台管理商品和订单

### 3.6 支付

- 统一支付单
- 微信支付预留
- 支付宝支付预留
- 开发环境 mock 支付
- 支付回调
- 支付状态查询
- 支付日志
- 幂等处理

---

## 4. 第一阶段暂不实现

以下功能不要在 MVP 阶段开发：

- 智能硬件互联
- 人宠翻译器
- 宠物托运
- 兴趣社区
- 寻宠互助
- 二手闲置交易
- 真正在线兽医问诊
- 医生处方
- 药品销售
- 上门喂养视频直播
- 服务商独立后台
- 伴宠师独立端

这些功能可以作为第二阶段或第三阶段扩展。

---

## 5. 技术栈

### 后端

```text
Python 3.11+
Django 5.x
Django REST Framework
MySQL 8.x
Redis
Celery
django-filter
djangorestframework-simplejwt
Pillow
httpx / requests
django-environ / python-dotenv
```

### 前端

```text
uni-app
Vue3
TypeScript
Pinia
uni-ui / uView Plus / Wot Design Uni
ECharts / ucharts
```

---

## 6. 推荐开发顺序

必须按阶段开发，不要一次性生成所有功能：

```text
Phase 0：项目初始化
Phase 1：邮箱注册与登录认证
Phase 2：宠物档案管理
Phase 3：AI 健康咨询
Phase 4：商城模块
Phase 5：支付模块
Phase 6：生活服务模块
Phase 7：管理后台与上线准备
```

详细开发任务见：

```text
docs/CODEX_EXEC_PLAN.md
```

---

## 7. 本地启动方式

### 7.1 后端

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

### 7.2 前端

```bash
cd frontend
npm install
npm run dev:mp-weixin
```

App 端后续使用 HBuilderX 或对应 CLI 打包。

---

## 8. 环境变量

后端需要提供：

```text
DEBUG
SECRET_KEY
DB_NAME
DB_USER
DB_PASSWORD
DB_HOST
DB_PORT
REDIS_URL
JWT_ACCESS_TOKEN_LIFETIME_MINUTES
JWT_REFRESH_TOKEN_LIFETIME_DAYS
WECHAT_LOGIN_ENABLED
WECHAT_LOGIN_MOCK_ENABLED
WECHAT_MINI_APPID
WECHAT_MINI_SECRET
WECHAT_APP_APPID
WECHAT_APP_SECRET
AI_PROVIDER
AI_API_BASE
AI_API_KEY
AI_MODEL
AI_TIMEOUT_SECONDS
AI_TEMPERATURE
AI_MAX_TOKENS
PAYMENT_MOCK
WECHAT_PAY_MCH_ID
ALIPAY_APP_ID
MEDIA_URL
MEDIA_ROOT
```

建议参考：

```text
docs/ARCHITECTURE.md
```

---

## 9. AI 健康咨询边界

严禁把 AI 功能描述为：

```text
AI 诊断
AI 开药
AI 医生
在线处方
替代兽医
确诊疾病
```

统一使用：

```text
AI 健康咨询
AI 养宠助手
症状初步分析
护理建议
就医风险提示
```

每次 AI 咨询结果必须展示：

```text
本结果由 AI 根据你提供的信息生成，仅供养宠护理参考，不能替代专业兽医诊断。如宠物出现持续呕吐、呼吸困难、抽搐、大量出血、精神极差、误食毒物等情况，请立即联系线下宠物医院。
```

默认本地 AI 配置示例：

```text
AI_PROVIDER=ark_openai_compatible
AI_API_BASE=https://ark.cn-beijing.volces.com/api/v3
AI_API_KEY=your-ark-api-key
AI_MODEL=doubao-seed-2-0-mini-260428
AI_TIMEOUT_SECONDS=60
AI_TEMPERATURE=0.3
AI_MAX_TOKENS=1200
```

真实 `AI_API_KEY` 只能由开发者手动写入 `backend/.env`，不要写入 README、docs、测试文件、前端代码或任何 Git 跟踪文件。`DEBUG=True` 且未配置 key 时，后端会回退到 `MockAIProvider`，便于本地开发。

AI 动作草稿接口：

```text
GET  /api/ai/conversations/{conversation_id}/action-drafts/
POST /api/ai/action-drafts/{id}/confirm/
POST /api/ai/action-drafts/{id}/cancel/
```

动作草稿支持 `create_weight_record` 和 `create_health_record`。模型不能直接写数据库，只有用户确认后，后端才会以 `request.user` 校验宠物归属并执行写入。

---

## 10. Codex 必读文档

Codex 开发前必须读取：

```text
README.md
AGENTS.md
docs/PRODUCT_SPEC.md
docs/ARCHITECTURE.md
docs/DATABASE_DESIGN.md
docs/API_SPEC.md
docs/CODEX_EXEC_PLAN.md
```

如果 Codex 只能优先读取少量文件，则优先读取：

```text
AGENTS.md
docs/CODEX_EXEC_PLAN.md
docs/ARCHITECTURE.md
docs/API_SPEC.md
```
