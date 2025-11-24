from flask import Flask
import threading
import asyncio
from bot import bot_instance
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def index():
    return "🤖 Бот Дворецкий работает! Группа активна."

@app.route('/health')
def health():
    return "OK"

async def run_bot_async():
    """Асинхронный запуск бота"""
    try:
        logger.info("🚀 Запуск бота...")
        await bot_instance.app.run_polling()
    except Exception as e:
        logger.error(f"Ошибка бота: {e}")

def run_bot():
    """Запуск бота в отдельном event loop"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_bot_async())

# Запускаем бот в отдельном потоке
bot_thread = threading.Thread(target=run_bot, daemon=True)
bot_thread.start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
