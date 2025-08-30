from telegram import (
    ReplyKeyboardMarkup, 
    BotCommand, 
    InlineKeyboardMarkup, 
    InlineKeyboardButton
)
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    filters, 
    ContextTypes
)
import a2s
import os
import asyncio

SERVERS = {
    "Public": ("198.163.207.119", 27015, "armcs.uz:27015"),
    "CW1": ("198.163.207.119", 27017, "armcs.uz:27017"),
    "CW2": ("198.163.207.119", 27016, "armcs.uz:27016"),
}

# 🔹 Server haqida info
def get_info(server_name):
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

# 🔹 Barcha serverlar haqida
def get_all_info():
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

# 🔹 Tugmalar + rasm bilan yuborish
async def send_with_button(update, context, msg):
    keyboard = [
        [InlineKeyboardButton("👑 Стать админом", url="https://t.me/aLi_Raadx")],
        [InlineKeyboardButton("🌍 Наш сайт", url="https://armcs.uz")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    photo_path = os.path.join(os.path.dirname(__file__), "logo.jpg")

    try:
        with open(photo_path, "rb") as photo_file:
            await update.message.reply_photo(
                photo=photo_file,
                caption=msg,
                reply_markup=reply_markup
            )
    except FileNotFoundError:
        await update.message.reply_text(msg)

# 🔹 Start komandasi
async def start(update, context: ContextTypes.DEFAULT_TYPE):
    chat_type = update.message.chat.type
    if chat_type == "private":
        keyboard = [["📌Инфо","⚡️Public", "🌟ClanWar", "🔥Cheaters"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("Выберите сервер 👇", reply_markup=reply_markup)
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

# 🔹 /public, /cw, /cw2
async def cmd(update, context: ContextTypes.DEFAULT_TYPE):
    server_name = update.message.text.split()[0]
    if "@" in server_name:
        server_name = server_name.split("@")[0]

    server_name = server_name.replace("/", "").upper()
    mapping = {"PUBLIC": "Public", "CW": "CW1", "CW2": "CW2"}

    if server_name in mapping:
        msg = get_info(mapping[server_name])
        await send_with_button(update, context, msg)

# 🔹 /info
async def info(update, context: ContextTypes.DEFAULT_TYPE):
    msg = get_all_info()
    await send_with_button(update, context, msg)

# 🔹 Custom handler
async def button_handler(update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "⚡️Public":
        msg = get_info("Public")
    elif text == "🌟ClanWar":
        msg = get_info("CW1")
    elif text == "🔥Cheaters":
        msg = get_info("CW2")
    elif text == "📌Инфо":
        msg = get_all_info()
    else:
        return
    await send_with_button(update, context, msg)

# 🔹 Main
def main():
    app = Application.builder().token("8339628428:AAGQza4vAsjKAexSKti1gHRkfYbE-xE0-r8").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler(["public", "cw", "cw2"], cmd))
    app.add_handler(CommandHandler("info", info))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, button_handler))

    # komandalarni qo'shamiz
    app.bot.set_my_commands([
        BotCommand("info", "📌Информация по всем серверам"),
        BotCommand("public", "⚡️Информация о Public сервере"),
        BotCommand("cw", "🌟Информация о ClanWar сервере"),
        BotCommand("cw2", "🔥Информация о CHEATERS сервере"),
    ])

    print("bot ishlayapti ✅")
    app.run_polling()

if __name__ == "__main__":
    main()
