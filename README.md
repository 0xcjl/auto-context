# auto-context

> Intelligent context hygiene checker for Hermes Agent

[中文](./README_zh.md)

## Overview

**auto-context** is a context hygiene checker for Hermes Agent. It automatically monitors conversation length and tool repetition, sending proactive reminders to users when thresholds are reached.

## Features

### Automatic Detection

| Detection | Threshold | Action |
|-----------|-----------|--------|
| Conversation Length | Every 20 turns | Send reminder |
| Tool Repetition | 5+ consecutive | Send reminder |

### Reminder Examples

When conversation reaches 20 turns:
```
📊 会话已达 20 轮，上下文可能变长。

💡 建议：/btw 切换后台 或 /new 新会话
```

When a tool is called repeatedly:
```
🔧 工具 'terminal' 被连续调用 5 次，可能陷入循环
```

## Architecture

```
agent:step → Hook detects threshold → enqueue_notification()
                                              ↓
agent:end → Gateway drains queue → Injects into user session
```

Components:
- **Hook Handler**: `hooks/auto-context/handler.py`
- **Notification Queue**: `gateway/auto_context_notifications.py` (Hermes core module)
- **Gateway Integration**: Drain logic in `gateway/run.py`

## How It Works

1. Hook listens to `session:start`, `agent:step`, `agent:end` events
2. On `agent:step`, monitors turn count and tool usage
3. When threshold is reached, enqueues a notification
4. On `agent:end`, gateway drains the queue and injects notifications into the conversation

## Installation

auto-context hook is loaded from `~/.hermes/hooks/auto-context/` by Hermes Agent's hook system.

## Requirements

- Hermes Agent with hook system support
- Gateway restart after installation

## Credits

- [Hermes Agent](https://github.com/0xcjl/hermes-agent)
- 0xcjl

## License

MIT
