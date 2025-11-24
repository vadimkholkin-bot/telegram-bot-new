import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

print("=== ЗАПУСК БОТА ДВОРЕЦКИЙ ===")

# Настройка
BOT_TOKEN = "7624651707:AAHN9syUPmr5eRSis3xcf8C2YZBZ7r4UE1s"

# Включим логирование
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Создаем бота
app = Application.builder().token(BOT_TOKEN).build()

# Хранилище в памяти (простое решение)
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
        # Сохраняем что ждем имя
        user_names[user_id] = {"status": "awaiting_name"}
    else:
        name = user_names[user_id].get("name", user_first_name)
        await update.message.reply_text(f"С возвращением, {name}!")

# Обработка обычных сообщений
async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text.strip()
    
    # Если пользователь ожидает регистрацию
    if user_id in user_names and user_names[user_id].get("status") == "awaiting_name":
        user_names[user_id] = {
            "name": text,
            "status": "registered"
        }
        await update.message.reply_text(
            f"🎉 Отлично, {text}! Вы зарегистрированы!\n"
            f"Теперь я знаю как вас зовут!"
        )
    else:
        # Обычное сообщение
        name = user_names.get(user_id, {}).get("name", "друг")
        await update.message.reply_text(f"Привет, {name}! Вы написали: {text}")

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
    user_id = update.message.from_user.id
    await update.message.reply_text(f"🟢 Бот работает! Пользователей в памяти: {len(user_names)}")

# Настройка обработчиков
app.add_handler(CommandHandler("start", start_command))
app.add_handler(CommandHandler("myinfo", myinfo_command))
app.add_handler(CommandHandler("status", status_command))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))

# Запуск бота
if __name__ == "__main__":
    print("🚀 Бот запущен и готов к работе!")
    print("📞 Ожидаю сообщения...")
    app.run_polling()
