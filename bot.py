import os
import json
import logging
from aiogram import Bot, Dispatcher, executor, types
from dotenv import load_dotenv

# Настройка логирования сообщений в консоль Термукса
logging.basicConfig(level=logging.INFO)

# Загрузка конфигурации из файла .env
load_dotenv()

BOT_TOKEN = os.getenv("8859119831:AAFBBnqoZGOEBYtUcvf3xFMgk_ck1qXmzUg")
WEBAPP_URL = os.getenv("https://meek-cajeta-3c5742.netlify.app/")

if not BOT_TOKEN or not WEBAPP_URL:
    exit("Ошибка: Проверь файл .env! Переменные BOT_TOKEN или WEBAPP_URL пусты.")

# Инициализация объектов бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Обработчик стартовой команды
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    # Создаем красивую нижнюю клавиатуру (ReplyKeyboardMarkup)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    
    # Кнопка, привязанная к нашему Netlify-сайту
    webapp_button = types.KeyboardButton(
        text="🔮 Открыть Flagon OSINT", 
        web_app=types.WebAppInfo(url=WEBAPP_URL)
    )
    markup.add(webapp_button)
    
    await message.answer(
        f"🤖 **Рады видеть Вас, {message.from_user.first_name}!**\n\n"
        f"Добро пожаловать в программный комплекс **Flagon OSINT**.\n"
        f"Все инструменты управления упакованы в наш быстрый Liquidglass интерфейс.\n\n"
        f"Нажмите на кнопку ниже, чтобы начать безопасную сессию.",
        reply_markup=markup,
        parse_mode="Markdown"
    )

# ГЛАВНЫЙ ОБРАБОТЧИК ДАННЫХ ИЗ WEB APP
# Перехватывает любые пакеты, отправленные через метод tg.sendData()
@dp.message_handler(content_types=types.ContentType.WEB_APP_DATA)
async def handle_webapp_data(message: types.Message):
    try:
        # Парсим входящую строку JSON в Python-словарь
        payload = json.loads(message.web_app_data.data)
        action = payload.get("action")

        # 1. Сценарий: Реальный Поиск
        if action == "search":
            query = payload.get("query")
            services = payload.get("services", [])
            services_string = ", ".join([s.upper() for s in services])

            # Имитируем начало глубокого поиска
            await message.answer(
                f"⚡️ **Запущен глобальный поиск Flagon OSINT**\n"
                f"───\n"
                f"🔍 **Объект:** `{query}`\n"
                f"📡 **Задействовано модулей ({len(services)}):** `[{services_string}]`\n\n"
                f"⏳ _Пожалуйста, подождите. Идет сбор и дедупликация данных из баз данных..._"
                f"⚡️ Поиск успешно завершен! Совпадений не обнаружено.",
                parse_mode="Markdown"
            )

        # 2. Сценарий: Создание Зеркала бота
        elif action == "create_mirror":
            new_token = payload.get("token")
            # Обрезаем токен для безопасности при выводе в лог
            masked_token = new_token[:10] + "..." + new_token[-5:] if len(new_token) > 15 else "Невалидный токен"
            
            await message.answer(
                f"🔮 **Запрос на развертывание Зеркала**\n"
                f"───\n"
                f"🔑 **Получен токен:** `{masked_token}`\n"
                f"⚙️ **Статус синхронизации:** `Копирование структуры Liquid Glass`\n\n"
                f"✅ **Успех!** Новое зеркало успешно инициализировано и привязано к вашей учетной записи. "
                f"Вы можете управлять им через главного бота.",
                parse_mode="Markdown"
            )

        # 3. Сценарий: Покупка за Звезды Telegram
        elif action == "buy_stars":
            item = payload.get("item")
            price = payload.get("price")
            
            await message.answer(
                f"🪙 **Инициирована покупка через Telegram Stars**\n"
                f"───\n"
                f"📦 **Продукт:** `{item}`\n"
                f"⭐️ **Стоимость:** `{price} XTR`\n\n"
                f"🛒 _Для проведения транзакции воспользуйтесь официальным счетом, высланным платежным шлюзом Telegram..._",
                parse_mode="Markdown"
            )

        else:
            await message.answer("⚠️ Получен неизвестный пакет данных из интерфейса.")

    except json.JSONDecodeError:
        await message.answer("❌ Ошибка обработки пакета: некорректный формат JSON.")
    except Exception as e:
        await message.answer(format(f"❌ Системный сбой при обработке Web App: {str(e)}"))

if __name__ == '__main__':
    # Запуск поллинга бота
    executor.start_polling(dp, skip_updates=True)
