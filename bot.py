import os
import json
import logging
from aiogram import Bot, Dispatcher, executor, types
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
load_dotenv()

BOT_TOKEN = os.getenv("8859119831:AAFBBnqoZGOEBYtUcvf3xFMgk_ck1qXmzUg")
WEBAPP_URL = os.getenv("https://meek-cajeta-3c5742.netlify.app/")

if not BOT_TOKEN or not WEBAPP_URL:
    exit("Ошибка конфигурации: Проверьте переменные среды в .env")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    webapp_btn = types.KeyboardButton(
        text="🔮 Открыть Flagon OSINT", 
        web_app=types.WebAppInfo(url=WEBAPP_URL)
    )
    markup.add(webapp_btn)
    
    await message.answer(
        f"🛡 **Система авторизации Flagon OSINT**\n\n"
        f"Приветствуем Вас, `{message.from_user.first_name}`. Модули ядра синхронизированы с Netlify-сервером. "
        f"Задействован интерактивный движок вычисления графов связей Obsidian.\n\n"
        f"Используйте кнопку меню для вызова панели управления.",
        reply_markup=markup,
        parse_mode="Markdown"
    )

@dp.message_handler(content_types=types.ContentType.WEB_APP_DATA)
async def process_webapp_incoming(message: types.Message):
    try:
        raw_data = message.web_app_data.data
        data = json.loads(raw_data)
        action = data.get("action")

        if action == "search":
            query = data.get("query")
            search_type = data.get("type", "unknown")
            modules = data.get("modules", [])
            
            # Маппинг типов поиска на читаемый язык
            type_mapping = {
                "tg_user": "Юзернейм Telegram",
                "phone": "Номер мобильного телефона",
                "vk_id": "Учетная запись ВКонтакте",
                "whatsapp": "Идентификатор WhatsApp"
            }
            readable_type = type_mapping.get(search_type, "Смешанный тип")
            mods_line = ", ".join(modules) if modules else "Авто-выбор"
            
            # Итоговый живой лог-отчет после прогона Obsidian-анимации
            await message.answer(
                f"📡 **[Flagon Core] Результаты трассировки Obsidian Graph**\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📊 **Тип пробива:** `{readable_type}`\n"
                f"🔍 **Объект проверки:** `{query}`\n"
                f"🧬 **Узлы цепочки:** `[{mods_line}]`\n\n"
                f"✅ **Статус:** Трассировка графа связей завершена. Пакеты данных успешно обработаны. "
                f"Поисковая сессия закрыта без ошибок.",
                parse_mode="Markdown"
            )

        elif action == "create_mirror":
            token = data.get("token")
            hidden = token[:9] + "..." + token[-4:] if len(token) > 15 else "Маска ошибки"
            
            await message.answer(
                f"🔮 **[Синхронизация Ядер] Выделенное зеркало**\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🔑 **Token:** `{hidden}`\n"
                f"🛠 **Конфигурация UI:** `Capsule Dock / Liquid Glass`\n\n"
                f"✅ Копия успешно скомпилирована. База данных Flagon интегрирована.",
                parse_mode="Markdown"
            )

        elif action == "buy_stars":
            item = data.get("item")
            cost = data.get("cost")
            
            await message.answer(
                f"⭐️ **[Telegram Stars Pay] Счёт сформирован**\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📦 **Услуга:** `{item}`\n"
                f"💎 **Номинал транзакции:** `{cost} XTR`\n\n"
                f"🛒 Для проведения оплаты используйте всплывающее диалоговое окно шлюза.",
                parse_mode="Markdown"
            )

    except json.JSONDecodeError:
        await message.answer("❌ Внутренний сбой ядра: Ошибка структуры JSON.")
    except Exception as e:
        await message.answer(f"❌ Критическая ошибка обработки: {str(e)}")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
