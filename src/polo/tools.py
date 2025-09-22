#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具系统模块
"""

import os
import subprocess
import shutil
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path


class Tools:
    """工具系统 - 提供各种实用工具功能"""
    
    def __init__(self):
        self.tool_history = []
    
    def execute_shell(self, command: str, timeout: int = 30, cwd: Optional[str] = None) -> str:
        """执行shell命令"""
        try:
            start_time = time.time()
            
            # 记录工具使用
            self._log_tool_usage("shell", {"command": command, "cwd": cwd})
            
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=cwd
            )
            
            execution_time = time.time() - start_time
            
            output = []
            if result.stdout:
                output.append(f"📤 输出:\n{result.stdout}")
            
            if result.stderr:
                output.append(f"⚠️  错误:\n{result.stderr}")
            
            if result.returncode != 0:
                output.append(f"❌ 返回码: {result.returncode}")
            else:
                output.append(f"✅ 执行成功")
            
            output.append(f"⏱️  耗时: {execution_time:.2f}秒")
            
            return "\n\n".join(output)
            
        except subprocess.TimeoutExpired:
            return f"⏰ 命令执行超时 ({timeout}秒)"
        except Exception as e:
            return f"❌ 执行错误: {str(e)}"
    
    def read_file(self, filepath: str, max_lines: Optional[int] = None, encoding: str = 'utf-8') -> str:
        """读取文件内容"""
        try:
            self._log_tool_usage("read_file", {"filepath": filepath, "max_lines": max_lines})
            
            path = Path(filepath)
            if not path.exists():
                return f"❌ 文件不存在: {filepath}"
            
            if not path.is_file():
                return f"❌ 不是文件: {filepath}"
            
            file_size = path.stat().st_size
            
            with open(path, 'r', encoding=encoding) as f:
                if max_lines:
                    lines = []
                    for i, line in enumerate(f, 1):
                        if i > max_lines:
                            lines.append(f"... (文件还有更多内容，使用 --lines 参数查看更多)")
                            break
                        lines.append(line.rstrip())
                    content = "\n".join(lines)
                else:
                    content = f.read()
                    # 限制输出长度
                    if len(content) > 5000:
                        content = content[:5000] + "\n... (文件太长，已截断到5000字符)"
            
            return f"📁 文件: {filepath}\n📊 大小: {file_size} bytes\n📄 内容:\n{'-'*40}\n{content}"
            
        except UnicodeDecodeError:
            return f"❌ 文件编码错误，请尝试其他编码: {filepath}"
        except PermissionError:
            return f"❌ 权限不足，无法读取文件: {filepath}"
        except Exception as e:
            return f"❌ 读取文件错误: {str(e)}"
    
    def write_file(self, filepath: str, content: str, append: bool = False, encoding: str = 'utf-8') -> str:
        """写入文件"""
        try:
            self._log_tool_usage("write_file", {
                "filepath": filepath, 
                "content_length": len(content),
                "append": append
            })
            
            path = Path(filepath)
            
            # 确保目录存在
            path.parent.mkdir(parents=True, exist_ok=True)
            
            mode = 'a' if append else 'w'
            
            with open(path, mode, encoding=encoding) as f:
                f.write(content)
            
            file_size = path.stat().st_size
            action = "追加到" if append else "写入"
            
            return f"✅ 已{action}文件: {filepath}\n📊 文件大小: {file_size} bytes"
            
        except PermissionError:
            return f"❌ 权限不足，无法写入文件: {filepath}"
        except Exception as e:
            return f"❌ 写入文件错误: {str(e)}"
    
    def list_directory(self, path: str = ".", show_hidden: bool = False, detailed: bool = False) -> str:
        """列出目录内容"""
        try:
            self._log_tool_usage("list_directory", {"path": path, "show_hidden": show_hidden})
            
            dir_path = Path(path)
            if not dir_path.exists():
                return f"❌ 路径不存在: {path}"
            
            if not dir_path.is_dir():
                return f"❌ 不是目录: {path}"
            
            items = []
            total_size = 0
            dir_count = 0
            file_count = 0
            
            for item in sorted(dir_path.iterdir()):
                # 跳过隐藏文件（除非指定显示）
                if not show_hidden and item.name.startswith('.'):
                    continue
                
                try:
                    stat = item.stat()
                    size = stat.st_size
                    mtime = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
                    
                    if item.is_dir():
                        dir_count += 1
                        icon = "📁"
                        size_str = "<DIR>"
                    else:
                        file_count += 1
                        total_size += size
                        icon = "📄"
                        size_str = self._format_size(size)
                    
                    if detailed:
                        perm = oct(stat.st_mode)[-3:]
                        items.append(f"{icon} {item.name:30} {size_str:>10} {mtime} {perm}")
                    else:
                        items.append(f"{icon} {item.name}")
                        
                except (PermissionError, OSError):
                    items.append(f"❓ {item.name} (无权限访问)")
            
            if not items:
                content_list = "目录为空"
            else:
                content_list = "\n".join(items)
            
            summary = f"📊 统计: {dir_count} 个目录, {file_count} 个文件"
            if total_size > 0:
                summary += f", 总大小: {self._format_size(total_size)}"
            
            return f"📁 目录: {path}\n{summary}\n{'-'*50}\n{content_list}"
            
        except PermissionError:
            return f"❌ 权限不足，无法访问目录: {path}"
        except Exception as e:
            return f"❌ 列出目录错误: {str(e)}"
    
    def copy_file(self, src: str, dst: str) -> str:
        """复制文件"""
        try:
            self._log_tool_usage("copy_file", {"src": src, "dst": dst})
            
            src_path = Path(src)
            dst_path = Path(dst)
            
            if not src_path.exists():
                return f"❌ 源文件不存在: {src}"
            
            # 确保目标目录存在
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            
            if src_path.is_dir():
                shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
                return f"✅ 已复制目录: {src} -> {dst}"
            else:
                shutil.copy2(src_path, dst_path)
                size = dst_path.stat().st_size
                return f"✅ 已复制文件: {src} -> {dst}\n📊 文件大小: {self._format_size(size)}"
                
        except PermissionError:
            return f"❌ 权限不足，无法复制: {src} -> {dst}"
        except Exception as e:
            return f"❌ 复制错误: {str(e)}"
    
    def move_file(self, src: str, dst: str) -> str:
        """移动文件"""
        try:
            self._log_tool_usage("move_file", {"src": src, "dst": dst})
            
            src_path = Path(src)
            dst_path = Path(dst)
            
            if not src_path.exists():
                return f"❌ 源文件不存在: {src}"
            
            # 确保目标目录存在
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.move(str(src_path), str(dst_path))
            return f"✅ 已移动: {src} -> {dst}"
            
        except PermissionError:
            return f"❌ 权限不足，无法移动: {src} -> {dst}"
        except Exception as e:
            return f"❌ 移动错误: {str(e)}"
    
    def delete_file(self, filepath: str, force: bool = False) -> str:
        """删除文件或目录"""
        try:
            self._log_tool_usage("delete_file", {"filepath": filepath, "force": force})
            
            path = Path(filepath)
            if not path.exists():
                return f"❌ 文件不存在: {filepath}"
            
            if path.is_dir():
                if force:
                    shutil.rmtree(path)
                    return f"✅ 已删除目录: {filepath}"
                else:
                    return f"❌ 是目录，请使用 --force 参数强制删除: {filepath}"
            else:
                path.unlink()
                return f"✅ 已删除文件: {filepath}"
                
        except PermissionError:
            return f"❌ 权限不足，无法删除: {filepath}"
        except Exception as e:
            return f"❌ 删除错误: {str(e)}"
    
    def find_files(self, pattern: str, path: str = ".", max_results: int = 50) -> str:
        """查找文件"""
        try:
            self._log_tool_usage("find_files", {"pattern": pattern, "path": path})
            
            from pathlib import Path
            import fnmatch
            
            search_path = Path(path)
            if not search_path.exists():
                return f"❌ 搜索路径不存在: {path}"
            
            results = []
            count = 0
            
            def search_recursive(current_path: Path):
                nonlocal count
                if count >= max_results:
                    return
                
                try:
                    for item in current_path.iterdir():
                        if count >= max_results:
                            break
                        
                        if item.name.startswith('.'):
                            continue
                        
                        if fnmatch.fnmatch(item.name, pattern):
                            results.append(str(item.relative_to(search_path)))
                            count += 1
                        
                        if item.is_dir():
                            search_recursive(item)
                            
                except (PermissionError, OSError):
                    pass
            
            search_recursive(search_path)
            
            if not results:
                return f"❌ 未找到匹配的文件: {pattern}"
            
            result_text = "\n".join(f"📄 {result}" for result in results)
            
            if count >= max_results:
                result_text += f"\n... (仅显示前 {max_results} 个结果)"
            
            return f"🔍 搜索结果 (模式: {pattern}):\n{result_text}\n\n📊 找到 {len(results)} 个文件"
            
        except Exception as e:
            return f"❌ 查找文件错误: {str(e)}"
    
    def get_system_info(self) -> str:
        """获取系统信息"""
        try:
            self._log_tool_usage("get_system_info", {})
            
            import platform
            import psutil
            
            info = []
            info.append(f"💻 系统: {platform.system()} {platform.release()}")
            info.append(f"🏗️  架构: {platform.machine()}")
            info.append(f"🐍 Python: {platform.python_version()}")
            info.append(f"👤 用户: {os.getenv('USER', os.getenv('USERNAME', '未知'))}")
            info.append(f"📁 当前目录: {os.getcwd()}")
            
            # 内存信息
            memory = psutil.virtual_memory()
            info.append(f"🧠 内存: {self._format_size(memory.used)}/{self._format_size(memory.total)} ({memory.percent:.1f}%)")
            
            # 磁盘信息
            disk = psutil.disk_usage('/')
            info.append(f"💾 磁盘: {self._format_size(disk.used)}/{self._format_size(disk.total)} ({disk.percent:.1f}%)")
            
            # CPU信息
            info.append(f"⚡ CPU: {psutil.cpu_count()} 核心, 使用率: {psutil.cpu_percent(interval=1):.1f}%")
            
            return "\n".join(info)
            
        except ImportError:
            return "❌ 需要安装 psutil 库来获取系统信息: pip install psutil"
        except Exception as e:
            return f"❌ 获取系统信息错误: {str(e)}"
    
    def _format_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        if size_bytes == 0:
            return "0 B"
        
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        unit_index = 0
        size = float(size_bytes)
        
        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1
        
        return f"{size:.1f} {units[unit_index]}"
    
    def _log_tool_usage(self, tool_name: str, params: Dict[str, Any]):
        """记录工具使用历史"""
        self.tool_history.append({
            "timestamp": datetime.now().isoformat(),
            "tool": tool_name,
            "params": params
        })
        
        # 只保留最近100条记录
        if len(self.tool_history) > 100:
            self.tool_history = self.tool_history[-100:]
    
    def get_tool_history(self, n: int = 10) -> List[Dict[str, Any]]:
        """获取工具使用历史"""
        return self.tool_history[-n:] if self.tool_history else []
    
    def clear_tool_history(self):
        """清空工具使用历史"""
        self.tool_history = []