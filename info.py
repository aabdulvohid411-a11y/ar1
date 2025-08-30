from telegram import ReplyKeyboardMarkup, BotCommand, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import telegram.error
import a2s
import os

SERVERS = {
    "Public": ("198.163.207.119", 27015, "armcs.uz:27015"),
    "CW1": ("198.163.207.119", 27017, "armcs.uz:27017"),
    "CW2": ("198.163.207.119", 27016, "armcs.uz:27016"),
}

# 🔹 Bitta server haqida to'liq ma'lumot
def get_info(server_name):
    host, port, domen = SERVERS[server_name]
    try:
        # timeout qo‘shildi (5 soniya)
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

# 🔹 Barcha serverlar haqida qisqa info (faqat /info uchun)
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

# 🔹 Rasm + tugmalar bilan yuborish
def send_with_button(update, context, msg):
    keyboard = [
        [InlineKeyboardButton("👑 Стать админом", url="https://t.me/aLi_Raadx")],
        [InlineKeyboardButton("🌍 Наш сайт", url="https://armcs.uz")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    photo_path = os.path.join(os.path.dirname(__file__), "logo.jpg")
    
    try:
        with open(photo_path, "rb") as photo_file:
            context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=photo_file,
                caption=msg,
                reply_markup=reply_markup
            )
    except FileNotFoundError:
        print("❌ Rasm topilmadi:", photo_path)
        update.effective_chat.send_message(msg)
    except telegram.error.NetworkError as e:
        print("Network error:", e)
    except Exception as e:
        print("Other error:", e)

def start(update, context):
    chat_type = update.message.chat.type
    if chat_type == "private":
        keyboard = [[ "📌Инфо","⚡️Public", "🌟ClanWar", "🔥Cheaters"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        update.message.reply_text("Выберите сервер 👇", reply_markup=reply_markup)
    else:
        update.message.reply_text(
            "👋 Здравствуйте!\n"
            "Я — официальный инфо-бот armcs.uz.\n\n"
            "ℹ️ Чтобы получить информацию о сервере в группе используйте:\n"
            "/public \n"
            "/cw \n"
            "/cw2 \n"
            "/info"
        )

# 🔹 Buyruqlarni tozalash (/public yoki /public@BotName)
def cmd(update, context):
    server_name = update.message.text.split()[0]

    # Agar /public@armcs1nfobot kelsa faqat /public qoldiramiz
    if "@" in server_name:
        server_name = server_name.split("@")[0]

    server_name = server_name.replace("/", "").upper()
    
    mapping = {"PUBLIC": "Public", "CW": "CW1", "CW2": "CW2"}

    if server_name in mapping:
        msg = get_info(mapping[server_name])
        send_with_button(update, context, msg)


def info(update, context):
    msg = get_all_info()
    send_with_button(update, context, msg)

def show_commands(update, context):
    update.message.reply_text(
        "📌 Доступные команды:\n"
        "/public\n"
        "/cw\n"
        "/cw2\n"
        "/info"
    )

def button_handler(update, context):
    try:
        if update.callback_query:
            message = update.callback_query.message
            text = update.callback_query.data
        elif update.message:
            message = update.message
            text = update.message.text
        else:
            return

        if message.chat.type == "private":
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
            send_with_button(update, context, msg)
    except Exception as e:
        print("Button handler error:", e)

def main():
    updater = Updater("8339628428:AAGQza4vAsjKAexSKti1gHRkfYbE-xE0-r8", use_context=True)
    dp = updater.dispatcher

    updater.bot.set_my_commands([
        BotCommand("info", "📌Информация по всем серверам "),
        BotCommand("public", "⚡️Информация о сервере: Узбекская Армия"),
        BotCommand("cw", "🌟Информация о сервере:ClanWar [5X5]"),
        BotCommand("cw2", "🔥Информация о сервере:CHEATERS [5X5]"),
    ])

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler(["public", "cw", "cw2"], cmd))
    dp.add_handler(CommandHandler("info", info))
    dp.add_handler(MessageHandler(Filters.regex(r"^/$"), show_commands))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, button_handler))

    updater.start_polling()
    print("bot ishlayabdi ✅")
    updater.idle()

if __name__ == "__main__":
    main()
