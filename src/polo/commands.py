#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
命令实现模块
"""

import argparse
import sys
from polo.memory import Memory
from polo.tools import Tools
from polo.ai_agent import AIAgent


# ---------------- AI相关命令 ----------------
def cmd_ask(args: argparse.Namespace) -> int:
    """单次AI对话"""
    message = " ".join(args.message)
    
    # 初始化组件
    memory = Memory() if args.context else None
    agent = AIAgent(memory=memory)
    
    try:
        response = agent.chat(message)
        print(f"🤖 助手: {response}")
        return 0
    except Exception as e:
        print(f"❌ 对话出错: {e}")
        return 1


def cmd_shell(args: argparse.Namespace) -> int:
    """执行系统命令"""
    command = " ".join(args.command)
    
    try:
        tools = Tools()
        result = tools.execute_shell(command, timeout=args.timeout)
        print(result)
        return 0
    except Exception as e:
        print(f"❌ 执行命令出错: {e}")
        return 1


def cmd_file(args: argparse.Namespace) -> int:
    """文件操作命令"""
    tools = Tools()
    
    try:
        if args.file_action == "read":
            result = tools.read_file(args.path, max_lines=args.lines)
            print(result)
            
        elif args.file_action == "write":
            content = " ".join(args.content) if args.content else ""
            if not content:
                # 从stdin读取
                print("请输入内容，按Ctrl+D结束:")
                content = sys.stdin.read()
            
            result = tools.write_file(args.path, content, append=args.append)
            print(result)
            
        elif args.file_action == "list":
            result = tools.list_directory(args.path, show_hidden=args.all)
            print(result)
            
        return 0
    except Exception as e:
        print(f"❌ 文件操作出错: {e}")
        return 1


def cmd_memory(args: argparse.Namespace) -> int:
    """记忆管理命令"""
    memory = Memory()
    
    try:
        if args.memory_action == "show":
            conversations = memory.get_recent_conversations(args.recent)
            if not conversations:
                print("暂无记忆记录")
                return 0
            
            print(f"📚 最近 {len(conversations)} 条记忆:")
            print("-" * 50)
            for i, conv in enumerate(conversations, 1):
                time_str = conv['timestamp'][:19].replace('T', ' ')
                print(f"{i}. [{time_str}]")
                print(f"   用户: {conv['user'][:100]}{'...' if len(conv['user']) > 100 else ''}")
                print(f"   助手: {conv['assistant'][:100]}{'...' if len(conv['assistant']) > 100 else ''}")
                print()
                
        elif args.memory_action == "clear":
            if not args.confirm:
                confirm = input("⚠️  确定要清空所有记忆吗？(y/N): ").strip().lower()
                if confirm not in ['y', 'yes']:
                    print("操作已取消")
                    return 0
            
            memory.clear_memory()
            print("✅ 记忆已清空")
            
        elif args.memory_action == "export":
            memory.export_memory(args.file)
            print(f"✅ 记忆已导出到: {args.file}")
            
        return 0
    except Exception as e:
        print(f"❌ 记忆操作出错: {e}")
        return 1


def cmd_chat(args: argparse.Namespace) -> int:
    """启动交互式REPL模式"""
    from polo.repl import PoloREPL
    
    try:
        # 初始化REPL
        repl = PoloREPL(
            use_memory=not args.no_memory,
            memory_file=args.memory_file
        )
        
        # 启动REPL
        return repl.run()
        
    except Exception as e:
        print(f"❌ REPL模式启动失败: {e}")
        return 1