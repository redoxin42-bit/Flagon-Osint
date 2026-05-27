import os
import json
import logging
import sqlite3
import asyncio
from datetime import datetime
from aiogram import Bot, Dispatcher, executor, types

logging.basicConfig(level=logging.INFO)

# --- Настройки конфигурации ---
BOT_TOKEN = "8859119831:AAFBBnqoZGOEBYtUcvf3xFMgk_ck1qXmzUg"
WEBAPP_URL = "https://meek-cajeta-3c5742.netlify.app/"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

current_dir = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(current_dir, "flagon_osint.db")

# --- Инициализация локальной базы SQLite ---
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS osint_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT UNIQUE,
            scan_date TEXT,
            platforms_found TEXT,
            raw_json TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# --- Боевой Движок: Вызов утилит через Консоль Термукса ---
async def run_heavy_osint_tools(query):
    clean_target = query.lstrip('@').strip()
    found_profiles = []

    # 1. Запуск НАСТОЯЩЕГО Maigret
    # --top-sites 150 проверяет самые популярные ресурсы СНГ и мира, сохраняет в json
    logging.info(f"Запуск Maigret для цели {clean_target}...")
    maigret_cmd = f"maigret {clean_target} --top-sites 150 --json report"
    
    proc_maigret = await asyncio.create_subprocess_shell(
        maigret_cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    await proc_maigret.communicate()

    # Парсим официальный JSON-отчет Maigret
    # По умолчанию maigret складывает их в папку reports/
    maigret_report = os.path.join(current_dir, "reports", f"report_{clean_target}.json")
    if os.path.exists(maigret_report):
        try:
            with open(maigret_report, "r", encoding="utf-8") as f:
                m_data = json.load(f)
                for site_name, site_info in m_data.get("sites", {}).items():
                    if site_info.get("status") == "claimed":
                        found_profiles.append({
                            "platform": f"📌 Maigret: {site_name}",
                            "url": site_info.get("url")
                        })
            os.remove(maigret_report) # Чистим тяжелые файлы за собой
        except Exception as e:
            logging.error(f"Ошибка чтения отчета Maigret: {e}")

    # 2. Запуск НАСТОЯЩЕГО Sherlock
    sherlock_script = os.path.join(current_dir, "sherlock", "sherlock", "sherlock.py")
    if os.path.exists(sherlock_script):
        logging.info(f"Запуск Sherlock для цели {clean_target}...")
        sherlock_cmd = f"python {sherlock_script} {clean_target} --timeout 5"
        
        proc_sherlock = await asyncio.create_subprocess_shell(
            sherlock_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await proc_sherlock.communicate()

        # Sherlock создает обычный текстовый файл с именем цели в текущей папке
        sherlock_report = os.path.join(current_dir, f"{clean_target}.txt")
        if os.path.exists(sherlock_report):
            try:
                with open(sherlock_report, "r", encoding="utf-8") as f:
                    for line in f:
                        if "http" in line and not line.startswith("="):
                            # Пример строки: GitHub: https://github.com/nick
                            parts = line.split(": ")
                            if len(parts) >= 2:
                                site_name = parts[0].strip()
                                site_url = ": ".join(parts[1:]).strip()
                                found_profiles.append({
                                    "platform": f"🔍 Sherlock: {site_name}",
                                    "url": site_url
                                })
                os.remove(sherlock_report) # Удаляем текстовый лог
            except Exception as e:
                logging.error(f"Ошибка чтения отчета Sherlock: {e}")

    # Удаляем дубликаты, если и Sherlock и Maigret нашли один и тот же сайт
    unique_profiles = {p['url']: p for p in found_profiles}.values()
    return list(unique_profiles)

# --- Логика Обработки Сообщений ---
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton(text="🔮 Открыть Flagon OSINT", web_app=types.WebAppInfo(url=WEBAPP_URL)))
    
    await message.answer(
        f"📡 **Flagon Core v6.0 [HARDWARE MODE]**\n\n"
        f"• Официальный софт **Maigret CLI**: `Интегрирован`\n"
        f"• Официальный софт **Sherlock Core**: `Подключен`\n"
        f"• База данных СУБД SQLite: `Синхронизирована`\n\n"
        f"Запускай поиск через Liquid Glass панель.",
        reply_markup=markup,
        parse_mode="Markdown"
    )

@dp.message_handler(content_types=types.ContentType.WEB_APP_DATA)
async def process_webapp_incoming(message: types.Message):
    try:
        raw_data = message.web_app_data.data
        try:
            data = json.loads(raw_data)
            query = data.get("query", "").strip()
        except json.JSONDecodeError:
            query = raw_data.strip()

        if not query:
            await message.answer("❌ Пустой поисковый запрос.")
            return

        # Проверяем локальный кэш SQLite
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT scan_date, platforms_found, raw_json FROM osint_cache WHERE query = ?", (query,))
        cached_result = cursor.fetchone()

        if cached_result:
            scan_date, platforms_count, raw_json = cached_result
            conn.close()
            
            profiles = json.loads(raw_json)
            report = (
                f"🗄 **[КЭШ БАЗЫ ДАННЫХ] РЕЗУЛЬТАТЫ СЛЕДА**\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🔍 **Запрос:** `{query}`\n"
                f"📅 **Дата первой фиксации:** `{scan_date}`\n\n"
                f"🌐 **Найденные профили ({platforms_count}):**\n"
            )
            for p in profiles:
                report += f"├ {p['platform']}: {p['url']}\n"
            report += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n⚖️ Данные подняты из локального дампа."
            
            await message.answer(report, parse_mode="Markdown", disable_web_page_preview=True)
            return

        # Если данных нет — запускаем консольный хардкорный скан
        status_msg = await message.answer(
            f"⏳ **[Flagon Скан]** Запись в SQLite отсутствует.\n"
            f"Инициализирую системный вызов `maigret` и `sherlock` в ядре Termux...\n"
            f"*Пожалуйста, подождите, идет глубокая трассировка (15-20 сек)...*"
        )
        
        # Запуск утилит
        real_profiles = await run_heavy_osint_tools(query)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Сохраняем логи в базу данных
        cursor.execute(
            "INSERT OR REPLACE INTO osint_cache (query, scan_date, platforms_found, raw_json) VALUES (?, ?, ?, ?)",
            (query, current_time, len(real_profiles), json.dumps(real_profiles))
        )
        conn.commit()
        conn.close()

        # Формируем финальный рапорт
        report = (
            f"📡 **[Flagon Ядро] ОФИЦИАЛЬНЫЙ РАПОРТ СБОРЩИКОВ**\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🔍 **Субъект поиска:** `{query}`\n"
            f"⏱ **Время завершения:** `{current_time}`\n\n"
            f"📊 **Найденные совпадения утилит:**\n"
        )
        
        if real_profiles:
            for p in real_profiles:
                report += f"├ {p['platform']}: {p['url']}\n"
            report += f"\n💾 Результаты упакованы в кэш базы `flagon_osint.db`."
        else:
            report += "└ ❌ Утилиты Maigret и Sherlock не нашли активных профилей с таким именем."
            
        report += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        
        await status_msg.delete()
        await message.answer(report, parse_mode="Markdown", disable_web_page_preview=True)

    except Exception as e:
        await message.answer(f"❌ Критический сбой системного вызова: {str(e)}")

if __name__ == '__main__':
    print("--------------------------------------------------")
    print(f" LOG: Запуск Flagon OSINT HARDWARE CORE v6.0")
    print(f" LOG: Движки Maigret и Sherlock переведены на автоматический парсинг.")
    print("--------------------------------------------------")
    executor.start_polling(dp, skip_updates=True)
