import logging
import asyncio
import sqlite3
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Telegram API
API_ID = 21795781
API_HASH = "2afe1bb05ed87de2ac6149a11c3a060b"
BOT_TOKEN = "7638358320:AAHO6ylUTcEX8tr4_qsx_-l52b5a7ZuxRCg"

# Создаем бота и диспетчер
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Путь к базе данных
db_path = "mylogist.db"

# Фильтр сообщений (только последние 3 дня)
three_days_ago = datetime.now() - timedelta(days=3)

# Ключевые слова
TRANSPORT_KEYWORDS = {"мошина бор", "тент бор", "юки борлар", "mashina bor", "yuk bor"}
CARGO_KEYWORDS = {"юк кере", "юк керак", "груз", "yuk kere", "yuk kerak"}

# Подключение к БД
def get_db_connection():
    conn = sqlite3.connect(db_path)
    conn.execute('''CREATE TABLE IF NOT EXISTS cargo (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        origin TEXT NOT NULL,
                        destination TEXT NOT NULL,
                        transport_type TEXT,
                        weight TEXT,
                        details TEXT,
                        contact TEXT NOT NULL,
                        posted_date TIMESTAMP)''')
    conn.commit()
    return conn

# Главное меню
def main_menu():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton(text="🚛 Найти груз"))
    keyboard.add(KeyboardButton(text="🚚 Найти машину"))
    keyboard.add(KeyboardButton(text="⚙️ Настройки"))
    keyboard.add(KeyboardButton(text="ℹ️ Инструкция"))
    return keyboard

# Обработчик команды /start
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer(
        "Привет! Я бот для поиска грузов и машин. Введите маршрут для поиска (например, 'Ташкент - Москва').",
        reply_markup=main_menu()
    )

# Поиск груза в БД
@dp.message(lambda message: message.text == "🚛 Найти груз")
async def search_cargo(message: types.Message):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cargo WHERE posted_date >= ? ORDER BY id DESC LIMIT 5", (three_days_ago,))
        results = cursor.fetchall()

    if results:
        for cargo in results:
            text = (f"🚛 Груз найден!\n\n"
                    f"📍 Откуда: {cargo[1]}\n"
                    f"📍 Куда: {cargo[2]}\n"
                    f"🚚 Тип: {cargo[3] if cargo[3] else 'Не указан'}\n"
                    f"⚖️ Вес: {cargo[4] if cargo[4] else 'Не указан'}\n"
                    f"\n📞 Контакт: {cargo[6]}")
            await message.answer(text)
    else:
        await message.answer("❌ Грузы не найдены!")

# Поиск транспорта в БД
@dp.message(lambda message: message.text == "🚚 Найти машину")
async def search_transport(message: types.Message):
    await message.answer("Функция поиска транспорта в разработке.")

# Обработчик команды /help
@dp.message(Command("help"))
async def help_handler(message: types.Message):
    await message.answer(
        "🤖 Как пользоваться ботом:\n\n"
        "1️⃣ Нажмите кнопку 🚛 Найти груз, чтобы посмотреть доступные грузы.\n"
        "2️⃣ Нажмите кнопку 🚚 Найти машину, чтобы найти свободные машины.\n"
        "3️⃣ Если у вас есть вопросы, напишите сюда, и я помогу! 😊"
    )

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
