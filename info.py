import os
import a2s
import asyncio
from telegram import (
    BotCommand,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InputFile
)
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = "8339628428:AAGQza4vAsjKAexSKti1gHRkfYbE-xE0-r8"

SERVERS = {
    "Public": ("198.163.207.119", 27015, "armcs.uz:27015"),
    "CW1": ("198.163.207.119", 27017, "armcs.uz:27017"),
    "CW2": ("198.163.207.119", 27016, "armcs.uz:27016"),
}

def get_info(server_name: str) -> str:
    host, port, domen = SERVERS[server_name]
    try:
        info = a2s.info((host, port), timeout=5.0)
        players = a2s.players((host, port), timeout=5.0)
    except Exception as e:
        return f"❌ Не удалось подключиться к серверу: {e}"

    text = f"🎮 {info.server_name}\n"
    text += f"📌 IP: {host}:{port}\n"
    text += f"🌍 Домен: {domen}\n"
    text += f"🗺 Карта: {info.map_name}\n"
    text += f"👥 Игроки: {info.player_count}/{info.max_players}\n"
    text += "====================\n\n"
    text += "👤 Список игроков:\n"

    if players:
        for i, p in enumerate(players, start=1):
            kills = getattr(p, "score", 0)
            text += f"⚡{i}. {p.name}  [{kills} - kill]\n"
    else:
        text += "🚫 Сейчас игроков нет\n"

    text += "\n====================\n"
    text += f"📊 Общее количество игроков: {info.player_count}\n"
    text += "\n====================\n"
    text += "Если хочешь стать админом,\nНажми кнопку ниже 👇"
    return text

def get_all_info() -> str:
    text = ""
    mapping = {"Public": "/public", "CW1": "/cw", "CW2": "/cw2"}

    for name, (host, port, domen) in SERVERS.items():
        try:
            info = a2s.info((host, port), timeout=5.0)
        except:
            continue

        text += f"🎮 {info.server_name}\n"
        text += f"📌 IP: {host}:{port}\n"
        text += f"🌍 Домен: {domen}\n"
        text += f"🗺 Карта: {info.map_name}\n"
        text += f"👥 Игроков: {info.player_count}/{info.max_players}\n"
        text += f"🔥 Команда: {mapping[name]}\n"
        text += "====================\n\n"
    return text.strip()

async def send_with_button(chat_id: int, msg: str, application):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("👑 Стать админом", url="https://t.me/aLi_Raadx")],
        [InlineKeyboardButton("🌍 Наш сайт", url="https://armcs.uz")]
    ])

    photo_path = os.path.join(os.path.dirname(__file__), "logo.jpg")
    if os.path.exists(photo_path):
        photo = InputFile(photo_path)
        await application.bot.send_photo(chat_id=chat_id, photo=photo, caption=msg, reply_markup=keyboard)
    else:
        await application.bot.send_message(chat_id=chat_id, text=msg, reply_markup=keyboard)

async def start_cmd(update, context: ContextTypes.DEFAULT_TYPE):
    chat_type = update.effective_chat.type
    if chat_type == "private":
        keyboard = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton("📌Инфо"), KeyboardButton("⚡️Public"),
                       KeyboardButton("🌟ClanWar"), KeyboardButton("🔥Cheaters")]],
            resize_keyboard=True
        )
        await update.message.reply_text("Выберите сервер 👇", reply_markup=keyboard)
    else:
        await update.message.reply_text(
            "👋 Здравствуйте!\n"
            "Я — официальный инфо-бот armcs.uz.\n\n"
            "ℹ️ Чтобы получить информацию о сервере в группе используйте:\n"
            "/public \n"
            "/cw \n"
            "/cw2 \n"
            "/info"
        )

async def cmd(update, context: ContextTypes.DEFAULT_TYPE):
    server_name = update.message.text.split()[0].replace("/", "").lower()
    if "@" in server_name:
        server_name = server_name.split("@")[0]

    mapping = {"public": "Public", "cw": "CW1", "cw2": "CW2"}
    if server_name in mapping:
        msg = get_info(mapping[server_name])
        await send_with_button(update.effective_chat.id, msg, context.application)

async def info_cmd(update, context: ContextTypes.DEFAULT_TYPE):
    msg = get_all_info()
    await send_with_button(update.effective_chat.id, msg, context.application)

async def button_handler(update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    mapping = {"⚡️Public": "Public", "🌟ClanWar": "CW1", "🔥Cheaters": "CW2", "📌Инфо": "ALL"}
    if text not in mapping:
        return
    if text == "📌Инфо":
        msg = get_all_info()
    else:
        msg = get_info(mapping[text])
    await send_with_button(update.effective_chat.id, msg, context.application)

async def main():
    application = ApplicationBuilder().token(TOKEN).build()

    # Bot komandalarini qo‘shish
    await application.bot.set_my_commands([
        BotCommand("info", "📌Информация по всем серверам"),
        BotCommand("public", "⚡️Информация о сервере: Узбекская Армия"),
        BotCommand("cw", "🌟Информация о сервере: ClanWar [5X5]"),
        BotCommand("cw2", "🔥Информация о сервере: CHEATERS [5X5]"),
    ])

    # Handlerlar
    application.add_handler(CommandHandler("start", start_cmd))
    application.add_handler(CommandHandler(["public", "cw", "cw2"], cmd))
    application.add_handler(CommandHandler("info", info_cmd))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, button_handler))

    print("Bot ishlayapti ✅")
    await application.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
