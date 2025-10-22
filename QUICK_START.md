# 🚀 快速启动指南 - Claude Code 远程Web控制器

## 📋 项目概述

这是一个Web应用，允许通过浏览器远程控制Claude Code。包含：
- **前端**：Vue 3 + TypeScript + TailwindCSS
- **后端**：FastAPI + Python 3.11+ + PostgreSQL
- **通信**：WebSocket (实时)

**完整状态**: 72.67% 完成 (109/150 任务)

---

## ⚡ 1分钟快速启动

### 前置条件检查
```bash
# 检查Python版本
python3.11 --version
python3.12 --version  # 推荐

# 检查Docker
docker --version
docker-compose --version

# 检查Node
node --version  # >= 18
npm --version
```

### 启动完整环境（Docker方式）⭐ 推荐

```bash
cd /home/image/projllm/llmservice/vermilion/RVC_projs/remote_vibe_coding

# 1️⃣ 启动数据库
docker-compose up -d postgresql

# 等待数据库就绪（5秒）
sleep 5

# 2️⃣ 后端设置
cd backend
python3.12 -m pip install -q -e .
export PYTHONPATH=.
alembic upgrade head

# 3️⃣ 启动后端（另一个终端）
python3.12 -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# 4️⃣ 前端设置（另一个终端）
cd frontend
npm install
npm run dev

# ✅ 访问应用
# 前端: http://localhost:5173
# API文档: http://localhost:8000/docs
```

---

## 🛠️ 本地开发工作流

### 快速命令集合

```bash
# 从项目根目录执行

# 启动数据库
docker-compose up -d postgresql

# 后端开发
cd backend
PYTHONPATH=. python3.12 -m uvicorn src.main:app --reload

# 前端开发（新终端）
cd frontend
npm run dev

# 运行后端测试
cd backend
pytest -xvs tests/

# 运行前端测试
cd frontend
npm run test

# 查看后端代码质量
cd backend
ruff check src/ tests/
mypy src/

# 格式化代码
cd backend
black src/ tests/
ruff check --fix src/ tests/
```

### 目录结构速览
```
.
├── backend/
│   ├── src/
│   │   ├── main.py          # FastAPI应用入口
│   │   ├── models/          # SQLAlchemy数据模型
│   │   ├── services/        # 业务逻辑
│   │   ├── api/             # API路由
│   │   └── schemas/         # Pydantic验证模式
│   ├── tests/
│   │   ├── integration/     # 集成测试
│   │   └── contract/        # API协议测试
│   └── pyproject.toml       # 依赖管理
│
├── frontend/
│   ├── src/
│   │   ├── components/      # Vue组件
│   │   ├── views/           # 页面
│   │   ├── stores/          # Pinia状态
│   │   ├── services/        # API客户端
│   │   └── composables/     # 逻辑复用
│   ├── tests/               # Vitest单元测试
│   └── package.json
│
├── specs/001-web-app-remote/
│   ├── spec.md              # 功能规格书
│   ├── plan.md              # 实现计划
│   ├── tasks.md             # 任务列表
│   └── data-model.md        # 数据模型
│
└── docker-compose.yml       # PostgreSQL配置
```

---

## 🧪 快速测试

### 后端测试

```bash
cd backend

# 运行所有测试
pytest -xvs

# 运行特定用户故事的测试
pytest -xvs tests/integration/test_authentication.py
pytest -xvs tests/integration/test_authorization.py

# 运行指定标记的测试
pytest -xvs -k "T118"  # 认证测试

# 查看测试覆盖率
pytest --cov=src --cov-report=html tests/

# 快速检查（无输出）
pytest -q
```

### 前端测试

```bash
cd frontend

# 运行所有单元测试
npm run test

# 监视模式（自动重新运行）
npm run test:watch

# 生成覆盖率报告
npm run test:coverage
```

### 手动测试流程

#### 1. 认证测试（2分钟）
```bash
# 1. 打开 http://localhost:5173
# 2. 注册新账户
#    Username: testuser
#    Email: test@example.com
#    Password: TestPassword123
# 3. 登录成功 → 进入主界面
# 4. 点击"登出" → 回到登录页
✅ 认证功能正常
```

#### 2. 会话管理测试（3分钟）
```bash
# 1. 登录
# 2. 主界面右上角查看连接状态
# 3. 点击"创建会话" → 新会话出现
# 4. 刷新页面 → 会话自动恢复
# 5. 打开浏览器开发者工具（F12）
#    - Console: 查看错误日志
#    - Network: 查看WebSocket连接
✅ 会话管理正常
```

#### 3. 命令执行测试（3分钟）
```bash
# 先启动Claude Code（如果需要）
# 或者mock响应用于测试

# 1. 登录并创建会话
# 2. 在命令输入框输入：
#    echo "Hello Claude"
# 3. 按Enter或点击发送
# 4. 观察输出显示区域
# 5. 检查WebSocket是否正在接收数据
✅ 命令执行正常
```

---

## 📊 查看API文档

后端启动后，自动生成API文档：

```
Swagger UI: http://localhost:8000/docs
ReDoc:      http://localhost:8000/redoc
```

### 常用API速查

```bash
# 注册
POST /api/v1/auth/register
{
  "username": "user",
  "email": "user@example.com",
  "password": "Password123"
}

# 登录
POST /api/v1/auth/login
{
  "username": "user",
  "password": "Password123"
}
# 返回: access_token, refresh_token

# 创建会话
POST /api/v1/sessions
Headers: Authorization: Bearer <token>
{
  "title": "My Session"
}

# 获取会话列表
GET /api/v1/sessions
Headers: Authorization: Bearer <token>

# WebSocket连接
WS /ws/{session_id}
Headers: Authorization: Bearer <token>
```

---

## 🐛 常见问题排查

### 问题1: 数据库连接失败
```bash
# 检查数据库状态
docker-compose ps postgresql

# 如果没有运行
docker-compose up -d postgresql

# 查看日志
docker-compose logs postgresql

# 重置数据库
docker-compose down
docker volume rm remote_vibe_coding_postgres_data  # 如果存在
docker-compose up -d postgresql
```

### 问题2: 后端启动失败
```bash
# 检查依赖
cd backend
pip list | grep fastapi

# 重新安装
pip install -e .

# 检查PYTHONPATH
export PYTHONPATH=/path/to/backend

# 查看Python版本
python3 --version  # 需要 >= 3.11
```

### 问题3: 前端热重载不工作
```bash
cd frontend

# 清除node_modules
rm -rf node_modules
npm install

# 清除缓存
rm -rf .vite
npm run dev
```

### 问题4: WebSocket连接失败
```
1. 检查后端是否在运行: http://localhost:8000/docs
2. 检查前端控制台错误 (F12)
3. 检查网络标签页，查看WS连接状态
4. 确认使用了正确的token
```

---

## 📝 开发任务流程

### 当前优先级

| 优先级 | 用户故事 | 完成% | 下一步 |
|--------|---------|-------|--------|
| P1 🔴  | US1: 远程命令执行 | ✅100% | 写测试 (T043-T048) |
| P2 🟡  | US2: 实时流式输出 | ✅100% | 写测试 (T075-T077) |
| P2 🟡  | US3: 会话管理/重连 | ✅90% | 完成T101, 写测试 |
| P3 🟢  | US4: 文件/工具交互 | ✅70% | 完成T112-T117 |
| P3 🟢  | US5: 多设备/安全 | ✅85% | 完成T130, 写测试 |
| P0 ⚪  | Phase 8: 优化打磨 | 0% | 开始T133+ |

### 开发流程

```
1. 从tasks.md选择任务
2. 如果是[ ]未完成：
   a. 先写测试（TDD）
   b. 确保测试失败
   c. 实现功能
   d. 测试通过
   e. 提交: git commit -m "feat: description (Txxx)"

3. 标记任务: [ ] → [X]
4. 更新tasks.md
5. 运行完整测试
```

---

## 🚢 快速部署

### 本地生产构建

```bash
# 后端构建（纯Python，无需构建）
cd backend
pip install -e .

# 前端生产构建
cd frontend
npm run build
# 输出: dist/

# 启动生产服务
cd backend
python3.12 -m uvicorn src.main:app --host 0.0.0.0 --port 8000

# 提供前端静态文件（需要nginx或fast.io配置）
```

### 使用Docker部署

```bash
# 构建镜像
docker-compose build

# 启动完整栈
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

---

## 📚 有用的文件

| 文件 | 用途 |
|------|------|
| `specs/001-web-app-remote/spec.md` | 完整功能需求 |
| `specs/001-web-app-remote/plan.md` | 技术架构与决策 |
| `specs/001-web-app-remote/tasks.md` | 任务清单 + 优先级 |
| `specs/001-web-app-remote/data-model.md` | 数据库设计 |
| `MVP_SUMMARY.md` | MVP功能总结 |
| `DEVELOPMENT_QUICKSTART.md` | 详细开发指南 |

---

## 🎯 今天应该做什么？

### 如果你要写代码：

```bash
# 1. 选择任务 (查看tasks.md中的[ ]项)
# 2. 启动环境
docker-compose up -d postgresql
cd backend && PYTHONPATH=. python3.12 -m uvicorn src.main:app --reload &
cd ../frontend && npm run dev &

# 3. 开发 + 测试
# - 修改代码
# - 单元测试: pytest tests/ (后端) 或 npm test (前端)
# - 手动测试: 访问 http://localhost:5173

# 4. 提交
git add .
git commit -m "feat: description (TaskID)"
```

### 如果你要写测试：

```bash
# 1. 查看pending测试任务 ([ ] 在tasks.md)
# 2. 在backend/tests/里创建测试文件
# 3. 运行测试 (应该失败)
pytest -xvs backend/tests/contract/test_xxx.py
# 4. 实现功能使测试通过
# 5. 提交

# 示例：
pytest -xvs backend/tests/contract/test_websocket_protocol.py
```

### 如果你要调试：

```bash
# 后端调试
cd backend
python3.12 -m debugpy --listen 5678 -m uvicorn src.main:app --reload

# 前端调试
cd frontend
npm run dev
# 打开 http://localhost:5173
# F12 → Sources标签 → 打断点

# 查看API日志
# 终端输出自动显示所有请求
```

---

## ✨ 相关命令速记

```bash
# 快速检查项目健康状况
docker-compose ps                  # 数据库状态
cd backend && pytest -q            # 后端测试快速检查
cd frontend && npm test -- --run   # 前端快速测试

# 查看最近的git历史
git log --oneline -10

# 重置到上一个已知好的状态
git reset --hard HEAD~1

# 查看哪些任务完成了
grep -c "^\- \[X\]" specs/001-web-app-remote/tasks.md
grep -c "^\- \[ \]" specs/001-web-app-remote/tasks.md
```

---

## 📞 需要帮助？

1. **查看错误日志**：
   - 后端: 终端输出
   - 前端: F12 → Console
   - 数据库: `docker-compose logs postgresql`

2. **查看相关文档**：
   - 项目结构: `specs/001-web-app-remote/plan.md`
   - 数据模型: `specs/001-web-app-remote/data-model.md`
   - 任务列表: `specs/001-web-app-remote/tasks.md`

3. **常见错误速查**：
   - "ModuleNotFoundError": 检查PYTHONPATH
   - "Connection refused": 检查docker-compose是否运行
   - "CORS error": 检查前端VITE_API_URL配置

---

**最后更新**: 2025-10-22
**完成度**: 72.67% (109/150任务)
**下一个检查点**: 完成User Story 1测试 (T043-T048)
