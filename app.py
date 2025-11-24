from flask import Flask
import threading
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

def run_bot():
    """Запуск бота в отдельном потоке"""
    try:
        logger.info("🚀 Запуск бота...")
        bot_instance.app.run_polling()
    except Exception as e:
        logger.error(f"Ошибка бота: {e}")

# Запускаем бот в отдельном потоке при старте Flask
bot_thread = threading.Thread(target=run_bot, daemon=True)
bot_thread.start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
