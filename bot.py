import logging
import json
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

print("🤖 Запускаю бота Дворецкий...")

# Настройка
BOT_TOKEN = "7624651707:AAHN9syUPmr5eRSis3xcf8C2YZBZ7r4UE1s"

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
logging.basicConfig(level=logging.INFO)

# Создаем бота
app = Application.builder().token(BOT_TOKEN).build()

# Загружаем данные
user_data = load_data()
print(f"📊 Загружено пользователей: {len(user_data)}")

# Команда /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    first_name = update.message.from_user.first_name
    
    if user_id not in user_data:
        # Новый пользователь
        await update.message.reply_text(
            f"🤖 Привет, {first_name}! Я бот Дворецкий!\n"
            f"Напишите мне ваше имя для регистрации:"
        )
        # Сохраняем что пользователь ожидает имя
        user_data[user_id] = {"awaiting_name": True, "first_name": first_name}
        save_data(user_data)
    else:
        # Существующий пользователь
        name = user_data[user_id].get('name', first_name)
        await update.message.reply_text(f"С возвращением, {name}!")

# Обработка обычных сообщений
async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Только личные сообщения
    if update.message.chat.type != "private":
        return
        
    user_id = str(update.message.from_user.id)
    text = update.message.text.strip()
    
    # Проверяем, ожидаем ли мы имя от пользователя
    if user_id in user_data and user_data[user_id].get('awaiting_name'):
        # Сохраняем имя
        user_data[user_id]['name'] = text
        user_data[user_id]['awaiting_name'] = False
        user_data[user_id]['registered_at'] = update.message.date.isoformat()
        save_data(user_data)
        
        await update.message.reply_text(
            f"🎉 Отлично, {text}! Регистрация завершена!\n"
            f"Теперь я буду обращаться к вам по имени.\n"
            f"Напишите /help для списка команд"
        )
    else:
        # Обычное сообщение
        name = user_data.get(user_id, {}).get('name', 'друг')
        await update.message.reply_text(f"Привет, {name}! Вы написали: {text}")

# Команда /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
🤖 БОТ ДВОРЕЦКИЙ - КОМАНДЫ:

/start - регистрация
/help - помощь
/myinfo - мои данные
/users - список пользователей

Просто напишите мне сообщение - я отвечу!
"""
    await update.message.reply_text(help_text)

# Команда /myinfo
async def myinfo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    if user_id in user_data:
        name = user_data[user_id].get('name', 'Не указано')
        await update.message.reply_text(f"📋 Ваши данные:\nИмя: {name}\nID: {user_id}")
    else:
        await update.message.reply_text("Вы еще не зарегистрированы! Напишите /start")

# Команда /users
async def users_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if user_data:
        users_list = "📊 Зарегистрированные пользователи:\n"
        count = 0
        for user_id, data in user_data.items():
            if data.get('name'):  # Только те, у кого есть имя
                name = data.get('name')
                users_list += f"• {name}\n"
                count += 1
        
        if count > 0:
            await update.message.reply_text(users_list)
        else:
            await update.message.reply_text("Пока нет полностью зарегистрированных пользователей")
    else:
        await update.message.reply_text("Пока нет зарегистрированных пользователей")

# Настройка обработчиков
app.add_handler(CommandHandler("start", start_command))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("myinfo", myinfo_command))
app.add_handler(CommandHandler("users", users_command))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))

# Запуск бота
if __name__ == "__main__":
    print("🚀 Бот запущен!")
    print("✅ Ожидаю сообщения...")
    app.run_polling()
