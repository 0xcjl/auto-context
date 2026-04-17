"""
Auto-Context Hook: 智能上下文卫生检查器

自动跟踪：
- 对话长度（turn count）
- 工具重复（tool repetition）

当达到阈值时，通过 auto_context_notifications 模块发送提醒到用户会话。
"""

import threading
from collections import defaultdict
from typing import Any, Dict

# 阈值配置
TURN_THRESHOLD = 20           # 对话长度阈值，达到后提醒
TOOL_REPEAT_THRESHOLD = 5    # 同一工具连续调用次数阈值

# 全局状态存储（线程安全）
_state_lock = threading.Lock()
_session_state: Dict[str, Dict] = defaultdict(lambda: {
    "turn_count": 0,
    "last_tool": None,
    "tool_repeat_count": 0,
    "last_reminder_turn": 0,
})


def _get_session_key(context: Dict) -> str:
    """构建会话唯一标识"""
    platform = context.get("platform", "")
    user_id = context.get("user_id", "")
    session_id = context.get("session_id", "")
    return f"{platform}:{user_id}:{session_id}"


def _send_notification(session_key: str, context: Dict, message: str) -> None:
    """通过 gateway 模块发送通知"""
    try:
        from gateway.auto_context_notifications import enqueue, AutoContextNotification, NotificationPriority
        notification = AutoContextNotification(
            session_key=session_key,
            platform=context.get("platform", ""),
            user_id=context.get("user_id", ""),
            message=message,
            priority=NotificationPriority.MEDIUM,
        )
        enqueue(notification)
    except Exception as e:
        # Fallback to print if import fails
        print(f"[auto-context] 通知失败: {e}", flush=True)


def handle(event_type: str, context: Dict[str, Any]) -> None:
    """
    Hook handler for auto-context monitoring.
    
    Events:
    - session:start: 初始化会话状态
    - agent:step: 跟踪工具使用和对话长度
    - agent:end: 预留（通知在 agent:step 检测到问题时发送）
    """
    session_key = _get_session_key(context)
    
    if event_type == "session:start":
        # 重置会话状态
        with _state_lock:
            _session_state[session_key] = {
                "turn_count": 0,
                "last_tool": None,
                "tool_repeat_count": 0,
                "last_reminder_turn": 0,
            }
        
        # 清理该 session 的旧通知
        try:
            from gateway.auto_context_notifications import clear
            clear(session_key)
        except Exception:
            pass
        return
    
    if event_type == "agent:step":
        iteration = context.get("iteration", 0)
        tool_names = context.get("tool_names", [])
        
        with _state_lock:
            state = _session_state[session_key]
            state["turn_count"] = iteration
            
            # 工具重复检测
            if tool_names:
                current_tool = tool_names[0] if tool_names else None
                if current_tool == state["last_tool"]:
                    state["tool_repeat_count"] += 1
                else:
                    state["tool_repeat_count"] = 1
                    state["last_tool"] = current_tool
            
            # 检查是否需要发送通知
            needs_notification = False
            notification_message = ""
            
            # 1. 对话长度提醒（每 TURN_THRESHOLD 轮提醒一次）
            if iteration - state["last_reminder_turn"] >= TURN_THRESHOLD:
                needs_notification = True
                state["last_reminder_turn"] = iteration
                notification_message = f"📊 会话已达 {iteration} 轮，上下文可能变长。\n\n💡 建议：/btw 切换后台 或 /new 新会话"
            
            # 2. 工具重复提醒
            if state["tool_repeat_count"] >= TOOL_REPEAT_THRESHOLD:
                needs_notification = True
                notification_message = f"🔧 工具 '{state['last_tool']}' 被连续调用 {state['tool_repeat_count']} 次，可能陷入循环"
            
            if needs_notification:
                _send_notification(session_key, context, notification_message)
        
        return
    
    # agent:end 不需要特殊处理
    return
