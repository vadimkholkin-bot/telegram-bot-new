from flask import Flask
import threading
import asyncio
from bot import bot_instance
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def index():
    return "🤖 Бот Дворецкий работает! Группа активна."

@app.route('/health')
def health():
    return "OK"

def run_bot():
    """Запуск бота в отдельном потоке"""
    try:
        logger.info("🚀 Запуск бота...")
        
        # Создаем новый event loop для этого потока
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Запускаем бота
        loop.run_until_complete(bot_instance.app.run_polling())
        
    except Exception as e:
        logger.error(f"Ошибка бота: {e}")

# Запускаем бот в отдельном потоке
bot_thread = threading.Thread(target=run_bot, daemon=True)
bot_thread.start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
