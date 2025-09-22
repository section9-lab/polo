#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
polo CLI 工具 - Mini Claude Code
"""

import argparse
import sys
import logging
from polo.commands import cmd_ask, cmd_shell, cmd_file, cmd_memory, cmd_chat
from dotenv import load_dotenv
load_dotenv()

__version__ = "0.1.0"
PROJECT_NAME = "polo"

# ---------------- 日志配置 ----------------
logger = logging.getLogger(PROJECT_NAME)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
logger.addHandler(handler)
logger.setLevel(logging.INFO)


# ---------------- 参数解析 ----------------
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=PROJECT_NAME,
        description="Mini Claude Code - AI助手CLI工具，支持REPL、Tools和Memory"
    )

    # 全局参数
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="显示版本信息"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="启用调试模式"
    )

    # 子命令集合
    subparsers = parser.add_subparsers(
        title="子命令",
        dest="command",
        required=True
    )

    # 新增：ask 子命令 - 单次对话
    parser_ask = subparsers.add_parser("ask", help="单次AI对话")
    parser_ask.add_argument("message", nargs="+", help="要发送的消息")
    parser_ask.add_argument("--context", "-c", action="store_true", help="使用历史上下文")
    parser_ask.set_defaults(func=cmd_ask)

    # 新增：chat 子命令 - 交互式模式（主要功能）
    parser_chat = subparsers.add_parser("chat", help="启动交互式REPL模式")
    parser_chat.add_argument("--no-memory", action="store_true", help="禁用记忆功能")
    parser_chat.add_argument("--memory-file", default="polo_memory.json", help="记忆文件路径")
    parser_chat.set_defaults(func=cmd_chat)

    # 新增：shell 子命令 - 执行系统命令
    parser_shell = subparsers.add_parser("shell", help="执行系统命令")
    parser_shell.add_argument("command", nargs="+", help="要执行的命令")
    parser_shell.add_argument("--timeout", "-t", type=int, default=30, help="超时时间（秒）")
    parser_shell.set_defaults(func=cmd_shell)

    # 新增：file 子命令 - 文件操作
    parser_file = subparsers.add_parser("file", help="文件操作")
    file_subparsers = parser_file.add_subparsers(dest="file_action", required=True)
    
    # file read
    parser_file_read = file_subparsers.add_parser("read", help="读取文件")
    parser_file_read.add_argument("path", help="文件路径")
    parser_file_read.add_argument("--lines", "-n", type=int, help="限制显示行数")
    
    # file write
    parser_file_write = file_subparsers.add_parser("write", help="写入文件")
    parser_file_write.add_argument("path", help="文件路径")
    parser_file_write.add_argument("content", nargs="*", help="文件内容")
    parser_file_write.add_argument("--append", "-a", action="store_true", help="追加模式")
    
    # file list
    parser_file_list = file_subparsers.add_parser("list", help="列出目录")
    parser_file_list.add_argument("path", nargs="?", default=".", help="目录路径")
    parser_file_list.add_argument("--all", "-a", action="store_true", help="显示隐藏文件")
    
    parser_file.set_defaults(func=cmd_file)

    # 新增：memory 子命令 - 记忆管理
    parser_memory = subparsers.add_parser("memory", help="记忆管理")
    memory_subparsers = parser_memory.add_subparsers(dest="memory_action", required=True)
    
    # memory show
    parser_memory_show = memory_subparsers.add_parser("show", help="显示记忆")
    parser_memory_show.add_argument("--recent", "-r", type=int, default=10, help="显示最近N条记录")
    
    # memory clear
    parser_memory_clear = memory_subparsers.add_parser("clear", help="清空记忆")
    parser_memory_clear.add_argument("--confirm", action="store_true", help="确认清空")
    
    # memory export
    parser_memory_export = memory_subparsers.add_parser("export", help="导出记忆")
    parser_memory_export.add_argument("file", help="导出文件路径")
    
    parser_memory.set_defaults(func=cmd_memory)

    return parser


# ---------------- 主函数 ----------------
def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    parser = build_parser()

    # 如果用户没有输入参数，默认进入REPL模式
    if not argv:
        print(f"🤖 {PROJECT_NAME} v{__version__} - Mini Claude Code")
        print("启动交互式REPL模式...")
        print("使用 --help 查看所有命令\n")
        # 默认进入REPL模式
        from polo.commands import cmd_chat
        import argparse
        args = argparse.Namespace()
        args.no_memory = False
        args.memory_file = "polo_memory.json"
        return cmd_chat(args)
    
    args = parser.parse_args(argv)
    
    # 设置日志级别
    if hasattr(args, 'debug') and args.debug:
        logger.setLevel(logging.DEBUG)

    try:
        return args.func(args)
    except Exception as e:
        logger.error(f"执行命令出错: {e}")
        if hasattr(args, 'debug') and args.debug:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())