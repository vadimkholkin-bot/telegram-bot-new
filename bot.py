import logging
import os
import json
import re
import asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфигурация
BOT_TOKEN = "7624651707:AAHN9syUPmr5eRSis3xcf8C2YZBZ7r4UE1s"
GROUP_CHAT_ID = -1002617255730

# Файлы данных
USER_DATA_FILE = "data/user_data.json"
BIRTHDAYS_FILE = "data/birthdays.json"

# Соответствие thread_id и названий тем
TOPIC_THREAD_IDS = {
    4172: "Юмор и для настроения",
    884: "На каждый день",
    None: "Мой день рождения",
    687: "Хобби",
    5194: "Моё здоровье",
    3433: "Мой город",
    793: "Моя семья",
    8295: "Новости",
    1149: "Мы после школы",
    1138: "Молодые годы",
    685: "Школьные годы",
    3448: "Я кулинар",
    3446: "Мой сад",
    3434: "Мой отпуск",
    888: "Вечера встречи",
    1137: "Правила, советы, обучение"
}

# Ключевые слова для тем
TOPIC_KEYWORDS = {
    "На каждый день": ["привет", "как дела", "спасибо", "пока", "общение", "разговор", "делиться", "мысль", "вопрос", "обсуждаем", "делимся"],
    "Новости": ["новость", "событие", "произошло", "объявление", "информация", "сообщаю", "уведомление", "новое", "актуальное", "свежее"],
    "Молодые годы": ["детство", "малыш", "ребенок", "до школы", "детский сад", "родители", "двор", "игрушки", "первое", "воспоминания", "фото детства"],
    "Школьные годы": ["школа", "урок", "учитель", "класс", "одноклассники", "перемена", "домашка", "учебник", "директор", "здание школы", "фото школы"],
    "Мы после школы": ["институт", "университет", "работа", "карьера", "студент", "армия", "первая работа", "специальность", "профессия", "выпуск"],
    "Вечера встречи": ["встреча", "выпускной", "вечер", "встречаемся", "организация", "приглашение", "фото встречи", "видео встречи", "воспоминания встреч"],
    "Моя семья": ["семья", "дети", "внуки", "муж", "жена", "родители", "брат", "сестра", "свадьба", "рождение", "семейное", "родственники"],
    "Мой город": ["город", "улица", "парк", "достопримечательность", "архитектура", "история", "прогулка", "фото города", "видео города", "улицы"],
    "Мой сад": ["сад", "дача", "огород", "цветы", "овощи", "фрукты", "урожай", "грядки", "посадка", "растения", "деревья", "отдых на даче"],
    "Мой отпуск": ["отпуск", "отдых", "путешествие", "море", "горы", "отель", "поездка", "курорт", "экскурсия", "пляж", "отдыхаем"],
    "Я кулинар": ["рецепт", " готовка", "еда", "блюдо", "торт", "пирог", "суп", "салат", "выпечка", "кухня", "приготовление", "продукты"],
    "Хобби": ["хобби", "увлечение", "рукоделие", "рисование", "вязание", "коллекция", "творчество", "мастерство", "изделие", "работа", "создание", "куклы", "рыбалка", "виноделие"],
    "Моё здоровье": ["здоровье", "болезнь", "лечение", "врач", "больница", "диета", "спорт", "зарядка", "оздоровление", "рецепт здоровья", "самочувствие"],
    "Правила, советы, обучение": ["правило", "совет", "обучение", "инструкция", "помощь", "вопрос", "как сделать", "объяснение", "руководство", "подсказка"],
    "Юмор и для настроения": ["шутка", "юмор", "смех", "прикол", "анекдот", "веселье", "позитив", "улыбка", "смешно", "развлечение", "настроение"],
    "Мой день рождения": ["день рождения", "др", "поздравление", "поздравляю", "именины", "родился"]
}

# Запрещенные темы
FORBIDDEN_KEYWORDS = [
    "политика", "политик", "правительство", "президент", "выборы", "партия",
    "религия", "бог", "аллах", "церковь", "мечеть", "синагога", "вера", "религиозный"
]

# Российские праздники
RUSSIAN_HOLIDAYS = {
    (1, 1): "Новый год",
    (1, 7): "Рождество Христово",
    (2, 23): "День защитника Отечества",
    (3, 8): "Международный женский день",
    (5, 1): "Праздник Весны и Труда",
    (5, 9): "День Победы",
    (6, 12): "День России",
    (11, 4): "День народного единства"
}

class DvoretskiyBot:
    def __init__(self):
        self.app = Application.builder().token(BOT_TOKEN).build()
        self.user_data = self.load_json(USER_DATA_FILE)
        self.birthdays = self.load_json(BIRTHDAYS_FILE)
        self.setup_handlers()
        
    def load_json(self, filename):
        """Загрузка данных из JSON файла"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            return {}
    
    def save_json(self, filename, data):
        """Сохранение данных в JSON файла"""
        try:
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Ошибка сохранения {filename}: {e}")
    
    def get_user_name(self, user_id):
        """Получение имени пользователя"""
        return self.user_data.get(str(user_id), {}).get('name', 'друг')
    
    def save_user_data(self, user_id, name, birthday=None):
        """Сохранение данных пользователя"""
        user_id_str = str(user_id)
        if user_id_str not in self.user_data:
            self.user_data[user_id_str] = {}
        
        self.user_data[user_id_str]['name'] = name
        if birthday:
            self.user_data[user_id_str]['birthday'] = birthday
            self.user_data[user_id_str]['registered_at'] = datetime.now().isoformat()
            
        self.save_json(USER_DATA_FILE, self.user_data)
        
        if birthday:
            self.birthdays[user_id_str] = birthday
            self.save_json(BIRTHDAYS_FILE, self.birthdays)
    
    def get_user_birthday(self, user_id):
        """Получение дня рождения пользователя"""
        return self.user_data.get(str(user_id), {}).get('birthday')
    
    def get_all_birthdays(self):
        """Получение всех дней рождения"""
        result = []
        for user_id, birthday in self.birthdays.items():
            name = self.get_user_name(user_id)
            result.append(f"• {name}: {birthday}")
        return result
    
    def get_today_birthdays(self):
        """Получение дней рождения на сегодня"""
        today = datetime.now()
        today_str = today.strftime("%d.%m")
        
        birthdays_today = []
        for user_id, birthday in self.birthdays.items():
            if birthday == today_str:
                name = self.get_user_name(user_id)
                birthdays_today.append(name)
        
        return birthdays_today
    
    def parse_birthday(self, text):
        """Парсинг даты дня рождения"""
        try:
            if re.match(r'^\d{1,2}\.\d{1,2}$', text):
                day, month = text.split('.')
                day = int(day)
                month = int(month)
                
                if 1 <= month <= 12 and 1 <= day <= 31:
                    return f"{day:02d}.{month:02d}"
        except:
            pass
        return None
    
    def get_today_holiday(self):
        """Получение сегодняшнего праздника"""
        today = datetime.now()
        return RUSSIAN_HOLIDAYS.get((today.month, today.day))
    
    def get_next_holiday(self):
        """Получение ближайшего праздника"""
        today = datetime.now()
        current_year = today.year
        
        holidays_with_dates = []
        for (month, day), name in RUSSIAN_HOLIDAYS.items():
            try:
                holiday_date = datetime(current_year, month, day).date()
                if holiday_date >= today.date():
                    holidays_with_dates.append((holiday_date, name))
            except ValueError:
                continue
        
        holidays_with_dates.sort()
        
        if holidays_with_dates:
            next_holiday_date, next_holiday_name = holidays_with_dates[0]
            return f"{next_holiday_date.strftime('%d.%m')} - {next_holiday_name}"
        
        return None
    
    def get_current_topic(self, message):
        """Определяет текущую тему по thread_id"""
        thread_id = message.message_thread_id if hasattr(message, 'message_thread_id') else None
        return TOPIC_THREAD_IDS.get(thread_id, "Основной чат")
    
    def detect_topic(self, message_text):
        """Определяет наиболее подходящую тему для сообщения"""
        message_lower = message_text.lower()
        best_topic = None
        max_matches = 0
        
        for topic, keywords in TOPIC_KEYWORDS.items():
            matches = sum(1 for keyword in keywords if keyword in message_lower)
            if matches > max_matches:
                max_matches = matches
                best_topic = topic
                
        return best_topic if max_matches > 0 else None

    def check_forbidden_content(self, message_text):
        """Проверяет сообщение на запрещенные темы"""
        message_lower = message_text.lower()
        for keyword in FORBIDDEN_KEYWORDS:
            if keyword in message_lower:
                return True
        return False

    async def delete_message_later(self, message, delay=120):
        """Удаляет сообщение бота через указанное время"""
        await asyncio.sleep(delay)
        try:
            await message.delete()
        except:
            pass

    def setup_handlers(self):
        """Настройка обработчиков"""
        # Обработчики для групп
        self.app.add_handler(MessageHandler(filters.ChatType.GROUPS & filters.TEXT & ~filters.COMMAND, self.handle_group_messages))
        self.app.add_handler(MessageHandler(filters.ChatType.GROUPS & filters.StatusUpdate.NEW_CHAT_MEMBERS, self.welcome_new_member))
        
        # Обработчики команд
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(CommandHandler("topics", self.topics_command))
        self.app.add_handler(CommandHandler("birthdays", self.birthdays_command))
        self.app.add_handler(CommandHandler("mybirthday", self.mybirthday_command))
        self.app.add_handler(CommandHandler("holiday", self.holiday_command))
        self.app.add_handler(CommandHandler("nextholiday", self.nextholiday_command))
        self.app.add_handler(CommandHandler("rules", self.rules_command))
        
        # Обработчик кнопок
        self.app.add_handler(CallbackQueryHandler(self.button_handler))
        
        # Обработчик личных сообщений
        self.app.add_handler(MessageHandler(filters.ChatType.PRIVATE & filters.TEXT & ~filters.COMMAND, self.handle_private_messages))
    
    async def welcome_new_member(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Приветствие нового участника"""
        for member in update.message.new_chat_members:
            user_id = member.id
            
            if str(user_id) not in self.user_data:
                try:
                    await context.bot.send_message(
                        chat_id=user_id,
                        text="Я помощник Вадима Ивановича. Меня зовут Дворецкий. Как я могу к Вам обращаться?"
                    )
                    context.user_data['awaiting_name'] = True
                    context.user_data['new_user_id'] = user_id
                    
                    self.user_data[str(user_id)] = {
                        'first_join': datetime.now().isoformat(),
                        'name': None,
                        'birthday': None
                    }
                    self.save_json(USER_DATA_FILE, self.user_data)
                    
                except:
                    welcome_msg = await update.message.reply_text(
                        f"Добро пожаловать! Я помощник Вадима Ивановича. Меня зовут Дворецкий. Напишите мне в личные сообщения, чтобы представиться."
                    )
                    await self.delete_message_later(welcome_msg)

    async def handle_group_messages(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка сообщений в группе"""
        try:
            user_id = update.message.from_user.id
            message_text = update.message.text
            user_name = self.get_user_name(user_id)
            
            user_info = self.user_data.get(str(user_id), {})
            if not user_info.get('name'):
                return
            
            if user_info.get('name') and not user_info.get('first_message_sent'):
                await self.send_welcome_notifications(update, context, user_id, user_name)
                self.user_data[str(user_id)]['first_message_sent'] = True
                self.save_json(USER_DATA_FILE, self.user_data)
            
            message_lower = message_text.lower()
            
            if any(cmd in message_lower for cmd in ["мой день рождения", "моя дата рождения", "когда мой др"]):
                await self.process_my_birthday(update, user_id, user_name)
                return
            
            elif any(cmd in message_lower for cmd in ["дни рождения", "дни рождения участников", "список др"]):
                await self.process_birthdays_list(update, user_name)
                return
            
            elif any(cmd in message_lower for cmd in ["какой сегодня праздник", "сегодня праздник", "какой праздник сегодня"]):
                await self.process_today_holiday(update, user_name)
                return
            
            elif any(cmd in message_lollow for cmd in ["ближайший праздник", "следующий праздник", "когда следующий праздник"]):
                await self.process_next_holiday(update, user_name)
                return
            
            elif any(cmd in message_lower for cmd in ["правила", "правила группы", "инструкция"]):
                await self.process_rules(update, user_name)
                return
            
            elif any(cmd in message_lower for cmd in ["темы", "список тем", "доступные темы"]):
                await self.process_topics(update, user_name)
                return
            
            elif any(cmd in message_lower for cmd in ["помощь", "help", "команды"]):
                await self.process_help(update, user_name)
                return
            
            if self.check_forbidden_content(message_text):
                keyboard = [
                    [InlineKeyboardButton("🗑️ Удалить", callback_data=f"delete_{update.message.message_id}")],
                    [InlineKeyboardButton("📌 Оставить", callback_data=f"keep_{update.message.message_id}")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                warning_msg = await update.message.reply_text(
                    f"Вы {user_name}, написали сообщение, текст которого запрещён Правилами",
                    reply_markup=reply_markup
                )
                await self.delete_message_later(warning_msg)
                return
            
            if len(message_text) >= 3:
                current_topic = self.get_current_topic(update.message)
                detected_topic = self.detect_topic(message_text)
                
                if detected_topic and current_topic != detected_topic:
                    keyboard = [
                        [InlineKeyboardButton("🔄 Переслать", callback_data=f"forward_{detected_topic}_{update.message.message_id}")],
                        [InlineKeyboardButton("📌 Оставить", callback_data=f"stay_{update.message.message_id}")]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    topic_msg = await update.message.reply_text(
                        f"{user_name}, Ваше сообщение подходит для темы '{detected_topic}'",
                        reply_markup=reply_markup
                    )
                    await self.delete_message_later(topic_msg)
                    return

        except Exception as e:
            logger.error(f"Ошибка в handle_group_messages: {e}")

    async def send_welcome_notifications(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, user_name: str):
        """Отправка приветственных уведомлений при первом входе"""
        today_birthdays = self.get_today_birthdays()
        if today_birthdays:
            birthday_names = ", ".join(today_birthdays)
            birthday_msg = await update.message.reply_text(
                f"{user_name}, скажу по секрету - у {birthday_names} сегодня день рождения, не забудь поздравить!"
            )
            await self.delete_message_later(birthday_msg)
        
        today_holiday = self.get_today_holiday()
        if today_holiday:
            holiday_msg = await update.message.reply_text(
                f"{user_name}, сегодня в России отмечается праздник: {today_holiday}"
            )
            await self.delete_message_later(holiday_msg)

    async def process_my_birthday(self, update: Update, user_id: int, user_name: str):
        """Обработка запроса своего дня рождения"""
        birthday = self.get_user_birthday(user_id)
        if birthday:
            response = f"{user_name}, ваш день рождения: {birthday}"
        else:
            response = f"{user_name}, ваша дата дня рождения не сохранена"
        msg = await update.message.reply_text(response)
        await self.delete_message_later(msg)

    async def process_birthdays_list(self, update: Update, user_name: str):
        """Обработка запроса списка дней рождений"""
        birthdays = self.get_all_birthdays()
        if birthdays:
            response = f"{user_name}, дни рождения участников:\n" + "\n".join(birthdays)
        else:
            response = f"{user_name}, дни рождения участников еще не сохранены"
        msg = await update.message.reply_text(response)
        await self.delete_message_later(msg)

    async def process_today_holiday(self, update: Update, user_name: str):
        """Обработка запроса сегодняшнего праздника"""
        holiday = self.get_today_holiday()
        if holiday:
            response = f"{user_name}, сегодня праздник: {holiday}"
        else:
            response = f"{user_name}, сегодня нет праздников"
        msg = await update.message.reply_text(response)
        await self.delete_message_later(msg)

    async def process_next_holiday(self, update: Update, user_name: str):
        """Обработка запроса ближайшего праздника"""
        next_holiday = self.get_next_holiday()
        if next_holiday:
            response = f"{user_name}, ближайший праздник: {next_holiday}"
        else:
            response = f"{user_name}, праздников не найдено"
        msg = await update.message.reply_text(response)
        await self.delete_message_later(msg)

    async def process_rules(self, update: Update, user_name: str):
        """Обработка запроса правил"""
        rules_text = (
            f"{user_name}, правила группы:\n\n"
            "1. 📚 Соблюдайте тематику обсуждений\n"
            "2. 🚫 Запрещены политические и религиозные темы\n"
            "3. 💬 Уважайте других участников\n"
            "4. 🎯 Размещайте сообщения в соответствующих темах\n"
            "5. 🤖 Бот поможет определить подходящую тему"
        )
        msg = await update.message.reply_text(rules_text)
        await self.delete_message_later(msg)

    async def process_topics(self, update: Update, user_name: str):
        """Обработка запроса списка тем"""
        await self.topics_command(update, None)

    async def process_help(self, update: Update, user_name: str):
        """Обработка запроса помощи"""
        await self.help_command(update, None)

    async def handle_private_messages(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка личных сообщений (регистрация)"""
        user_id = update.message.from_user.id
        message_text = update.message.text
        
        if context.user_data.get('awaiting_name'):
            context.user_data['awaiting_name'] = False
            context.user_data['awaiting_birthday'] = True
            context.user_data['user_name'] = message_text
            
            topics_text = (
                "📋 Доступные темы в группе:\n\n"
                "🏷️ На каждый день\n🏷️ Новости\n🏷️ Молодые годы\n🏷️ Школьные годы\n"
                "🏷️ Мы после школы\n🏷️ Вечера встречи\n🏷️ Моя семья\n🏷️ Мой город\n"
                "🏷️ Мой сад\n🏷️ Мой отпуск\n🏷️ Я кулинар\n🏷️ Хобби\n🏷️ Моё здоровье\n"
                "🏷️ Правила, советы, обучение\n🏷️ Юмор и для настроения\n🏷️ Мой день рождения\n\n"
                "📚 Пожалуйста, ознакомьтесь с правилами группы в теме 'Правила, советы, обучение'"
            )
            
            await update.message.reply_text(topics_text)
            await update.message.reply_text(f"Приятно познакомиться, {message_text}! Назовите дату своего дня рождения в формате число и месяц (например, 15.05)")
            return
        
        if context.user_data.get('awaiting_birthday'):
            birthday = self.parse_birthday(message_text)
            if birthday:
                user_name = context.user_data['user_name']
                self.save_user_data(user_id, user_name, birthday)
                
                context.user_data.clear()
                
                success_msg = await update.message.reply_text(
                    f"Отлично, {user_name}! Регистрация завершена. Теперь вы можете использовать все функции бота в группе!"
                )
                
                today_holiday = self.get_today_holiday()
                if today_holiday:
                    await update.message.reply_text(f"Кстати, сегодня в России отмечается: {today_holiday}")
            else:
                error_msg = await update.message.reply_text("Пожалуйста, введите дату в правильном формате (например, 15.05)")
            return
        
        if str(user_id) in self.user_data:
            await update.message.reply_text("Вы уже зарегистрированы! Используйте команды в группе.")
        else:
            context.user_data['awaiting_name'] = True
            await update.message.reply_text("Я помощник Вадима Ивановича. Меня зовут Дворецкий. Как я могу к Вам обращаться?")

    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка нажатий на кнопки"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data.startswith("delete_"):
            message_id = int(data.split("_")[1])
            try:
                await context.bot.delete_message(chat_id=query.message.chat_id, message_id=message_id)
                await query.edit_message_text("✅ Сообщение удалено")
            except:
                await query.edit_message_text("❌ Не удалось удалить сообщение")
        
        elif data.startswith("keep_"):
            await query.edit_message_text("✅ Сообщение оставлено")
        
        elif data.startswith("forward_"):
            parts = data.split("_")
            topic_name = parts[1]
            message_id = int(parts[2])
            
            instructions = (
                f"📋 Чтобы переслать сообщение в тему '{topic_name}':\n\n"
                f"1. 📱 Нажмите и удерживайте свое сообщение\n"
                f"2. 📤 Выберите 'Переслать'\n"
                f"3. 🎯 Найдите тему '{topic_name}' в списке\n"
                f"4. ✅ Отправьте сообщение"
            )
            await query.edit_message_text(instructions)
        
        elif data.startswith("stay_"):
            await query.edit_message_text("✅ Сообщение остается в текущей теме")
        
        await self.delete_message_later(query.message, 30)

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /start"""
        if update.effective_chat.type == "private":
            await self.handle_private_messages(update, context)
        else:
            msg = await update.message.reply_text("Привет! Я бот-помощник для поддержания порядка в темах!")
            await self.delete_message_later(msg)

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /help"""
        help_text = """
🤖 **ДВОРЕЦКИЙ - ВАШ ПОМОЩНИК В ГРУППЕ**

**📝 ТЕКСТОВЫЕ КОМАНДЫ (пишите в чат):**

**🎂 Дни рождения:**
• "Мой день рождения" - узнать свою дату
• "Дни рождения участников" - список всех дней рождений

**🎊 Праздники:**
• "Какой сегодня праздник?" - сегодняшний праздник
• "Ближайший праздник" - следующий праздник

**📚 Информация:**
• "Правила" - правила группы
• "Темы" - список доступных тем
• "Помощь" - эта справка

**🔧 СЛУЖЕБНЫЕ КОМАНДЫ (через /):**
• /start - начать работу
• /help - помощь
• /topics - список тем
• /birthdays - дни рождения
• /mybirthday - мой день рождения
• /holiday - сегодняшний праздник
• /nextholiday - ближайший праздник
• /rules - правила группы

**⚡ АВТОМАТИЧЕСКИЕ ФУНКЦИИ:**
🎉 Сообщаю о днях рождения при вашем входе
🎊 Уведомляю о праздниках
⚠️ Контролирую запрещённые темы
🎯 Подсказываю подходящие темы для сообщений
        """
        msg = await update.message.reply_text(help_text)
        await self.delete_message_later(msg)

    async def topics_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /topics"""
        topics_text = "📋 **Доступные темы в группе:**\n\n"
        for topic in TOPIC_KEYWORDS.keys():
            topics_text += f"🏷️ {topic}\n"
        
        topics_text += "\n💡 Напишите сообщение - я подскажу подходящую тему!"
        msg = await update.message.reply_text(topics_text)
        await self.delete_message_later(msg)

    async def birthdays_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /birthdays"""
        user_id = str(update.message.from_user.id)
        if user_id not in self.user_data:
            error_msg = await update.message.reply_text("Сначала зарегистрируйтесь! Напишите любое сообщение в группе.")
            await self.delete_message_later(error_msg)
            return
            
        await self.process_birthdays_list(update, self.get_user_name(user_id))

    async def mybirthday_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /mybirthday"""
        user_id = str(update.message.from_user.id)
        if user_id not in self.user_data:
            error_msg = await update.message.reply_text("Сначала зарегистрируйтесь! Напишите любое сообщение в группе.")
            await self.delete_message_later(error_msg)
            return
            
        await self.process_my_birthday(update, user_id, self.get_user_name(user_id))

    async def holiday_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /holiday"""
        user_id = str(update.message.from_user.id)
        if user_id not in self.user_data:
            error_msg = await update.message.reply_text("Сначала зарегистрируйтесь! Напишите любое сообщение в группе.")
            await self.delete_message_later(error_msg)
            return
            
        await self.process_today_holiday(update, self.get_user_name(user_id))

    async def nextholiday_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /nextholiday"""
        user_id = str(update.message.from_user.id)
        if user_id not in self.user_data:
            error_msg = await update.message.reply_text("Сначала зарегистрируйтесь! Напишите любое сообщение в группе.")
            await self.delete_message_later(error_msg)
            return
            
        await self.process_next_holiday(update, self.get_user_name(user_id))

    async def rules_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /rules"""
        user_id = str(update.message.from_user.id)
        user_name = self.get_user_name(user_id)
        await self.process_rules(update, user_name)

# Создаем экземпляр бота для использования в app.py
bot_instance = DvoretskiyBot()

# Для локального тестирования (раскомментируйте если нужно тестировать локально)
if __name__ == "__main__":
    print("=" * 60)
    print("🚀 БОТ ДВОРЕЦКИЙ ЗАПУЩЕН!")
    print(f"👥 Группа: {GROUP_CHAT_ID}")
    print(f"📊 Зарегистрировано пользователей: {len(bot_instance.user_data)}")
    print("🎯 Все системы активированы")
    print("=" * 60)
    
    bot_instance.app.run_polling()

