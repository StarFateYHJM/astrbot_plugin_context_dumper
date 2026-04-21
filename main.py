import json
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
        try:
            uid = event.unified_msg_origin
            conv_mgr = self.context.conversation_manager
            
            curr_cid = await conv_mgr.get_curr_conversation_id(uid)
            if not curr_cid:
                yield event.plain_result("❌ 当前没有活跃对话")
                return
            
            conversation = await conv_mgr.get_conversation(uid, curr_cid)
            if not conversation:
                yield event.plain_result("❌ 获取对话失败")
                return
            
            history = conversation.history
            
            # 处理不同类型的 history
            if history is None:
                yield event.plain_result("❌ 对话历史为空")
                return
            
            if isinstance(history, str):
                try:
                    messages = json.loads(history)
                except:
                    yield event.plain_result("❌ 解析对话历史失败")
                    return
            elif isinstance(history, list):
                messages = history
            else:
                yield event.plain_result(f"❌ 未知的历史数据类型: {type(history)}")
                return
            
            if not messages:
                yield event.plain_result("❌ 无对话消息")
                return
            
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
                # 处理 msg 可能是 dict 或其他类型
                if isinstance(msg, dict):
                    role = msg.get("role", "unknown")
                    content = msg.get("content", "")
                else:
                    role = getattr(msg, "role", "unknown")
                    content = getattr(msg, "content", str(msg))
                
                # 确保 content 是字符串
                if not isinstance(content, str):
                    content = json.dumps(content, ensure_ascii=False)
                
                lines.append(f"[{i}] [{role}]")
                lines.append(content)
                lines.append("-" * 40)
                lines.append("")
            
            # 写入文件
            filepath.write_text("\n".join(lines), encoding="utf-8")
            
            yield event.plain_result(f"✅ 已导出 {len(messages)} 条消息\n📁 {filepath}")
            
        except Exception as e:
            logger.error(f"导出失败: {e}", exc_info=True)
            yield event.plain_result(f"❌ 导出失败: {e}")
