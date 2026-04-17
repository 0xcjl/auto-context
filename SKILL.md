---
name: auto-context
description: >
  智能上下文卫生检查器。自动跟踪对话长度、检测工具重复，
  在达到阈值时主动提醒用户。建议：/btw、/new 或继续当前话题。
  基于 Hermes Agent Hook 系统实现。
license: MIT
compatibility: hermes-agent
tags:
  - context-management
  - session-health
  - productivity
metadata:
  author: 0xcjl
  repo: https://github.com/0xcjl/auto-context
---

# AutoContext: 智能上下文卫生检查器

主动监控会话状态，在达到阈值时智能提醒用户。

## 功能

### 自动检测

| 检测项 | 阈值 | 动作 |
|--------|------|------|
| 对话长度 | 每20轮 | 发送提醒 |
| 工具重复 | 连续5次 | 发送提醒 |

### 提醒示例

当对话达到20轮时，用户会收到：
```
📊 会话已达 20 轮，上下文可能变长。

💡 建议：/btw 切换后台 或 /new 新会话
```

当工具连续调用5次时：
```
🔧 工具 'terminal' 被连续调用 5 次，可能陷入循环
```

## 架构

```
agent:step → 钩子检测阈值 → enqueue_notification()
                                    ↓
agent:end → gateway drain 队列 → 注入到用户会话
```

- **Hook Handler**: `hooks/auto-context/handler.py`
- **通知队列**: `gateway/auto_context_notifications.py` (Hermes 核心模块)
- **Gateway 集成**: `gateway/run.py` 中的 drain 逻辑

## 安装

auto-context hook 通过 Hermes Agent 的 hook 系统工作：

1. Hook 文件自动从 `~/.hermes/hooks/auto-context/` 加载
2. Gateway 在 `agent:end` 后注入提醒到用户会话

## 触发条件

- `session:start` - 初始化会话状态
- `agent:step` - 跟踪工具使用和对话长度
- `agent:end` - 预留（通知在 step 时发送）

## Credits

- Hermes Agent Hook System
- 0xcjl
