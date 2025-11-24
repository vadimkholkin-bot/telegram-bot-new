import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Настройка
BOT_TOKEN = "7624651707:AAHN9syUPmr5eRSis3xcf8C2YZBZ7r4UE1s"

# Включим логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создаем бота
app = Application.builder().token(BOT_TOKEN).build()

# Команда /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Привет! Я бот Дворецкий! Работаю на PythonAnywhere!")

# Команда /help  
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Помощь: /start - начать")

# Настройка обработчиков
app.add_handler(CommandHandler("start", start_command))
app.add_handler(CommandHandler("help", help_command))

# Запуск бота
if __name__ == "__main__":
    print("🚀 Бот запускается на PythonAnywhere...")
    app.run_polling()
    print("✅ Бот работает!")
