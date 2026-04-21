from pathlib import Path
from datetime import datetime

from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger


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
        """一键导出当前会话完整上下文"""
        
        conv_manager = self.context.get_conversation_manager()
        session_id = event.message_obj.session_id
        
        try:
            context_list = await conv_manager.get_context(session_id)
        except:
            yield event.plain_result("❌ 获取上下文失败")
            return
        
        if not context_list:
            yield event.plain_result("❌ 当前会话无上下文")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"context_{session_id.replace(':', '_')}_{timestamp}.txt"
        filepath = self.output_dir / filename
        
        lines = [
            f"会话ID: {session_id}",
            f"导出时间: {datetime.now()}",
            f"消息数量: {len(context_list)}",
            "=" * 50,
            ""
        ]
        
        for i, msg in enumerate(context_list, 1):
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            lines.append(f"[{i}] [{role}]")
            lines.append(content)
            lines.append("-" * 40)
            lines.append("")
        
        filepath.write_text("\n".join(lines), encoding="utf-8")
        
        yield event.plain_result(f"✅ 已导出 {len(context_list)} 条消息\n📁 {filepath}")
