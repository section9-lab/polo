#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI代理模块
"""

import re
import os
import random
from datetime import datetime
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod

# 多个LLM库的导入尝试
try:
    import openai
except ImportError:
    openai = None

try:
    import anthropic
except ImportError:
    anthropic = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None

try:
    import jieba
    import jieba.analyse
except ImportError:
    jieba = None
from polo.memory import Memory
from polo.tools import Tools


# --- 基础类，用于LLM抽象 ---


class LLMBase(ABC):
    """Abstract Base Class for Large Language Models."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.client = self._setup_client()

    @abstractmethod
    def _setup_client(self) -> Any:
        """Sets up the specific API client."""
        pass

    @abstractmethod
    def chat(self, user_input: str, context: str) -> str:
        """Generates a response from the language model."""
        pass

    def get_system_prompt(self) -> str:
        """Provides a consistent system prompt for the AI."""
        return """You are Polo, an AI assistant integrated into a command-line interface (CLI).
- You are helpful, concise, and efficient.
- You have access to a set of tools for file system operations and shell command execution.
- When a user asks you to perform a task that requires a tool, respond by stating the tool you would use in a clear format. For example: "I will use the shell tool to list the files: `!shell ls -l`"
- For general conversation, provide direct and helpful answers.
"""


# --- LLM Implementations ---


class OpenAI_LLM(LLMBase):
    """LLM implementation for OpenAI models."""
            
    def _setup_client(self) -> Any:
        if not openai:
            raise ImportError(
                "OpenAI library not found. Please run 'pip install openai'."
            )
        api_key = self.api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OpenAI API key not provided or set in OPENAI_API_KEY environment variable."
            )
        return openai.OpenAI(api_key=api_key)

    def chat(self, user_input: str, context: str) -> str:
        try:
            messages = [{"role": "system", "content": self.get_system_prompt()}]
            if context:
                messages.append(
                    {
                        "role": "system",
                        "content": f"Previous conversation context:\n{context}",
                    }
                )
            messages.append({"role": "user", "content": user_input})

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo", messages=messages
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"❌ OpenAI API Error: {e}"


class Claude_LLM(LLMBase):
    """LLM implementation for Anthropic's Claude."""
            
    def _setup_client(self) -> Any:
        if not anthropic:
            raise ImportError(
                "Anthropic library not found. Please run 'pip install anthropic'."
            )
        api_key = self.api_key or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "Anthropic API key not provided or set in ANTHROPIC_API_KEY environment variable."
            )
        return anthropic.Anthropic(api_key=api_key)

    def chat(self, user_input: str, context: str) -> str:
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=self.get_system_prompt(),
                messages=[{"role": "user", "content": f"{context}\n\n{user_input}"}],
            )
            return response.content[0].text.strip()
        except Exception as e:
            return f"❌ Anthropic API Error: {e}"


class Gemini_LLM(LLMBase):
    """LLM implementation for Google's Gemini."""

    def _setup_client(self) -> Any:
        if not genai:
            raise ImportError(
                "Google GenerativeAI library not found. Please run 'pip install google-generativeai'."
            )
        api_key = self.api_key or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError(
                "Google API key not provided or set in GOOGLE_API_KEY environment variable."
            )
        genai.configure(api_key=api_key)
        return genai.GenerativeModel("gemini-2.5-flash")

    def chat(self, user_input: str, context: str) -> str:
        try:
            prompt = f"{self.get_system_prompt()}\n\nPrevious context:\n{context}\n\nUser query: {user_input}"
            response = self.client.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"❌ Gemini API Error: {e}"


class AIAgent:
    """AI代理 - 负责处理用户对话和工具调用"""

    # 1. 先定义“模型名 -> provider”映射
    MODEL2PROVIDER = {
        # OpenAI
        "gpt-3.5-turbo": "openai",
        "gpt-4": "openai",
        "gpt-4o": "openai",
        # Anthropic
        "claude-2.1": "claude",
        "claude-3-sonnet": "claude",
        "claude-3.5-sonnet": "claude",
        # Google
        "gemini-pro": "gemini",
        "gemini-1.5-flash": "gemini",
        "gemini-2.0-flash": "gemini",
        "gemini-2.5-flash": "gemini",
        "gemini-2.5-pro": "gemini",
    }
    LLM_PROVIDERS = {
        "openai": OpenAI_LLM,
        "claude": Claude_LLM,
        "gemini": Gemini_LLM,
    }

    def __init__(
        self,
        memory: Optional[Memory] = None,
        tools: Optional[Tools] = None,
        model_name: str = None,
        api_key: Optional[str] = None,
    ):
        self.memory = memory
        self.tools = tools or Tools()
        self.conversation_count = 0

        # Instantiate the selected LLM provider
        # model_class = self.LLM_PROVIDERS.get(model_name.lower())
        # if not model_class:
        #     raise ValueError(
        #         f"Unknown model provider: {model_name}. Available: {list(self.LLM_PROVIDERS.keys())}. model_class:"
        #     )

        # 2. 根据模型名拿到 provider 字符串
        provider = self.MODEL2PROVIDER.get(model_name.lower())
        if provider is None:
            # 用户只给了 provider 名，没给具体模型
            if model_name.lower() in self.LLM_PROVIDERS:
                provider = model_name.lower()
                model_name = None  # 后面用默认模型
            else:
                raise ValueError(
                    f"Unknown model '{model_name}'. "
                    f"Available models: {list(self.MODEL2PROVIDER.keys())} | "
                    f"Available providers: {list(self.LLM_PROVIDERS.keys())}"
                )

        # 3. 实例化 LLM
        model_class = self.LLM_PROVIDERS[provider]
        try:
            print(model_class)
            self.llm_client = model_class()
        except (ImportError, ValueError) as e:
            print(f"⚠️  Warning: Failed to initialize model '{model_name}': {e}")

    def chat(self, user_input: str) -> str:
        """处理用户对话"""
        self.conversation_count += 1

        # Check for direct tool invocations (e.g. `!ls`) which are handled by repl.py
        # This agent's role is to interpret natural language requests for tools
        tool_result = self._check_tool_commands(user_input)
        if tool_result:
            return tool_result

        # Generate AI response using the selected LLM
        response = self._generate_response(user_input)

        # Save to memory
        if self.memory:
            self.memory.add_conversation(user_input, response)

        return response

    def _generate_response(self, user_input: str) -> str:
        """Generates a response using the configured LLM client."""
        context = ""
        if self.memory:
            # Provide the last 3 exchanges as context
            context = self.memory.get_context_string(3)

        return self.llm_client.chat(user_input, context)

    def _check_tool_commands(self, user_input: str) -> Optional[str]:
        """(Optional) Kept for direct natural language tool invocation if desired."""
        # This logic can be expanded or used by an LLM that is trained for function calling.
        # For this implementation, we assume the LLM will suggest commands and the user will execute them.
        return None

    def analyze_user_intent(self, user_input: str) -> Dict[str, Any]:
        """Analyzes user intent (simple version)."""
        intent_data = {"input": user_input, "length": len(user_input)}

        if jieba:
            try:
                intent_data["keywords"] = jieba.analyse.extract_tags(user_input, topK=5)
            except Exception:
                intent_data["keywords"] = user_input.split()[:5]
        else:
            intent_data["keywords"] = user_input.split()[:5]
        return intent_data
