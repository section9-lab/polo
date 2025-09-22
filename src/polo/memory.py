#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
记忆系统模块
"""

import json
import os
import shutil
from datetime import datetime
from typing import Dict, List, Any, Optional


class Memory:
    """记忆系统 - 负责存储和检索对话历史"""
    
    def __init__(self, memory_file: str = "polo_memory.json"):
        self.memory_file = memory_file
        self.data = self.load_memory()
    
    def load_memory(self) -> Dict[str, Any]:
        """加载记忆数据"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 确保数据结构完整
                    if not isinstance(data, dict):
                        data = {}
                    if "conversations" not in data:
                        data["conversations"] = []
                    if "context" not in data:
                        data["context"] = {}
                    if "metadata" not in data:
                        data["metadata"] = {
                            "created_at": datetime.now().isoformat(),
                            "version": "1.0"
                        }
                    return data
            except (json.JSONDecodeError, Exception) as e:
                print(f"⚠️  记忆文件损坏，将创建新的记忆: {e}")
                return self._create_empty_memory()
        
        return self._create_empty_memory()
    
    def _create_empty_memory(self) -> Dict[str, Any]:
        """创建空的记忆结构"""
        return {
            "conversations": [],
            "context": {},
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "version": "1.0"
            }
        }
    
    def save_memory(self) -> bool:
        """保存记忆到文件"""
        try:
            # 创建备份
            if os.path.exists(self.memory_file):
                backup_file = f"{self.memory_file}.backup"
                shutil.copy2(self.memory_file, backup_file)
            
            # 保存数据
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"❌ 保存记忆失败: {e}")
            return False
    
    def add_conversation(self, user_input: str, assistant_output: str, metadata: Optional[Dict] = None) -> bool:
        """添加对话记录"""
        try:
            conversation = {
                "id": len(self.data["conversations"]) + 1,
                "timestamp": datetime.now().isoformat(),
                "user": user_input,
                "assistant": assistant_output,
                "metadata": metadata or {}
            }
            
            self.data["conversations"].append(conversation)
            
            # 限制记忆大小，只保留最近的记录
            max_conversations = 1000
            if len(self.data["conversations"]) > max_conversations:
                # 保留最近的记录
                self.data["conversations"] = self.data["conversations"][-max_conversations:]
                # 重新分配ID
                for i, conv in enumerate(self.data["conversations"], 1):
                    conv["id"] = i
            
            return self.save_memory()
        except Exception as e:
            print(f"❌ 添加对话记录失败: {e}")
            return False
    
    def get_recent_conversations(self, n: int = 10) -> List[Dict]:
        """获取最近的N条对话"""
        conversations = self.data.get("conversations", [])
        return conversations[-n:] if conversations else []
    
    def get_context_string(self, n: int = 5) -> str:
        """获取上下文字符串，用于AI对话"""
        recent = self.get_recent_conversations(n)
        if not recent:
            return ""
        
        context_parts = []
        for conv in recent:
            context_parts.append(f"用户: {conv['user']}")
            context_parts.append(f"助手: {conv['assistant']}")
        
        return "\n".join(context_parts)
    
    def search_conversations(self, keyword: str, limit: int = 10) -> List[Dict]:
        """搜索包含关键词的对话"""
        conversations = self.data.get("conversations", [])
        results = []
        
        keyword_lower = keyword.lower()
        for conv in reversed(conversations):  # 从最新开始搜索
            if (keyword_lower in conv['user'].lower() or 
                keyword_lower in conv['assistant'].lower()):
                results.append(conv)
                if len(results) >= limit:
                    break
        
        return results
    
    def get_conversation_stats(self) -> Dict[str, Any]:
        """获取对话统计信息"""
        conversations = self.data.get("conversations", [])
        if not conversations:
            return {"total": 0}
        
        total = len(conversations)
        first_conv = conversations[0] if conversations else None
        last_conv = conversations[-1] if conversations else None
        
        # 计算用户消息和助手消息的平均长度
        user_lengths = [len(conv['user']) for conv in conversations]
        assistant_lengths = [len(conv['assistant']) for conv in conversations]
        
        return {
            "total": total,
            "first_conversation": first_conv['timestamp'] if first_conv else None,
            "last_conversation": last_conv['timestamp'] if last_conv else None,
            "avg_user_message_length": sum(user_lengths) / len(user_lengths) if user_lengths else 0,
            "avg_assistant_message_length": sum(assistant_lengths) / len(assistant_lengths) if assistant_lengths else 0,
            "memory_file_size": os.path.getsize(self.memory_file) if os.path.exists(self.memory_file) else 0
        }
    
    def clear_memory(self) -> bool:
        """清空所有记忆"""
        try:
            self.data = self._create_empty_memory()
            return self.save_memory()
        except Exception as e:
            print(f"❌ 清空记忆失败: {e}")
            return False
    
    def export_memory(self, export_file: str) -> bool:
        """导出记忆到指定文件"""
        try:
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"❌ 导出记忆失败: {e}")
            return False
    
    def import_memory(self, import_file: str) -> bool:
        """从文件导入记忆"""
        try:
            with open(import_file, 'r', encoding='utf-8') as f:
                imported_data = json.load(f)
            
            # 验证数据结构
            if not isinstance(imported_data, dict) or "conversations" not in imported_data:
                print("❌ 导入文件格式不正确")
                return False
            
            # 合并数据
            existing_conversations = self.data.get("conversations", [])
            imported_conversations = imported_data.get("conversations", [])
            
            # 简单去重（基于timestamp和内容）
            seen = set()
            combined = []
            
            for conv in existing_conversations + imported_conversations:
                key = (conv.get('timestamp', ''), conv.get('user', ''), conv.get('assistant', ''))
                if key not in seen:
                    seen.add(key)
                    combined.append(conv)
            
            # 按时间排序
            combined.sort(key=lambda x: x.get('timestamp', ''))
            
            # 重新分配ID
            for i, conv in enumerate(combined, 1):
                conv['id'] = i
            
            self.data["conversations"] = combined
            return self.save_memory()
            
        except Exception as e:
            print(f"❌ 导入记忆失败: {e}")
            return False
    
    def set_context_value(self, key: str, value: Any) -> bool:
        """设置上下文值"""
        try:
            self.data["context"][key] = value
            return self.save_memory()
        except Exception as e:
            print(f"❌ 设置上下文失败: {e}")
            return False
    
    def get_context_value(self, key: str, default: Any = None) -> Any:
        """获取上下文值"""
        return self.data["context"].get(key, default)
    
    def remove_context_value(self, key: str) -> bool:
        """删除上下文值"""
        try:
            if key in self.data["context"]:
                del self.data["context"][key]
                return self.save_memory()
            return True
        except Exception as e:
            print(f"❌ 删除上下文失败: {e}")
            return False