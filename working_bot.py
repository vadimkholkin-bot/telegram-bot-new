import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

print("=== ЗАПУСК БОТА ДВОРЕЦКИЙ ===")

# Настройка
BOT_TOKEN = "7624651707:AAHN9syUPmr5eRSis3xcf8C2YZBZ7r4UE1s"
GROUP_CHAT_ID = -1002617255730

# Включим логирование
logging.basicConfig(level=logging.INFO)

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

# Обработка сообщений в ЛИЧКЕ
async def handle_private_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text.strip()
    
    print(f"📨 Личное сообщение от {user_id}: {text}")
    
    if user_id in user_names and user_names[user_id].get("status") == "awaiting_name":
        user_names[user_id] = {"name": text, "status": "registered"}
        print(f"✅ Пользователь {user_id} зарегистрирован как: {text}")
        await update.message.reply_text(f"🎉 Отлично, {text}! Вы зарегистрированы!")
    else:
        name = user_names.get(user_id, {}).get("name", "друг")
        await update.message.reply_text(f"Привет, {name}! Вы написали: {text}")

# Обработка сообщений в ГРУППЕ
async def handle_group_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text.lower().strip()
    
    print(f"👥 Сообщение в группе от {user_id}: {text}")
    
    # Получаем имя пользователя
    user_name = user_names.get(user_id, {}).get("name", "друг")
    
    # Ответы на ключевые фразы
    if "мой день рождения" in text:
        await update.message.reply_text(f"{user_name}, ваша дата дня рождения еще не сохранена")
        return
    
    if "дни рождения" in text:
        await update.message.reply_text(f"{user_name}, список дней рождений пока пуст")
        return
    
    if "правила" in text:
        rules_text = (
            f"{user_name}, правила группы:\n\n"
            "1. 📚 Соблюдайте тематику обсуждений\n"
            "2. 🚫 Запрещены политические и религиозные темы\n"
            "3. 💬 Уважайте других участников\n"
            "4. 🎯 Размещайте сообщения в соответствующих темах\n"
            "5. 🤖 Бот поможет определить подходящую тему"
        )
        await update.message.reply_text(rules_text)
        return
    
    if "темы" in text:
        topics_text = (
            f"{user_name}, доступные темы:\n\n"
            "🏷️ На каждый день\n"
            "🏷️ Новости\n" 
            "🏷️ Молодые годы\n"
            "🏷️ Школьные годы\n"
            "🏷️ Мы после школы\n"
            "🏷️ Вечера встречи\n"
            "🏷️ Моя семья\n"
            "🏷️ Мой город\n"
            "🏷️ Мой сад\n"
            "🏷️ Мой отпуск\n"
            "🏷️ Я кулинар\n"
            "🏷️ Хобби\n"
            "🏷️ Моё здоровье\n"
            "🏷️ Правила, советы, обучение\n"
            "🏷️ Юмор и для настроения\n"
            "🏷️ Мой день рождения"
        )
        await update.message.reply_text(topics_text)
        return
    
    # Если не нашли ключевых фраз - не отвечаем
    print(f"❌ Не нашел ключевых фраз в сообщении: {text}")

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
app.add_handler(MessageHandler(filters.ChatType.PRIVATE & filters.TEXT & ~filters.COMMAND, handle_private_messages))
app.add_handler(MessageHandler(filters.ChatType.GROUPS & filters.TEXT & ~filters.COMMAND, handle_group_messages))

# Запуск бота
if __name__ == "__main__":
    print("🚀 Бот запущен и готов!")
    print("📞 Ожидаю сообщения...")
    app.run_polling()
