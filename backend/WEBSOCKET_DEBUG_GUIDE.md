# 🔍 WebSocket 通信调试指南

本指南帮助你追踪和诊断前台到后台的完整通信流程。

---

## 📋 完整的消息流程

### 预期流程（正常情况）

```
前端发送消息
  ↓
后端接收消息 📨
  ↓
保存消息到数据库
  ↓
发送命令到 Claude 🔨
  ↓
Claude 执行命令
  ↓
读取 Claude 输出 📦
  ↓
发送输出块到前端
  ↓
执行完成，保存响应
  ↓
发送完成消息到前端 ✅
```

### 日志应该显示的内容

```
2025-10-22 15:50:10 - WebSocket connection request - Session: xxx
2025-10-22 15:50:10 - ✅ WebSocket connection accepted - Session: xxx
2025-10-22 15:50:10 - No active Claude bridge found, starting new process - Session: xxx
2025-10-22 15:50:10 - ✅ Claude process started successfully - Session: xxx
2025-10-22 15:50:15 - 🔨 Command received - Session: xxx, Command: your-command
2025-10-22 15:50:15 - Sending command to Claude - Session: xxx
2025-10-22 15:50:15 - ✅ Command sent to Claude - Session: xxx
2025-10-22 15:50:15 - Starting to read Claude output - Session: xxx
2025-10-22 15:50:16 - 📦 Output chunk [1] - Length: 45, Session: xxx
2025-10-22 15:50:16 - ✅ Command execution complete - Chunks: 5, Time: 1234ms
```

---

## 🔧 调试步骤

### 第 1️⃣ 步：检查 WebSocket 连接

```bash
# 查看日志
tail -f logs/app.log | grep -E "WebSocket|Session"
```

**期望看到：**
```
✅ WebSocket connection accepted - Session: xxx
```

**问题场景：**
- ❌ 看不到这条消息 → WebSocket 连接失败
- ❌ 看到 "auth failed" → Token 验证失败
- ❌ 看到 "Session not found" → Session 不存在或不属于该用户

**解决方案：**
```bash
# 检查 Token 是否有效
# 检查 Session ID 是否正确
# 检查用户是否拥有该 Session
```

---

### 第 2️⃣ 步：检查 Claude 进程启动

```bash
# 查看 Claude 启动日志
tail -f logs/app.log | grep -E "Claude|process"
```

**期望看到：**
```
✅ Claude process started successfully - Session: xxx
```

**问题场景：**
- ❌ 看不到启动消息 → 没有尝试启动
- ❌ 看到"Failed to start" → 启动失败

**详细的失败日志：**
```
❌ Failed to start Claude process - Error: [详细错误信息]
[完整的 Python 堆栈跟踪]
```

**常见错误：**

| 错误 | 原因 | 解决方案 |
|-----|------|--------|
| `Claude executable not found` | CLAUDE_CODE_PATH 错误 | 检查 `.env` 中的路径 |
| `Working directory does not exist` | 工作目录不存在 | 创建目录或修改 CLAUDE_WORKING_DIRECTORY |
| `Permission denied` | 没有执行权限 | 运行 `chmod +x /path/to/claude` |

---

### 第 3️⃣ 步：检查消息是否收到

```bash
# 查看所有消息接收
tail -f logs/app.log | grep "received"
```

**期望看到：**
```
🔨 Command received - Session: xxx, Command: hello
```

**问题场景：**
- ❌ 看不到此消息 → 前端没有发送消息
- ✅ 看到此消息 → 消息成功接收

**前端没有发送消息的原因：**
1. 前端页面卡住
2. WebSocket 连接断开
3. 按钮点击没有触发
4. 浏览器控制台有 JavaScript 错误

**解决方案：**
- 检查浏览器开发者工具（F12） → 控制台
- 查看 Network 标签中的 WebSocket 连接状态
- 查看是否有 JavaScript 错误

---

### 第 4️⃣ 步：检查命令是否发送到 Claude

```bash
# 查看命令发送
tail -f logs/app.log | grep "Command sent to Claude"
```

**期望看到：**
```
✅ Command sent to Claude - Session: xxx
```

**问题场景：**
- ❌ 看不到 → 没有成功发送
- ✅ 看到 → 命令已发送

**可能的错误：**
```
❌ Command execution failed - Error: Process not started
❌ Command execution failed - Error: Broken pipe
```

---

### 第 5️⃣ 步：检查 Claude 是否有输出

```bash
# 查看输出读取
tail -f logs/app.log | grep "📦"
```

**期望看到：**
```
📦 Output chunk [1] - Length: 45, Session: xxx
📦 Output chunk [2] - Length: 38, Session: xxx
...
✅ Command execution complete - Chunks: 5, Time: 1234ms
```

**问题场景：**
- ❌ 看不到任何输出 → Claude 没有产生输出
- ✅ 看到多个块 → 输出正常

**Claude 无输出的可能原因：**
1. Claude 进程没有真正启动（虽然日志说启动了）
2. Claude 不回复标准输入/输出
3. Claude 可执行文件不是真正的 Claude Code
4. Claude 需要交互式终端

**测试 Claude：**
```bash
# 直接运行 Claude 测试
/home/user/.local/bin/claude --version

# 交互式测试
/home/user/.local/bin/claude << EOF
hello
EOF
```

---

## 🎯 快速诊断脚本

使用这个脚本快速诊断问题：

```bash
#!/bin/bash

echo "=== 诊断 Claude 通信问题 ==="

# 1. 检查日志文件
echo ""
echo "1️⃣ 检查日志文件..."
if [ -f logs/app.log ]; then
    echo "✅ 日志文件存在"
    tail -n 20 logs/app.log
else
    echo "❌ 日志文件不存在"
fi

echo ""
echo "2️⃣ 检查 WebSocket 连接..."
grep "WebSocket connection accepted" logs/app.log | tail -1

echo ""
echo "3️⃣ 检查 Claude 启动..."
grep "Claude process started" logs/app.log | tail -1

echo ""
echo "4️⃣ 检查命令接收..."
grep "Command received" logs/app.log | tail -1

echo ""
echo "5️⃣ 检查命令发送..."
grep "Command sent to Claude" logs/app.log | tail -1

echo ""
echo "6️⃣ 检查 Claude 输出..."
grep "📦 Output chunk" logs/app.log | tail -3

echo ""
echo "7️⃣ 检查错误..."
grep "❌" logs/app.log | tail -5
```

---

## 📊 常见错误和解决方案

### 错误 1: 只看到 ping/pong 消息

```
Heartbeat pong received - Session: xxx
```

**问题：** 心跳正常，但没有看到命令消息

**原因：** 前端没有发送命令，可能卡在"Streaming response..."

**解决：**
1. 检查前端是否卡住
2. 刷新页面重试
3. 检查浏览器控制台是否有错误

---

### 错误 2: 看到"Failed to start Claude process"

```
❌ Failed to start Claude process - Session: xxx, Error: ...
```

**检查项：**
1. CLAUDE_CODE_PATH 是否正确
   ```bash
   which claude
   ls -la /path/to/claude
   ```

2. 工作目录是否存在
   ```bash
   ls -la /path/to/working/directory
   ```

3. Claude 是否可执行
   ```bash
   /home/user/.local/bin/claude --version
   ```

---

### 错误 3: 看到"No Claude output"

症状：
```
Starting to read Claude output - Session: xxx
✅ Command execution complete - Chunks: 0, Time: 5000ms
```

**问题：** Claude 进程启动但没有输出

**原因：**
1. Claude 需要交互式终端（TTY）
2. Claude 进程实际没有启动
3. Claude 在等待输入

**测试：**
```bash
# 测试 Claude 的交互
echo "hello" | /home/user/.local/bin/claude
```

---

### 错误 4: WebSocket 连接超时

```
🔌 WebSocket disconnected - Session: xxx
```

**原因：**
1. 网络连接丢失
2. 后端服务崩溃
3. 处理时间过长（前端超时）

---

## 📈 性能指标

从日志中提取性能数据：

```bash
# 提取执行时间
grep "Command execution complete" logs/app.log | \
  grep -oP 'Time: \K[0-9]+' | \
  awk '{sum+=$1; count++} END {print "平均: " sum/count "ms"}'

# 计数命令
grep "Command received" logs/app.log | wc -l

# 统计成功率
echo "成功: $(grep '✅ Command execution complete' logs/app.log | wc -l)"
echo "失败: $(grep '❌ Command execution failed' logs/app.log | wc -l)"
```

---

## 💾 保存日志用于分析

```bash
# 导出最近的日志
tail -n 1000 logs/app.log > debug_logs_$(date +%Y%m%d_%H%M%S).log

# 导出特定会话的日志
grep "Session: xxx" logs/app.log > session_xxx_debug.log

# 导出所有错误
grep "❌\|ERROR" logs/app.log > errors_debug.log
```

---

## 🆘 获取帮助

当报告问题时，请附上：

1. **日志文件** - `logs/app.log` 或导出的日志
2. **会话 ID** - 从日志中复制
3. **前端错误** - 浏览器开发者工具的错误
4. **系统信息**
   ```bash
   which claude
   echo $PATH
   python3 --version
   ```

---

祝调试顺利！如有问题，查看日志就能找到答案。🔍✨
