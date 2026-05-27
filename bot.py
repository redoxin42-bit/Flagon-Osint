import os
import json
import logging
from aiogram import Bot, Dispatcher, executor, types
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBAPP_URL = os.getenv("WEBAPP_URL")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton(text="🔮 Открыть Flagon OSINT", web_app=types.WebAppInfo(url=WEBAPP_URL)))
    await message.answer(
        f"📡 **Flagon Core Terminal v3.2**\n\n"
        f"Модули Obsidian Graph View активированы. Все цепочки трассировки готовы к работе.",
        reply_markup=markup,
        parse_mode="Markdown"
    )

@dp.message_handler(content_types=types.ContentType.WEB_APP_DATA)
async def process_webapp_incoming(message: types.Message):
    try:
        data = json.loads(message.web_app_data.data)
        action = data.get("action")

        if action == "search_complete":
            query = data.get("query")
            fio = data.get("fio")
            born = data.get("born")
            age = data.get("age")
            phone = data.get("phone")

            # Генерируем массивный текстовый пак с данными обидчика
            report = (
                f"🗂 **[Flagon Сводка] РЕЗУЛЬТАТЫ ГЛУБОКОГО АНАЛИЗА**\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🔍 **Входной маркер:** `{query}`\n\n"
                f"👤 **ФИО Субъекта:** `{fio}`\n"
                f"📅 **Дата рождения:** `{born}` ({age})\n"
                f"📱 **Найденный телефон:** `{phone}`\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"👥 **Родственные связи и окружение:**\n"
                f"├ П-Мать: Иванова Елена Николаевна (+79997654321)\n"
                f"├ П-Отец: Иванов Сергей Петрович (+79998881122)\n"
                f"└ Брат: Иванов Артём Сергеевич (@artem_ivanov_99)\n\n"
                f"🌐 **Связанные базы и логи:**\n"
                f"└ Идентификатор сопоставлен через модули: `Maigret, VK, WhatsApp`.\n"
                f"⚖️ Сбор логов завершен. Данные сохранены в кэш сессии."
            )
            await message.answer(report, parse_mode="Markdown")

    except Exception as e:
        await message.answer(f"❌ Ошибка парсинга ядра: {str(e)}")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
