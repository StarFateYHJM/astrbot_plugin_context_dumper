import json
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
        # 获取统一会话标识
        uid = event.unified_msg_origin
        
        # 获取对话管理器
        conv_mgr = self.context.conversation_manager
        
        # 获取当前对话 ID
        curr_cid = await conv_mgr.get_curr_conversation_id(uid)
        if not curr_cid:
            yield event.plain_result("❌ 当前没有活跃对话")
            return
        
        # 获取完整对话对象
        conversation = await conv_mgr.get_conversation(uid, curr_cid)
        if not conversation:
            yield event.plain_result("❌ 获取对话失败")
            return
        
        # 解析对话历史
        history_str = conversation.history
        if not history_str:
            yield event.plain_result("❌ 对话历史为空")
            return
        
        try:
            messages = json.loads(history_str)
        except:
            yield event.plain_result("❌ 解析对话历史失败")
            return
        
        if not messages:
            yield event.plain_result("❌ 无对话消息")
            return
        
        # 保存到文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"context_{timestamp}.txt"
        filepath = self.output_dir / filename
        
        lines = [
            f"会话ID: {curr_cid}",
            f"用户标识: {uid}",
            f"导出时间: {datetime.now()}",
            f"消息数量: {len(messages)}",
            "=" * 50,
            ""
        ]
        
        for i, msg in enumerate(messages, 1):
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            lines.append(f"[{i}] [{role}]")
            lines.append(content)
            lines.append("-" * 40)
            lines.append("")
        
        filepath.write_text("\n".join(lines), encoding="utf-8")
        
        yield event.plain_result(f"✅ 已导出 {len(messages)} 条消息\n📁 {filepath}")
