# 🔧 开发环境完整设置指南

**用途**: 本地开发 Claude Code Remote Web Controller
**时间**: 10-15 分钟
**最后更新**: 2025-10-22

---

## 📋 前置要求

### 必须安装
- **Python 3.12+**（后端运行时）
- **Node.js 18+**（前端运行时）
- **npm 或 yarn**（前端包管理）
- **PostgreSQL**（数据库，推荐用 Docker）
- **Git**（版本控制）

### 验证环境

```bash
# 检查 Python
python3 --version  # >= 3.12

# 检查 Node
node --version  # >= 18
npm --version

# 检查 Docker（可选但推荐）
docker --version
docker-compose --version
```

---

## 🚀 快速启动（3 步）

### 步骤 1️⃣: 启动数据库

**选项 A: 使用 Docker（推荐）**

```bash
# 在项目根目录执行
docker-compose up -d postgres

# 验证数据库连接
docker-compose exec postgres psql -U admin -d claude_remote -c "SELECT version();"
```

**选项 B: 本地 PostgreSQL**

```bash
# 确保 PostgreSQL 正在运行
# macOS: brew services start postgresql
# Linux: sudo systemctl start postgresql
# Windows: 启动 PostgreSQL 服务

# 创建数据库（如果还没有）
psql -U postgres -c "CREATE DATABASE claude_remote;"
```

---

### 步骤 2️⃣: 配置和启动后端

**在终端 1 中执行：**

```bash
# 进入后端目录
cd backend

# 复制环境配置文件
cp .env.example .env

# 编辑 .env 文件（配置重要参数）
# 需要修改的关键参数：
# - CLAUDE_CODE_PATH=/home/image/.local/bin/claude  (your claude executable path)
# - DATABASE_URL=postgresql+asyncpg://admin:password@localhost:25432/claude_remote
# - CORS_ORIGINS=http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173
# - JWT_SECRET=your-secret-key-min-32-characters-long

# 打开编辑器
nano .env
# 或使用你喜欢的编辑器 (vim, code, etc.)
```

**编辑 .env 的关键参数：**

| 参数 | 值 | 说明 |
|-----|-----|------|
| `CLAUDE_CODE_PATH` | `/home/image/.local/bin/claude` | Claude Code 可执行文件路径（使用 `which claude` 查找） |
| `DATABASE_URL` | `postgresql+asyncpg://admin:password@localhost:25432/claude_remote` | 数据库连接字符串（Docker 端口 25432） |
| `CORS_ORIGINS` | `http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173` | 允许的前端源地址 |
| `JWT_SECRET` | `your-secret-key-min-32-characters-...` | JWT 密钥（至少 32 字符） |

**保存后，继续设置后端：**

```bash
# 安装依赖
pip install -q uv
uv pip install -q -e .

# 运行数据库迁移（创建表）
PYTHONPATH=. python3 -m alembic upgrade head

# 启动后端开发服务器
uvicorn src.main:app --reload

# 预期输出：
# INFO:     Uvicorn running on http://0.0.0.0:8000
# INFO:     Application startup complete
```

✅ **后端已启动**: http://localhost:8000
📚 **API 文档**: http://localhost:8000/docs

---

### 步骤 3️⃣: 启动前端

**在终端 2 中执行：**

```bash
# 进入前端目录
cd frontend

# 复制环境配置文件
cp .env.example .env

# 如果需要修改，编辑 .env
# 通常默认值就可以：
# - VITE_API_URL=http://localhost:8000/api/v1
# - VITE_WS_URL=ws://localhost:8000/ws

nano .env  # 如需编辑

# 安装依赖
npm install

# 启动前端开发服务器
npm run dev
# 或使用 npx 直接运行
# npx vite dev

# 预期输出：
# VITE v5.0.0  ready in 234 ms
# ➜  Local:   http://localhost:5173/
```

✅ **前端已启动**: http://localhost:5173

---

## ✨ 开发工作流

### 完整的 3 个终端设置

现在你应该在运行以下 3 个进程：

**终端 1: 后端**
```bash
cd backend
uvicorn src.main:app --reload
# 监听: http://localhost:8000
```

**终端 2: 前端**
```bash
cd frontend
npm run dev
# 监听: http://localhost:5173
```

**终端 3: 可选 - 运行测试**
```bash
cd frontend
npm run test:ui
# 监听: http://localhost:51204 (Vitest UI)
```

### 访问应用

在浏览器打开：**http://localhost:5173**

1. 点击 "Register" 创建新账户
2. 输入用户名、邮箱、密码（最多 72 字符）
3. 登录
4. 点击 "New Session" 创建一个 Claude 会话
5. 输入命令（例如: `hello` 或 `你好`）
6. 查看 Claude 的实时响应

---

## 🔄 .env.example 配置说明

### Backend (.env.example)

**数据库配置**
```bash
# 本地 PostgreSQL
DATABASE_URL=postgresql+asyncpg://admin:password@localhost:5432/claude_remote

# Docker Compose
DATABASE_URL=postgresql+asyncpg://admin:password@localhost:25432/claude_remote
```

**认证配置**
```bash
JWT_SECRET=your-secret-key-min-32-characters-long-please-change-this
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7
```

**Claude Code 路径**
```bash
# 查找 claude 可执行文件
which claude
# 输出: /home/image/.local/bin/claude

# 在 .env 中设置
CLAUDE_CODE_PATH=/home/image/.local/bin/claude
```

**CORS 配置**
```bash
# 允许以下源访问后端
CORS_ORIGINS=http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173
```

### Frontend (.env.example)

```bash
# API 端点
VITE_API_URL=http://localhost:8000/api/v1

# WebSocket 端点（实时通信）
VITE_WS_URL=ws://localhost:8000/ws
```

---

## 🛠️ 常见开发任务

### 后端

```bash
cd backend

# 检查代码风格
pylint src/

# 运行测试
pytest tests/

# 迁移数据库
alembic upgrade head

# 查看日志
tail -f logs/app.log
```

### 前端

```bash
cd frontend

# 检查代码风格
npm run lint

# 运行测试
npm run test

# 测试 UI 模式
npm run test:ui

# 构建生产版本
npm run build

# 预览生产构建
npm run preview

# 类型检查
npm run type-check
```

---

## 🐛 故障排除

### 问题: 后端启动失败

**错误**: `ModuleNotFoundError: No module named 'src'`

```bash
# 解决: 设置 PYTHONPATH
cd backend
export PYTHONPATH=.
uvicorn src.main:app --reload
```

**错误**: `psycopg2.OperationalError: connection refused`

```bash
# 检查数据库是否运行
docker-compose ps postgres

# 如果没运行，启动它
docker-compose up -d postgres

# 等待 5 秒后重试
```

### 问题: 前端启动失败

**错误**: `Port 5173 already in use`

```bash
# 使用不同的端口
npx vite dev --port 5174

# 或找到占用的进程并关闭
lsof -i :5173
kill -9 <PID>
```

**错误**: `Cannot find module '@/'`

```bash
# 重新安装依赖
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### 问题: CORS 错误

**浏览器控制台显示**:
```
Access to XMLHttpRequest at 'http://localhost:8000/api/v1/...'
has been blocked by CORS policy
```

**解决**:
1. 检查后端正在运行
2. 检查 `backend/.env` 中的 `CORS_ORIGINS` 包含你的前端 URL
3. 重启后端服务

```bash
# 编辑 .env
cd backend
nano .env

# 确保包含：
# CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# 重启
uvicorn src.main:app --reload
```

### 问题: WebSocket 连接失败

**症状**: 创建会话后页面卡在 "Streaming response..."

**检查清单**:
1. ✅ 后端是否运行？
2. ✅ `CLAUDE_CODE_PATH` 是否正确设置？
3. ✅ Claude Code 是否安装？

```bash
# 验证 Claude Code 已安装
which claude

# 测试运行
/home/image/.local/bin/claude --version

# 检查后端日志中是否有错误
# 查看 "Streaming response..." 时的日志消息
```

---

## 📚 详细文档

- **后端开发**: `backend/README.md`
- **前端开发**: `frontend/DEVELOPMENT.md`
- **API 文档**: http://localhost:8000/docs (运行时访问)
- **部署指南**: `DEPLOYMENT_GUIDE.md`

---

## 🎯 开发检查清单

在提交代码前，确保：

- [ ] 后端通过了 linting 检查
- [ ] 前端通过了类型检查（`npm run type-check`）
- [ ] 所有测试都通过（`npm run test`）
- [ ] `.env` 文件**不**被提交（应在 `.gitignore` 中）
- [ ] 提交消息遵循规范

```bash
# 完整的开发流程检查
cd backend
npm run lint
npm run type-check
npm run test

cd ../frontend
npm run lint
npm run type-check
npm run test
```

---

## 🆘 需要帮助？

遇到问题？检查：

1. **本文档的故障排除部分**
2. **`frontend/DEVELOPMENT.md`** - 前端特定问题
3. **`backend/README.md`** - 后端特定问题
4. **`DEPLOYMENT_GUIDE.md`** - 部署问题

或创建一个 GitHub Issue 描述你的问题！

---

**祝你开发愉快！** 🚀
