import sqlite3
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Токен вашего Telegram бота (хранить строго на сервере!)
TOKEN = "8859119831:AAFBBnqoZGOEBYtUcvf3xFMgk_ck1qXmzUg"

# URL вашего WebApp приложения с дизайном Liquid Glass
WEBAPP_URL = "https://flagonosint.org"

# Включаем логирование, чтобы видеть ошибки в терминале Termux
logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

def init_local_db():
    """Инициализация базы данных, если она запускается на том же устройстве"""
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            tg_id INTEGER PRIMARY KEY,
            username TEXT,
            searches_count INTEGER DEFAULT 0,
            search_limits INTEGER DEFAULT 2,
            stars_balance INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    tg_id = message.from_user.id
    username = message.from_user.username or f"user_{tg_id}"
    
    # Регистрация пользователя в локальной базе данных при старте
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('INSERT OR IGNORE INTO users (tg_id, username) VALUES (?, ?)', (tg_id, username))
        conn.commit()
        conn.close()
    except Exception as e:
        logging.error(f"Ошибка бд: {e}")

    # Создаем интерактивную кнопку для открытия WebApp
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(
            text="🔮 Запустить Flagon OSINT",
            web_app=types.WebAppInfo(url=WEBAPP_URL)
        )
    )
    
    welcome_text = (
        f"Привет, <b>{message.from_user.first_name}</b>!

"
        f"Добро пожаловать в <b>Flagon OSINT</b> — мобильный инструмент для "
        f"анализа цифрового следа и построения связей.

"
        f"Нажмите на кнопку ниже, чтобы открыть панель управления:"
    )
    
    await message.answer(welcome_text, reply_markup=builder.as_markup(), parse_mode="HTML")

async def main():
    init_local_db()
    print("Бот успешно запущен и готов к работе в Termux/Хостинге!")
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Бот остановлен.")
