import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

print("=== ЗАПУСК БОТА ДВОРЕЦКИЙ ===")

# Настройка
BOT_TOKEN = "7624651707:AAHN9syUPmr5eRSis3xcf8C2YZBZ7r4UE1s"
GROUP_CHAT_ID = -1002617255730

# Включим логирование
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Создаем бота
app = Application.builder().token(BOT_TOKEN).build()

# Хранилище в памяти
user_names = {}

# Команда /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_first_name = update.message.from_user.first_name
    
    if user_id not in user_names:
        await update.message.reply_text(
            f"🤖 Привет, {user_first_name}! Я бот Дворецкий!\n"
            f"Напишите мне ваше имя для регистрации:"
        )
        user_names[user_id] = {"status": "awaiting_name"}
        print(f"👤 Новый пользователь: {user_first_name}, ждет имя")
    else:
        name = user_names[user_id].get("name", user_first_name)
        await update.message.reply_text(f"С возвращением, {name}!")

# Обработка ВСЕХ сообщений
async def handle_all_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text
    chat_type = update.message.chat.type
    chat_id = update.message.chat.id
    
    print(f"🔴 ДИАГНОСТИКА: chat_type='{chat_type}' (тип: {type(chat_type)})")
    print(f"🔴 ДИАГНОСТИКА: chat_id={chat_id}")
    print(f"🔴 ДИАГНОСТИКА: текст='{text}'")
    
    # ЭКСТРЕННЫЙ ТЕСТ - принудительно обрабатываем как групповое
    if chat_id == -1002617255730:  # Ваш ID группы
        print("🟢 ПРИНУДИТЕЛЬНО обрабатываю как ГРУППУ")
        user_name = user_names.get(user_id, {}).get("name", "друг")
        text_lower = text.lower()
        
        if "мой день рождения" in text_lower:
            await update.message.reply_text(f"🎉 {user_name}, это РАБОТАЕТ! День рождения в группе!")
            return
        elif "правила" in text_lower:
            await update.message.reply_text(f"📚 {user_name}, правила группы!")
            return
        elif "темы" in text_lower:
            await update.message.reply_text(f"🏷️ {user_name}, доступные темы!")
            return
        else:
            print("❌ Не нашел ключевых фраз, НЕ отвечаю")
            return
    
    # Старая логика (на всякий случай)
    if chat_type == "private":
        print("📍 Обрабатываю как ЛИЧНОЕ сообщение")
        if user_id in user_names and user_names[user_id].get("status") == "awaiting_name":
            user_names[user_id] = {"name": text, "status": "registered"}
            await update.message.reply_text(f"🎉 Отлично, {text}! Вы зарегистрированы!")
        else:
            name = user_names.get(user_id, {}).get("name", "друг")
            await update.message.reply_text(f"Привет, {name}! Вы написали: {text}")
    else:
        print(f"📍 Обрабатываю как ГРУППОВОЕ сообщение")
        # Здесь будет остальная логика

# Команда /myinfo
async def myinfo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id in user_names and user_names[user_id].get("status") == "registered":
        name = user_names[user_id]["name"]
        await update.message.reply_text(f"📋 Ваше имя: {name}")
    else:
        await update.message.reply_text("Вы еще не зарегистрированы! Напишите /start")

# Команда /status
async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    count = len([u for u in user_names.values() if u.get("status") == "registered"])
    await update.message.reply_text(f"🟢 Бот работает! Зарегистрировано: {count}")

# Настройка обработчиков
app.add_handler(CommandHandler("start", start_command))
app.add_handler(CommandHandler("myinfo", myinfo_command))
app.add_handler(CommandHandler("status", status_command))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_all_messages))

# Запуск бота
if __name__ == "__main__":
    print("🚀 Бот запущен и готов!")
    print("📞 Ожидаю сообщения...")
    app.run_polling()
