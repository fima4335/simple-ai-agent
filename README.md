# Simple AI Agent

Простой локальный AI-агент для ПК на Python.

Умеет:
- Создавать и изменять файлы
- Читать файлы и папки
- Запускать shell-команды
- Работать в цикле с инструментами (tool calling)

Поддерживает любой OpenAI-совместимый API (OpenAI, Grok, OpenRouter, Ollama и т.д.).

## Быстрая установка

```bash
git clone https://github.com/fima4335/simple-ai-agent.git
cd simple-ai-agent
pip install -r requirements.txt
```

Скопируй `.env.example` в `.env` и укажи ключ:

```bash
cp .env.example .env
# отредактируй .env
```

Запуск:

```bash
python agent.py
```

Или с одним файлом (если хочешь минимально):

```bash
python agent.py
```

## Настройка

В `.env`:

```env
OPENAI_API_KEY=твой_ключ
OPENAI_BASE_URL=https://api.openai.com/v1   # или https://api.x.ai/v1 для Grok
MODEL=gpt-4o-mini                           # или grok-beta, llama3.1 и т.д.
```

Для локальной модели через Ollama:

```env
OPENAI_API_KEY=ollama
OPENAI_BASE_URL=http://localhost:11434/v1
MODEL=llama3.1
```

## Как пользоваться

Просто пиши задачи на русском или английском:

- "Создай файл hello.py с кодом Hello World"
- "Прочитай содержимое папки"
- "Создай папку projects и в ней файл main.py"
- "Запусти команду ls -la"

Агент сам решает, какие инструменты использовать.

## Безопасность

Агент может выполнять shell-команды. Запускай только в доверенной среде.  
По умолчанию работает в текущей папке.

## Структура

- `agent.py` — основной файл
- `requirements.txt` — зависимости
- `.env.example` — пример настроек

Сделано просто и понятно. Можно дорабатывать.
