#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
REPL交互模块
"""

import os
import sys
import readline
import atexit
from typing import Optional, Tuple
from polo.memory import Memory
from polo.tools import Tools
from polo.ai_agent import AIAgent


class PoloREPL:
    """Polo REPL - 交互式命令行界面"""

    def __init__(self, use_memory: bool = True, memory_file: str = "polo_memory.json"):
        self.use_memory = use_memory
        self.memory_file = memory_file
        self.running = True

        # 初始化组件
        self.memory = Memory(memory_file) if use_memory else None
        self.tools = Tools()
        self.agent = AIAgent(memory=self.memory, tools=self.tools, model_name="gemini-2.5-flash")

        # 设置readline历史
        self.history_file = os.path.expanduser("~/.polo_history")
        self._setup_readline()

        # 命令计数器
        self.command_count = 0

        # 内置命令映射
        self.builtin_commands = {
            "help": self.cmd_help,
            "exit": self.cmd_exit,
            "quit": self.cmd_exit,
            "clear": self.cmd_clear,
            "history": self.cmd_history,
            "memory": self.cmd_memory,
            "stats": self.cmd_stats,
            "tools": self.cmd_tools,
            "about": self.cmd_about,
        }

    def _setup_readline(self):
        """设置readline历史记录"""
        try:
            if os.path.exists(self.history_file):
                readline.read_history_file(self.history_file)

            # 设置历史记录长度
            readline.set_history_length(1000)

            # 注册退出时保存历史
            atexit.register(self._save_history)

        except Exception:
            pass  # readline可能不可用

    def _save_history(self):
        """保存readline历史"""
        try:
            readline.write_history_file(self.history_file)
        except Exception:
            pass

    def _parse_command(self, user_input: str) -> Tuple[str, Optional[str]]:
        """解析用户输入"""
        user_input = user_input.strip()

        if not user_input:
            return "empty", None

        # 检查是否是内置命令
        if user_input.startswith("/"):
            parts = user_input[1:].split(" ", 1)
            command = parts[0].lower()
            args = parts[1] if len(parts) > 1 else None

            if command in self.builtin_commands:
                return command, args
            else:
                return "unknown_builtin", command

        # 检查是否是工具命令（以!开头）
        if user_input.startswith("!"):
            return self._parse_tool_command(user_input[1:])

        # 默认为聊天
        return "chat", user_input

    def _parse_tool_command(self, command: str) -> Tuple[str, Optional[str]]:
        """解析工具命令"""
        parts = command.split(" ", 1)
        tool_name = parts[0].lower()
        args = parts[1] if len(parts) > 1 else None

        tool_mapping = {
            "shell": "tool_shell",
            "sh": "tool_shell",
            "read": "tool_read",
            "cat": "tool_read",
            "write": "tool_write",
            "echo": "tool_write",
            "ls": "tool_ls",
            "list": "tool_ls",
            "find": "tool_find",
            "search": "tool_find",
            "copy": "tool_copy",
            "cp": "tool_copy",
            "move": "tool_move",
            "mv": "tool_move",
            "delete": "tool_delete",
            "rm": "tool_delete",
            "info": "tool_info",
            "sysinfo": "tool_info",
        }

        return tool_mapping.get(tool_name, "unknown_tool"), args

    def run(self) -> int:
        """运行REPL主循环"""
        self._show_banner()

        while self.running:
            try:
                # 生成提示符
                prompt = self._get_prompt()

                # 获取用户输入
                user_input = input(prompt).strip()

                if not user_input:
                    continue

                self.command_count += 1

                # 解析和执行命令
                command_type, args = self._parse_command(user_input)
                response = self._execute_command(command_type, args, user_input)

                if response:
                    print(response)
                print()  # 空行分隔

            except KeyboardInterrupt:
                print("\n\n👋 按 Ctrl+C 退出，或输入 /exit")
                print()
            except EOFError:
                print("\n👋 再见！")
                break
            except Exception as e:
                print(f"❌ 发生错误: {e}")
                print()

        return 0

    def _show_banner(self):
        """显示欢迎横幅"""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                     🤖 Polo AI Assistant                     ║
║                    Mini Claude Code v0.2.0                   ║
╠══════════════════════════════════════════════════════════════╣
║  💬 聊天模式：直接输入消息                                      ║
║  🛠️  工具命令：!command args                                   ║
║  ⚙️  内置命令：/command args                                   ║
║  📚 帮助信息：/help                                           ║
║  👋 退出程序：/exit 或 Ctrl+D                                  ║
╚══════════════════════════════════════════════════════════════╝
"""
        print(banner)

        if self.memory:
            stats = self.memory.get_conversation_stats()
            if stats["total"] > 0:
                print(f"📝 欢迎回来！我记住了我们之前的 {stats['total']} 次对话。")
            else:
                print("🆕 这是我们的第一次对话，我会记住我们的交流内容。")
        else:
            print("⚠️  记忆功能已禁用，不会保存对话历史。")
        print()

    def _get_prompt(self) -> str:
        """生成命令提示符"""
        cwd = os.path.basename(os.getcwd())
        return f"👤 [{cwd}]({self.command_count}): "

    def _execute_command(
        self, command_type: str, args: Optional[str], original_input: str
    ) -> Optional[str]:
        """执行命令"""
        # 内置命令
        if command_type in self.builtin_commands:
            return self.builtin_commands[command_type](args)

        # 工具命令
        elif command_type.startswith("tool_"):
            return self._execute_tool_command(command_type[5:], args, original_input)

        # 聊天
        elif command_type == "chat":
            return self._execute_chat(original_input)

        # 未知命令
        elif command_type == "unknown_builtin":
            return f"❌ 未知的内置命令: /{args}\n💡 输入 /help 查看可用命令"

        elif command_type == "unknown_tool":
            return f"❌ 未知的工具命令: !{args}\n💡 输入 /tools 查看可用工具"

        elif command_type == "empty":
            return None

        else:
            return f"❌ 未知命令类型: {command_type}"

    def _execute_chat(self, user_input: str) -> str:
        """执行聊天"""
        try:
            response = self.agent.chat(user_input)
            return f"🤖 {response}"
        except Exception as e:
            return f"❌ 聊天出错: {e}"

    def _execute_tool_command(
        self, tool_name: str, args: Optional[str], original_input: str
    ) -> str:
        """执行工具命令"""
        try:
            if tool_name == "shell":
                if not args:
                    return "❌ 请提供要执行的命令"
                result = self.tools.execute_shell(args)
                response = f"🔧 执行: {args}\n{result}"

            elif tool_name == "read":
                if not args:
                    return "❌ 请提供要读取的文件路径"
                result = self.tools.read_file(args)
                response = result

            elif tool_name == "write":
                if not args:
                    return "❌ 请提供文件路径和内容，格式: !write filepath content"
                parts = args.split(" ", 1)
                if len(parts) < 2:
                    return "❌ 格式错误，应为: !write filepath content"
                filepath, content = parts
                result = self.tools.write_file(filepath, content)
                response = result

            elif tool_name == "ls":
                path = args or "."
                result = self.tools.list_directory(path)
                response = result

            elif tool_name == "find":
                if not args:
                    return "❌ 请提供搜索模式"
                result = self.tools.find_files(args)
                response = result

            elif tool_name == "copy":
                if not args:
                    return "❌ 请提供源文件和目标文件，格式: !copy src dst"
                parts = args.split(" ", 1)
                if len(parts) < 2:
                    return "❌ 格式错误，应为: !copy src dst"
                src, dst = parts
                result = self.tools.copy_file(src, dst)
                response = result

            elif tool_name == "move":
                if not args:
                    return "❌ 请提供源文件和目标文件，格式: !move src dst"
                parts = args.split(" ", 1)
                if len(parts) < 2:
                    return "❌ 格式错误，应为: !move src dst"
                src, dst = parts
                result = self.tools.move_file(src, dst)
                response = result

            elif tool_name == "delete":
                if not args:
                    return "❌ 请提供要删除的文件路径"
                result = self.tools.delete_file(args)
                response = result

            elif tool_name == "info":
                result = self.tools.get_system_info()
                response = result

            else:
                response = f"❌ 未实现的工具命令: {tool_name}"

            # 保存工具使用到记忆
            if self.memory:
                self.memory.add_conversation(
                    original_input,
                    response,
                    metadata={"type": "tool_usage", "tool": tool_name},
                )

            return response

        except Exception as e:
            return f"❌ 执行工具命令出错: {e}"

    # ================ 内置命令实现 ================

    def cmd_help(self, args: Optional[str]) -> str:
        """显示帮助信息"""
        help_text = """
🆘 Polo AI Assistant 帮助信息

📝 聊天模式:
  直接输入消息即可与AI对话
  例：你好，今天天气怎么样？

🛠️ 工具命令 (以 ! 开头):
  !shell <命令>    - 执行系统命令
  !read <文件>     - 读取文件内容
  !write <文件> <内容> - 写入文件
  !ls [路径]       - 列出目录内容
  !find <模式>     - 查找文件
  !copy <源> <目标> - 复制文件
  !move <源> <目标> - 移动文件
  !delete <文件>   - 删除文件
  !info           - 显示系统信息

⚙️ 内置命令 (以 / 开头):
  /help           - 显示此帮助信息
  /exit, /quit    - 退出程序
  /clear          - 清空屏幕
  /history        - 显示命令历史
  /memory         - 显示记忆统计
  /stats          - 显示会话统计
  /tools          - 显示工具历史
  /about          - 关于信息

💡 提示:
  - 按 Tab 键自动补全
  - 按 Ctrl+C 中断当前操作
  - 按 Ctrl+D 或输入 /exit 退出
  - 使用上下箭头键浏览历史命令
"""
        return help_text

    def cmd_exit(self, args: Optional[str]) -> str:
        """退出程序"""
        self.running = False

        if self.memory:
            stats = self.memory.get_conversation_stats()
            goodbye_msg = f"👋 再见！本次会话我们对话了 {self.command_count} 次，"
            goodbye_msg += f"总共保存了 {stats['total']} 条记忆。"
        else:
            goodbye_msg = f"👋 再见！本次会话共执行了 {self.command_count} 个命令。"

        return goodbye_msg

    def cmd_clear(self, args: Optional[str]) -> str:
        """清空屏幕"""
        os.system("clear" if os.name == "posix" else "cls")
        return None

    def cmd_history(self, args: Optional[str]) -> str:
        """显示命令历史"""
        try:
            history_length = readline.get_current_history_length()
            if history_length == 0:
                return "📜 命令历史为空"

            # 显示最近的10条命令
            recent_count = min(10, history_length)
            history_list = []

            for i in range(
                max(1, history_length - recent_count + 1), history_length + 1
            ):
                cmd = readline.get_history_item(i)
                if cmd:
                    history_list.append(f"{i:3d}. {cmd}")

            if history_list:
                return "📜 最近的命令历史:\n" + "\n".join(history_list)
            else:
                return "📜 无可显示的命令历史"

        except Exception:
            return "❌ 无法访问命令历史（readline不可用）"

    def cmd_memory(self, args: Optional[str]) -> str:
        """显示记忆统计"""
        if not self.memory:
            return "❌ 记忆功能已禁用"

        stats = self.memory.get_conversation_stats()
        recent = self.memory.get_recent_conversations(5)

        result = "🧠 记忆统计:\n"
        result += f"📊 总对话数: {stats['total']}\n"
        result += f"📅 首次对话: {stats.get('first_conversation', '无')[:19]}\n"
        result += f"🕒 最近对话: {stats.get('last_conversation', '无')[:19]}\n"
        result += f"📝 记忆文件: {self.memory_file}\n"
        result += f"💾 文件大小: {stats.get('memory_file_size', 0)} bytes\n"

        if recent:
            result += "\n📚 最近对话:\n"
            for i, conv in enumerate(recent, 1):
                time_str = conv["timestamp"][:16].replace("T", " ")
                user_preview = conv["user"][:40] + (
                    "..." if len(conv["user"]) > 40 else ""
                )
                result += f"{i}. [{time_str}] {user_preview}\n"

        return result

    def cmd_stats(self, args: Optional[str]) -> str:
        """显示会话统计"""
        stats = "📈 本次会话统计:\n"
        stats += f"💬 执行命令数: {self.command_count}\n"
        stats += f"🧠 记忆功能: {'启用' if self.memory else '禁用'}\n"
        stats += f"📁 当前目录: {os.getcwd()}\n"
        stats += f"🐍 Python版本: {sys.version.split()[0]}\n"

        if self.tools:
            tool_history = self.tools.get_tool_history()
            stats += f"🔧 工具使用次数: {len(tool_history)}\n"

        return stats

    def cmd_tools(self, args: Optional[str]) -> str:
        """显示工具历史"""
        if not self.tools:
            return "❌ 工具系统不可用"

        tool_history = self.tools.get_tool_history(10)
        if not tool_history:
            return "🔧 暂无工具使用历史"

        result = "🔧 最近的工具使用历史:\n"
        for i, usage in enumerate(tool_history, 1):
            time_str = usage["timestamp"][:16].replace("T", " ")
            tool_name = usage["tool"]
            params = usage.get("params", {})

            # 简化参数显示
            param_str = ""
            if params:
                key_params = {
                    k: v
                    for k, v in params.items()
                    if k in ["command", "filepath", "path"]
                }
                if key_params:
                    param_str = (
                        f" ({', '.join(f'{k}={v}' for k, v in key_params.items())})"
                    )

            result += f"{i:2d}. [{time_str}] {tool_name}{param_str}\n"

        return result

    def cmd_about(self, args: Optional[str]) -> str:
        """显示关于信息"""
        about_text = """
🤖 Polo AI Assistant - Mini Claude Code
📦 版本: v0.2.0
👨‍💻 基于原始polo CLI改造

✨ 特性:
• 🧠 记忆系统 - 记住对话历史
• 🛠️ 工具集成 - 文件操作、命令执行
• 💬 智能对话 - 上下文感知回复
• 🔄 REPL模式 - 交互式命令行

📁 文件结构:
• cli.py        - 主入口
• commands.py   - 命令实现
• memory.py     - 记忆系统
• tools.py      - 工具系统
• ai_agent.py   - AI代理
• repl.py       - REPL界面

💡 这是一个演示性的AI助手CLI实现，
   实际应用中可以集成真实的AI API。
"""
        return about_text


# ================ REPL工具函数 ================


def start_repl(use_memory: bool = True, memory_file: str = "polo_memory.json") -> int:
    """启动REPL的便捷函数"""
    repl = PoloREPL(use_memory=use_memory, memory_file=memory_file)
    return repl.run()


if __name__ == "__main__":
    # 直接运行REPL
    import sys

    sys.exit(start_repl())
