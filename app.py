from flask import Flask
import threading

# Добавьте этот код в САМЫЙ КОНЕЦ файла bot.py

# Создаем простой Flask сервер
flask_app = Flask(__name__)

@flask_app.route('/')
def health_check():
    return "🤖 Бот Дворецкий работает!"

@flask_app.route('/health')
def health():
    return "OK"

def run_flask():
    flask_app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

# Запускаем Flask в отдельном потоке
if __name__ == "__main__":
    # Запускаем Flask сервер
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Запускаем бота
    print("=" * 60)
    print("🚀 БОТ ДВОРЕЦКИЙ ЗАПУЩЕН!")
    print(f"👥 Группа: {GROUP_CHAT_ID}")
    print(f"📊 Зарегистрировано пользователей: {len(bot_instance.user_data)}")
    print("🎯 Все системы активированы")
    print("=" * 60)
    
    bot_instance.app.run_polling()
