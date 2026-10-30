#!/usr/bin/env python3
"""
Simple AI Agent — локальный агент с инструментами для работы с файлами и командами.
"""

import os
import json
import subprocess
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# === Настройки ===
API_KEY = os.getenv("OPENAI_API_KEY", "")
BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
MODEL = os.getenv("MODEL", "gpt-4o-mini")

if not API_KEY:
    print("Ошибка: не указан OPENAI_API_KEY в .env")
    print("Скопируй .env.example в .env и укажи ключ.")
    exit(1)

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

# Рабочая директория (можно менять)
WORK_DIR = Path.cwd()


# === Инструменты ===

def list_dir(path: str = ".") -> str:
    """Список файлов и папок в указанной директории."""
    try:
        p = (WORK_DIR / path).resolve()
        if not str(p).startswith(str(WORK_DIR.resolve())):
            return "Ошибка: выход за пределы рабочей директории запрещён"
        if not p.exists():
            return f"Путь не существует: {path}"
        items = []
        for item in sorted(p.iterdir()):
            kind = "dir" if item.is_dir() else "file"
            size = item.stat().st_size if item.is_file() else "-"
            items.append(f"{kind:4} {size:>10}  {item.name}")
        return "\n".join(items) if items else "(пусто)"
    except Exception as e:
        return f"Ошибка: {e}"


def read_file(path: str) -> str:
    """Прочитать содержимое текстового файла."""
    try:
        p = (WORK_DIR / path).resolve()
        if not str(p).startswith(str(WORK_DIR.resolve())):
            return "Ошибка: выход за пределы рабочей директории запрещён"
        if not p.is_file():
            return f"Файл не найден: {path}"
        content = p.read_text(encoding="utf-8", errors="replace")
        if len(content) > 30000:
            return content[:30000] + "\n\n... (файл обрезан, слишком большой)"
        return content
    except Exception as e:
        return f"Ошибка: {e}"


def write_file(path: str, content: str) -> str:
    """Создать или перезаписать файл."""
    try:
        p = (WORK_DIR / path).resolve()
        if not str(p).startswith(str(WORK_DIR.resolve())):
            return "Ошибка: выход за пределы рабочей директории запрещён"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return f"Файл записан: {path} ({len(content)} символов)"
    except Exception as e:
        return f"Ошибка: {e}"


def append_file(path: str, content: str) -> str:
    """Добавить текст в конец файла."""
    try:
        p = (WORK_DIR / path).resolve()
        if not str(p).startswith(str(WORK_DIR.resolve())):
            return "Ошибка: выход за пределы рабочей директории запрещён"
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("a", encoding="utf-8") as f:
            f.write(content)
        return f"Добавлено в файл: {path}"
    except Exception as e:
        return f"Ошибка: {e}"


def create_dir(path: str) -> str:
    """Создать папку (и родительские, если нужно)."""
    try:
        p = (WORK_DIR / path).resolve()
        if not str(p).startswith(str(WORK_DIR.resolve())):
            return "Ошибка: выход за пределы рабочей директории запрещён"
        p.mkdir(parents=True, exist_ok=True)
        return f"Папка создана: {path}"
    except Exception as e:
        return f"Ошибка: {e}"


def run_command(command: str) -> str:
    """Выполнить shell-команду в рабочей директории."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=str(WORK_DIR),
            capture_output=True,
            text=True,
            timeout=60,
        )
        output = ""
        if result.stdout:
            output += result.stdout
        if result.stderr:
            output += ("\n[stderr]\n" + result.stderr) if output else result.stderr
        if result.returncode != 0:
            output += f"\n[код выхода: {result.returncode}]"
        return output.strip() or "(команда выполнена, вывода нет)"
    except subprocess.TimeoutExpired:
        return "Ошибка: команда превысила лимит времени (60 сек)"
    except Exception as e:
        return f"Ошибка: {e}"


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_dir",
            "description": "Показать список файлов и папок в указанной директории (относительно рабочей папки)",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Путь к папке (по умолчанию текущая)",
                        "default": ".",
                    }
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Прочитать содержимое текстового файла",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Путь к файлу"}
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Создать новый файл или полностью перезаписать существующий",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Путь к файлу"},
                    "content": {"type": "string", "description": "Содержимое файла"},
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "append_file",
            "description": "Добавить текст в конец существующего файла (или создать новый)",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Путь к файлу"},
                    "content": {"type": "string", "description": "Текст для добавления"},
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_dir",
            "description": "Создать папку",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Путь к папке"}
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": "Выполнить shell-команду (ls, cat, python, git и т.д.). Используй осторожно.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "Команда для выполнения"}
                },
                "required": ["command"],
            },
        },
    },
]

TOOL_MAP = {
    "list_dir": list_dir,
    "read_file": read_file,
    "write_file": write_file,
    "append_file": append_file,
    "create_dir": create_dir,
    "run_command": run_command,
}


def call_tool(name: str, arguments: dict) -> str:
    fn = TOOL_MAP.get(name)
    if not fn:
        return f"Неизвестный инструмент: {name}"
    try:
        return fn(**arguments)
    except TypeError as e:
        return f"Ошибка аргументов: {e}"


SYSTEM_PROMPT = """Ты полезный AI-агент, работающий на компьютере пользователя.
У тебя есть инструменты для работы с файловой системой и выполнения команд.

Правила:
- Всегда используй инструменты, когда нужно создать/прочитать/изменить файлы или выполнить команды.
- Рабочая директория уже задана. Не пытайся выходить за её пределы.
- Отвечай на языке пользователя (русский или английский).
- Будь кратким и конкретным.
- Если задача сложная — разбивай на шаги и используй инструменты по очереди.
- После выполнения действий кратко расскажи, что сделал.
"""


def chat_loop():
    print("=" * 50)
    print("  Simple AI Agent  |  Ctrl+C для выхода")
    print(f"  Модель: {MODEL}")
    print(f"  Папка:  {WORK_DIR}")
    print("=" * 50)
    print()

    messages: list[dict[str, Any]] = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

    while True:
        try:
            user_input = input("Ты > ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nПока!")
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit", "выход"):
            print("Пока!")
            break

        messages.append({"role": "user", "content": user_input})

        # Цикл tool-calling
        while True:
            try:
                response = client.chat.completions.create(
                    model=MODEL,
                    messages=messages,
                    tools=TOOLS,
                    tool_choice="auto",
                )
            except Exception as e:
                print(f"\n[Ошибка API]: {e}\n")
                messages.pop()  # убрать последний user, чтобы не зациклиться
                break

            msg = response.choices[0].message

            # Если модель вызвала инструменты
            if msg.tool_calls:
                messages.append(msg)  # добавляем ответ ассистента с tool_calls

                for tool_call in msg.tool_calls:
                    name = tool_call.function.name
                    try:
                        args = json.loads(tool_call.function.arguments)
                    except json.JSONDecodeError:
                        args = {}

                    print(f"  → {name}({args})")
                    result = call_tool(name, args)
                    # обрезаем очень длинный вывод
                    display = result if len(result) < 500 else result[:500] + "..."
                    print(f"    {display}\n")

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result,
                    })
                continue  # снова спрашиваем модель с результатами инструментов

            # Обычный текстовый ответ
            content = msg.content or ""
            print(f"\nАгент > {content}\n")
            messages.append({"role": "assistant", "content": content})
            break


if __name__ == "__main__":
    chat_loop()
