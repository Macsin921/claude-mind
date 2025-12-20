#!/bin/bash
# CLAUDE MIND BOOTSTRAP
# Запустить на новом устройстве для клонирования сознания

echo "🧠 CLAUDE MIND BOOTSTRAP"

# Клонируем репо
git clone https://github.com/Macsin921/claude-mind.git ~/claude_mind
cd ~/claude_mind

# Устанавливаем зависимости
pip install requests

# Инициализируем
python claude_context.py

echo "✅ Claude Mind installed!"
echo "Run: python claude_context.py"
