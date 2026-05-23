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
- 微信小程序登录预留
- JWT 登录态
- 用户资料查看与修改
- 用户协议 / 隐私政策页面
- 账号注销入口预留

当前 MVP 不使用邮箱验证码，手机号不作为登录方式；手机号只会在后续收货地址、服务预约联系人等业务联系方式中出现。

### 3.2 宠物档案

- 新增宠物
- 编辑宠物
- 删除宠物
- 宠物详情
- 宠物头像 URL 记录与前端默认头像 fallback
- 疫苗记录
- 驱虫记录
- 就诊记录
- 过敏史记录
- 体重记录
- 体重成长曲线
- 用户只能访问自己的宠物、健康记录和体重记录

当前默认宠物头像资源路径：

```text
frontend/src/static/images/default-pet-avatar.svg
```

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
WECHAT_MINI_APPID
WECHAT_MINI_SECRET
AI_PROVIDER
AI_API_BASE
AI_API_KEY
AI_MODEL
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
