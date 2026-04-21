from pathlib import Path
from datetime import datetime

from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register


@register(
    "astrbot_plugin_context_dumper",
    "Starfate",
    "上下文导出工具 - 一键导出当前会话完整上下文",
    "1.0.0"
)
class ContextDumper(Star):
    
    def __init__(self, context: Context, config: dict = None):
        super().__init__(context)
        self.output_dir = Path("/AstrBot/data/context_dumps")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    @filter.command("dump")
    async def cmd_dump(self, event: AstrMessageEvent):
        conv_manager = self.context.conversation_manager
        
        # 尝试从 session 获取对话历史
        session_id = event.message_obj.session_id
        session = conv_manager.get_session(session_id)
        
        if not session:
            yield event.plain_result("❌ 未找到会话上下文")
            return
        
        # 从 session 中获取消息列表
        messages = session.messages if hasattr(session, 'messages') else []
        
        if not messages:
            yield event.plain_result("❌ 当前会话无上下文消息")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"context_{session_id.replace(':', '_')}_{timestamp}.txt"
        filepath = self.output_dir / filename
        
        lines = [
            f"会话ID: {session_id}",
            f"导出时间: {datetime.now()}",
            f"消息数量: {len(messages)}",
            "=" * 50,
            ""
        ]
        
        for i, msg in enumerate(messages, 1):
            role = msg.get("role", "unknown") if isinstance(msg, dict) else getattr(msg, "role", "unknown")
            content = msg.get("content", "") if isinstance(msg, dict) else getattr(msg, "content", "")
            lines.append(f"[{i}] [{role}]")
            lines.append(content)
            lines.append("-" * 40)
            lines.append("")
        
        filepath.write_text("\n".join(lines), encoding="utf-8")
        
        yield event.plain_result(f"✅ 已导出 {len(messages)} 条消息\n📁 {filepath}")
