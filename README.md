# 🤖 Polo AI Assistant - Mini Claude Code

基于原始polo CLI改造的AI助手命令行工具，实现了REPL、Tools和Memory三大核心功能。

## ✨ 特性

- 🧠 **记忆系统** - 自动保存对话历史，支持上下文感知
- 🛠️ **工具集成** - 文件操作、命令执行、系统信息等
- 💬 **智能对话** - 模拟AI对话，支持意图识别
- 🔄 **REPL模式** - 交互式命令行界面
- 📁 **模块化设计** - 清晰的代码结构，易于扩展

## 🚀 快速开始

### 安装依赖

```bash
# 基础功能无需外部依赖
# 可选安装增强功能依赖
pip install -r requirements.txt
```

### 运行方式

```bash
# 1. 直接启动REPL模式
python cli.py

# 2. 或者显式启动REPL
python cli.py repl

# 3. 单次命令模式
python cli.py chat "你好，今天天气怎么样？"
python cli.py shell "ls -la"
python cli.py file read example.txt

# 4. 查看帮助
python cli.py --help
```

## 📚 使用指南

### REPL交互模式

启动后进入交互式模式，支持三种输入：

#### 💬 聊天模式
直接输入消息与AI对话：
```
👤 [polo] (1): 你好！
🤖 你好！我是polo AI助手，有什么可以帮助你的吗？

👤 [polo] (2): 现在几点了？
🤖 当前时间是: 2025-01-15 14:30:25
```

#### 🛠️ 工具命令 (以`!`开头)
```
👤 [polo] (3): !ls
📁 目录: .
📊 统计: 2 个目录, 8 个文件
--------------------------------------------------
📁 __pycache__
📄 ai_agent.py
📄 cli.py
📄 commands.py
📄 memory.py
📄 polo_memory.json
📄 README.md
📄 repl.py
📄 requirements.txt
📄 tools.py

👤 [polo] (4): !read README.md
📁 文件: README.md
📊 大小: 3247 bytes
📄 内容:
----------------------------------------
# 🤖 Polo AI Assistant - Mini Claude Code
...

👤 [polo] (5): !shell echo "Hello World"
🔧 执行: echo "Hello World"
📤 输出:
Hello World

✅ 执行成功
⏱️  耗时: 0.02秒
```

#### ⚙️ 内置命令 (以`/`开头)
```
👤 [polo] (6): /help
🆘 Polo AI Assistant 帮助信息
...

👤 [polo] (7): /memory
🧠 记忆统计:
📊 总对话数: 15
📅 首次对话: 2025-01-15 14:25
🕒 最近对话: 2025-01-15 14:35
...

👤 [polo] (8): /exit
👋 再见！本次会话我们对话了 8 次，总共保存了 15 条记忆。
```

### 命令行模式

#### 聊天命令
```bash
# 单次对话
python cli.py chat "解释一下Python装饰器"

# 带上下文的对话
python cli.py chat --context "继续之前的话题"
```

#### 工具命令
```bash
# 执行系统命令
python cli.py shell "ps aux | grep python"

# 文件操作
python cli.py file read config.json
python cli.py file write test.txt "Hello World"
python cli.py file list /usr/local

# 记忆管理
python cli.py memory show --recent 10
python cli.py memory export backup.json
python cli.py memory clear --confirm
```

## 🏗️ 架构设计

```
cli.py          # 主入口，参数解析
├── commands.py # 命令实现层
├── repl.py     # REPL交互界面
├── ai_agent.py # AI对话代理
├── memory.py   # 记忆存储系统
└── tools.py    # 工具执行系统
```

### 核心组件

- **CLI层** (`cli.py`): 命令行参数解析和路由
- **命令层** (`commands.py`): 各种子命令的具体实现
- **REPL层** (`repl.py`): 交互式界面和命令解析
- **AI代理** (`ai_agent.py`): 对话处理和意图识别
- **记忆系统** (`memory.py`): 对话历史存储和检索
- **工具系统** (`tools.py`): 文件操作和系统命令执行

## 🔧 功能详解

### 记忆系统
- JSON格式存储对话历史
- 支持上下文检索和统计分析
- 自动备份和数据完整性检查
- 可导出导入记忆数据

### 工具系统
- 安全的命令执行（超时保护）
- 文件系统操作（读写、复制、移动等）
- 系统信息获取
- 工具使用历史记录

### AI代理
- 基于关键词的意图识别
- 上下文感知回复生成
- 工具调用检测和执行
- 对话摘要和统计

## 🔄 扩展指南

### 接入真实AI API

修改 `ai_agent.py` 中的 `_generate_response` 方法：

```python
def _generate_response(self, user_input: str) -> str:
    # 替换为真实AI API调用
    import openai
    
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "你是一个有用的AI助手"},
            {"role": "user", "content": user_input}
        ]
    )
    
    return response.choices[0].message.content
```

### 添加新工具

在 `tools.py` 的 `Tools` 类中添加新方法：

```python
def your_new_tool(self, param1: str, param2: int = 10) -> str:
    """你的新工具描述"""
    try:
        self._log_tool_usage("your_new_tool", {"param1": param1, "param2": param2})
        
        # 工具逻辑实现
        result = "工具执行结果"
        
        return f"✅ {result}"
    except Exception as e:
        return f"❌ 工具执行错误: {str(e)}"
```

然后在 `repl.py` 中添加命令映射。

### 自定义记忆后端

继承 `Memory` 类实现不同的存储后端：

```python
class DatabaseMemory(Memory):
    def load_memory(self):
        # 从数据库加载
        pass
    
    def save_memory(self):
        # 保存到数据库
        pass
```

## 📝 开发说明

### 运行测试
```bash
# 如果安装了pytest
pytest tests/

# 或者直接运行测试文件
python -m unittest discover tests/
```

### 代码格式化
```bash
black *.py
flake8 *.py
```

## 🐛 已知问题

1. **中文分词**: 如果未安装jieba，关键词提取将使用简单的空格分割
2. **系统信息**: 如果未安装psutil，系统信息功能会受限
3. **Readline**: 在某些环境下readline可能不可用，会影响命令历史功能

## 🤝 贡献指南

1. Fork本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交Pull Request

## 📄 许可证

本项目基于MIT许可证开源。

## 🙏 致谢

- 灵感来源于Claude Code和各种AI助手工具

---

**Happy Coding! 🚀**


