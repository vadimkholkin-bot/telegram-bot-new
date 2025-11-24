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
logging.basicConfig(level=logging.INFO)

# Создаем бота
app = Application.builder().token(BOT_TOKEN).build()

# Загружаем данные
user_data = load_data()
print(f"📊 Загружено пользователей: {len(user_data)}")

# Команда /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name
    
    if str(user_id) not in user_data:
        await update.message.reply_text(
            f"🤖 Привет, {user_name}! Я бот Дворецкий!\n"
            f"Напишите мне ваше имя (как хотите чтобы я к вам обращался)"
        )
        # Сохраняем временные данные
        user_data[str(user_id)] = {'temp_name': user_name}
        save_data(user_data)
    else:
        name = user_data[str(user_id)].get('name', user_name)
        await update.message.reply_text(f"С возвращением, {name}!")

# Команда /help  
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
🤖 БОТ ДВОРЕЦКИЙ - КОМАНДЫ:

/start - начать работу
/help - помощь
/myinfo - мои данные
/users - список пользователей

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
        name = user_data[str(user_id)].get('name', 'Не указано')
        await update.message.reply_text(f"📋 Ваши данные:\nИмя: {name}\nID: {user_id}")
    else:
        await update.message.reply_text("Вы еще не зарегистрированы! Напишите /start")

# Команда /users
async def users_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if user_data:
        users_list = "📊 Зарегистрированные пользователи:\n"
        for user_id, data in user_data.items():
            name = data.get('name', 'Без имени')
            users_list += f"• {name}\n"
        await update.message.reply_text(users_list)
    else:
        await update.message.reply_text("Пока нет зарегистрированных пользователей")

# Обработка обычных сообщений (регистрация)
async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Только личные сообщения
    if update.message.chat.type != "private":
        return
        
    user_id = update.message.from_user.id
    text = update.message.text.strip()
    
    # Если пользователь не зарегистрирован полностью - сохраняем имя
    if str(user_id) in user_data and not user_data[str(user_id)].get('name'):
        user_data[str(user_id)]['name'] = text
        user_data[str(user_id)]['registered_at'] = update.message.date.isoformat()
        save_data(user_data)
        
        await update.message.reply_text(
            f"🎉 Отлично, {text}! Регистрация завершена!\n"
            f"Теперь я буду обращаться к вам по имени в группе.\n"
            f"Используйте /help для списка команд"
        )

# Настройка обработчиков
app.add_handler(CommandHandler("start", start_command))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("myinfo", myinfo_command))
app.add_handler(CommandHandler("users", users_command))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))

# Запуск бота
if __name__ == "__main__":
    print("🚀 Бот запускается...")
    print(f"📊 Зарегистрировано пользователей: {len(user_data)}")
    print("✅ Бот работает!")
    app.run_polling()
