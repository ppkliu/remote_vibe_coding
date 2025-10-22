# 📊 日志和配置指南

本指南说明如何使用新的日志系统和工作目录配置。

---

## 🔓 临时启用 SQLAlchemy SQL 日志

如果你需要调试数据库问题，可以临时启用 SQL 查询日志：

### 方法 1：修改代码（临时）

编辑 `backend/src/main.py` 的启动部分：

```python
# 在 setup_logging() 后添加
import logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
```

### 方法 2：通过环境变量（更方便）

在 `backend/.env` 中添加：

```bash
SQLALCHEMY_LOG_LEVEL=INFO
```

然后在 `logging_config.py` 中使用：

```python
from ..config import get_settings
settings = get_settings()

sqlalchemy_level = getattr(logging, settings.SQLALCHEMY_LOG_LEVEL, logging.WARNING)
logging.getLogger('sqlalchemy.engine').setLevel(sqlalchemy_level)
```

### 方法 3：命令行（一次性）

```bash
# 直接在启动时设置
PYTHONPATH=. python3 -c "
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
" && uvicorn src.main:app --reload
```

### 启用后看到的日志

```
INFO sqlalchemy.engine.Engine SELECT users.id, users.username, users.email
FROM users
WHERE users.id = $1::UUID
[generated in 0.00123s] (UUID('xxx'),)
```

### 何时需要启用 SQL 日志

- ❌ **一般开发** - 不需要，太吵
- ✅ **数据库问题** - 需要查看 SQL 查询
- ✅ **性能优化** - 需要看慢查询
- ✅ **数据不一致** - 需要查看实际执行的 SQL

---

## 📝 日志系统配置

### 日志文件位置

日志文件存储在 `logs/` 目录中（可在 `.env` 中配置）：

```
logs/
├── app.log          # 主日志文件（最新日志）
├── app.log.1        # 第一个备份（已满 3MB）
├── app.log.2        # 第二个备份（已满 3MB）
└── app.log.3        # 第三个备份（已满 3MB）
```

**总容量**: 3MB × 4 个文件 = 12MB 的日志历史记录

### 日志轮转机制

- **maxBytes**: 3MB - 当日志文件达到 3MB 时自动轮转
- **backupCount**: 3 - 保留 3 个备份文件（加上主文件共 4 个）
- **轮转方式**: 基于文件大小（而非时间）

### 配置日志级别

在 `backend/.env` 中设置：

```bash
# 日志输出目录
LOG_DIR=logs

# 日志级别 (DEBUG < INFO < WARNING < ERROR < CRITICAL)
LOG_LEVEL=INFO
```

### 日志级别说明

| 级别 | 用途 | 包含内容 |
|-----|------|--------|
| **DEBUG** | 开发调试 | 所有详细信息，包括变量值、函数调用 |
| **INFO** | 正常运行 | 应用启动、会话创建、Claude 进程启动 |
| **WARNING** | 潜在问题 | 不会导致错误的警告 |
| **ERROR** | 错误 | 失败的操作、异常情况 |
| **CRITICAL** | 严重错误 | 应用无法继续运行的错误 |

### 日志格式

```
2025-10-22 15:49:30 - src.services.claude_bridge - INFO - [claude_bridge.py:47] - ✅ Claude Code process started successfully - PID: 12345
```

格式: `时间 - 模块 - 级别 - [文件:行号] - 消息`

### 默认行为：SQLAlchemy 日志被抑制

**重要：** SQLAlchemy 的 SQL 查询日志默认被设置为 WARNING 级别。

这意味着：
- ✅ **控制台输出很干净** - 只显示应用级日志
- ✅ **文件日志完整** - `logs/app.log` 中有所有日志
- ❌ **默认不显示 SQL 查询** - SELECT/INSERT/UPDATE 不显示在控制台

**原因：** 大多数情况下，SQL 查询太多，会淹没重要的应用日志

---

## 🚀 工作目录配置

### 用途

指定 Claude Code 执行命令时的工作目录。这样可以让 Claude 在特定的项目文件夹中操作。

### 配置方法

在 `backend/.env` 中设置：

```bash
# Claude 工作目录 (相对或绝对路径)
CLAUDE_WORKING_DIRECTORY=.
```

### 示例配置

**示例 1**: 当前目录
```bash
CLAUDE_WORKING_DIRECTORY=.
```

**示例 2**: 特定项目目录
```bash
CLAUDE_WORKING_DIRECTORY=/path/to/my/project
CLAUDE_WORKING_DIRECTORY=/home/user/workspace/my-app
```

**示例 3**: 相对路径
```bash
CLAUDE_WORKING_DIRECTORY=./src
CLAUDE_WORKING_DIRECTORY=../my-codebase
```

### 工作目录如何工作

1. 用户创建会话
2. 后端读取 `CLAUDE_WORKING_DIRECTORY` 配置
3. Claude 进程以该目录为 `cwd` 启动
4. Claude 所有命令都在该目录中执行

```python
# 在 session_manager.py 中
working_dir = settings.CLAUDE_WORKING_DIRECTORY  # 从 .env 读取
pid = await bridge.start_process(working_directory=working_dir)
```

---

## 🔍 查看日志

### 查看最新日志

```bash
# 实时查看日志
tail -f logs/app.log

# 查看最后 50 行
tail -n 50 logs/app.log

# 查看最后 100 行
tail -n 100 logs/app.log
```

### 搜索特定内容

```bash
# 搜索错误
grep "❌" logs/app.log

# 搜索成功消息
grep "✅" logs/app.log

# 搜索 Claude 相关日志
grep "Claude" logs/app.log

# 搜索特定会话
grep "session-uuid-here" logs/app.log

# 搜索特定时间段
grep "2025-10-22 15:" logs/app.log
```

### 查看旧的备份日志

```bash
# 查看第一个备份
cat logs/app.log.1

# 搜索备份中的内容
grep "error" logs/app.log.1 logs/app.log.2
```

### 完整的日志分析

```bash
# 统计不同日志级别的数量
grep -c "INFO" logs/app.log
grep -c "ERROR" logs/app.log
grep -c "❌" logs/app.log

# 查看所有错误
grep "ERROR\|❌" logs/app.log

# 按时间查看日志
sort logs/app.log | tail -20
```

---

## 🐛 调试 Claude 通信问题

### 常见日志消息

#### ✅ 成功消息

```
Starting Claude Code process
Claude executable path: /home/user/.local/bin/claude
Working directory: /path/to/project
✅ Claude Code process started successfully - PID: 12345
Sending command to Claude: your-command-here
✅ Command sent successfully
Starting to read Claude Code output...
📦 Claude output [1]: Response from Claude...
```

#### ❌ 错误消息

```
❌ Claude executable not found at: /wrong/path/to/claude
❌ Working directory does not exist: /nonexistent/path
❌ Failed to start Claude Code process: [error details]
❌ Cannot send command - process not started
❌ Error reading Claude output: [error details]
```

### 调试步骤

#### 1. 检查 Claude 可执行文件路径

```bash
# 查看日志中的路径
grep "Claude executable path" logs/app.log

# 验证路径是否存在
which claude
ls -la /home/user/.local/bin/claude
```

#### 2. 检查工作目录

```bash
# 查看日志中使用的工作目录
grep "working directory\|Working directory" logs/app.log

# 验证目录是否存在
ls -la /path/to/project
cd /path/to/project && pwd
```

#### 3. 检查进程启动

```bash
# 在日志中查找 PID
grep "PID" logs/app.log

# 验证进程是否在运行
ps aux | grep claude
ps -p <PID>  # 检查特定 PID
```

#### 4. 检查通信错误

```bash
# 查看所有错误
grep "❌\|ERROR" logs/app.log

# 查看特定会话的日志
grep "session-id-here" logs/app.log

# 包含上下文的错误
grep -A 5 -B 5 "Claude output" logs/app.log
```

---

## 🔧 配置示例

### 生产环境配置

```bash
# backend/.env
LOG_DIR=/var/log/claude-remote
LOG_LEVEL=INFO
CLAUDE_CODE_PATH=/usr/local/bin/claude
CLAUDE_WORKING_DIRECTORY=/home/claude-projects
```

### 开发环境配置（详细日志）

```bash
# backend/.env
LOG_DIR=logs
LOG_LEVEL=DEBUG
CLAUDE_CODE_PATH=/home/user/.local/bin/claude
CLAUDE_WORKING_DIRECTORY=.
```

### 测试环境配置

```bash
# backend/.env
LOG_DIR=./test-logs
LOG_LEVEL=DEBUG
CLAUDE_CODE_PATH=/path/to/test/claude
CLAUDE_WORKING_DIRECTORY=./test-project
```

---

## 📚 日志示例

### 完整的会话启动日志

```
2025-10-22 15:50:00 - src.main - INFO - ════════════════════════════════════════════════════════════════════════════════
2025-10-22 15:50:00 - src.main - INFO - 🚀 Claude Code Remote Web Controller - Starting
2025-10-22 15:50:00 - src.main - INFO - ════════════════════════════════════════════════════════════════════════════════
2025-10-22 15:50:00 - src.main - INFO - Server: 0.0.0.0:8000
2025-10-22 15:50:00 - src.main - INFO - Debug mode: True
2025-10-22 15:50:00 - src.main - INFO - Claude Code: /home/user/.local/bin/claude
2025-10-22 15:50:00 - src.main - INFO - Working Directory: /path/to/project
2025-10-22 15:50:00 - src.main - INFO - Log Directory: logs
2025-10-22 15:50:00 - src.main - INFO - ════════════════════════════════════════════════════════════════════════════════

2025-10-22 15:50:10 - src.services.session_manager - INFO - Starting Claude process for session: a1b2c3d4-e5f6-7890-abcd-ef1234567890
2025-10-22 15:50:10 - src.services.session_manager - INFO - Using working directory: /path/to/project
2025-10-22 15:50:10 - src.services.claude_bridge - INFO - Starting Claude Code process
2025-10-22 15:50:10 - src.services.claude_bridge - INFO - Claude executable path: /home/user/.local/bin/claude
2025-10-22 15:50:10 - src.services.claude_bridge - INFO - Working directory: /path/to/project
2025-10-22 15:50:10 - src.services.claude_bridge - INFO - ✅ Claude Code process started successfully - PID: 12345

2025-10-22 15:50:10 - src.services.session_manager - INFO - ✅ Claude process started - Session: a1b2c3d4-e5f6-7890-abcd-ef1234567890, PID: 12345
2025-10-22 15:50:10 - src.services.session_manager - INFO - ✅ Session activated: a1b2c3d4-e5f6-7890-abcd-ef1234567890

2025-10-22 15:50:15 - src.services.claude_bridge - DEBUG - Sending command to Claude: hello
2025-10-22 15:50:15 - src.services.claude_bridge - DEBUG - ✅ Command sent successfully
2025-10-22 15:50:15 - src.services.claude_bridge - INFO - Starting to read Claude Code output...
2025-10-22 15:50:16 - src.services.claude_bridge - DEBUG - 📦 Claude output [1]: Hi there! How can I help you today?
```

---

## 📞 需要帮助？

如果遇到问题：

1. **检查日志文件** - `logs/app.log`
2. **启用 DEBUG 模式** - 设置 `LOG_LEVEL=DEBUG`
3. **验证配置** - 检查 `.env` 中的路径
4. **查看最新日志** - `tail -f logs/app.log`
5. **搜索错误** - `grep "❌\|ERROR" logs/app.log`

祝调试愉快！🔍
