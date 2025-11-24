from flask import Flask, request
from bot import bot_instance
import logging
import os
from telegram import Update
import asyncio

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def index():
    return "🤖 Бот Дворецкий работает! Группа активна."

@app.route('/webhook', methods=['POST'])
def webhook():
    """Обработчик веб-хука от Telegram"""
    try:
        # Получаем обновление от Telegram
        update_data = request.get_json()
        
        # Создаем объект Update из данных
        update = Update.de_json(update_data, bot_instance.app.bot)
        
        # Запускаем асинхронную обработку
        asyncio.create_task(process_update_async(update))
        
        return '', 200
    except Exception as e:
        logger.error(f"Ошибка в webhook: {e}")
        return 'Error', 500

async def process_update_async(update):
    """Асинхронная обработка обновления"""
    try:
        await bot_instance.app.process_update(update)
    except Exception as e:
        logger.error(f"Ошибка при обработке обновления: {e}")

@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    """Установка веб-хука - вызовите этот URL один раз"""
    try:
        import requests
        
        token = "7624651707:AAHN9syUPmr5eRSis3xcf8C2YZBZ7r4UE1s"
        
        webhook_url = "https://telegram-bot-new-udpy.onrender.com/webhook"
        
        # Устанавливаем веб-хук
        url = f"https://api.telegram.org/bot{token}/setWebhook"
        response = requests.post(url, json={'url': webhook_url})
        
        result = response.json()
        
        if result.get('ok'):
            return f"✅ Веб-хук установлен!<br>URL: {webhook_url}<br>Ответ: {result}"
        else:
            return f"❌ Ошибка: {result}"
            
    except Exception as e:
        return f"❌ Ошибка: {str(e)}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
