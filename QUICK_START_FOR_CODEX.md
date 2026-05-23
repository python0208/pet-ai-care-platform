# QUICK_START_FOR_CODEX.md

# 给 Codex 的第一条消息

请复制下面这段内容给 Codex：

```text
请先完整读取以下文件：

1. README.md
2. AGENTS.md
3. docs/PRODUCT_SPEC.md
4. docs/ARCHITECTURE.md
5. docs/DATABASE_DESIGN.md
6. docs/API_SPEC.md
7. docs/CODEX_EXEC_PLAN.md

读取后不要急着开发，先总结你对项目的理解，包括：
1. 项目目标；
2. 技术栈；
3. MVP 范围；
4. 必须优先开发的 Phase；
5. 不能做的事情；
6. 你准备如何开始 Phase 0。

总结完成后，再等待我确认是否开始执行 Phase 0。
```

# 确认后执行 Phase 0

```text
开始执行 Phase 0：项目初始化。

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
