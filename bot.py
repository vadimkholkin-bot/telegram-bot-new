import logging
import json
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

print("🤖 Начинаю запуск бота...")

# Настройка
BOT_TOKEN = "7624651707:AAHN9syUPmr5eRSis3xcf8C2YZBZ7r4UE1s"
GROUP_CHAT_ID = -1002617255730

# Файл для данных
DATA_FILE = "user_data.json"

# Загрузка данных
def load_data():
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

# Сохранение данных  
def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Включим логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Создаем бота
app = Application.builder().token(BOT_TOKEN).build()

# Загружаем данные
user_data = load_data()

# Команда /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if str(user_id) not in user_data:
        await update.message.reply_text(
            "🤖 Привет! Я бот Дворецкий!\n"
            "Как мне к вам обращаться?"
        )
    else:
        name = user_data[str(user_id)]['name']
        await update.message.reply_text(f"С возвращением, {name}!")

# Команда /help  
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
🤖 БОТ ДВОРЕЦКИЙ - КОМАНДЫ:

/start - начать работу
/help - помощь
/myinfo - мои данные
/group - проверить группу

📝 В группе я также отвечаю на:
• "Мой день рождения"
• "Дни рождения"
• "Правила"
• "Темы"
"""
    await update.message.reply_text(help_text)

# Команда /myinfo
async def myinfo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if str(user_id) in user_data:
        name = user_data[str(user_id)]['name']
        await update.message.reply_text(f"Ваше имя: {name}")
    else:
        await update.message.reply_text("Вы еще не зарегистрированы!")

# Команда /group
async def group_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"ID группы: {GROUP_CHAT_ID}")

# Обработка обычных сообщений (регистрация)
async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Только личные сообщения
    if update.message.chat.type != "private":
        return
        
    user_id = update.message.from_user.id
    text = update.message.text
    
    # Если пользователь не зарегистрирован - сохраняем имя
    if str(user_id) not in user_data:
        user_data[str(user_id)] = {
            'name': text,
            'registered_at': update.message.date.isoformat()
        }
        save_data(user_data)
        await update.message.reply_text(
            f"Отлично, {text}! Вы зарегистрированы!\n"
            f"Теперь я буду обращаться к вам по имени в группе."
        )

# Настройка обработчиков
app.add_handler(CommandHandler("start", start_command))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("myinfo", myinfo_command))
app.add_handler(CommandHandler("group", group_command))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))

# Запуск бота
if __name__ == "__main__":
    print("🚀 Бот запускается...")
    print(f"📊 Зарегистрировано пользователей: {len(user_data)}")
    print("✅ Бот работает!")
    app.run_polling()
