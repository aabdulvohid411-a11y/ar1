import os
import a2s
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, InputFile
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
import asyncio

TOKEN = "8339628428:AAGQza4vAsjKAexSKti1gHRkfYbE-xE0-r8"

SERVERS = {
    "Public": ("198.163.207.119", 27015, "armcs.uz:27015"),
    "CW1": ("198.163.207.119", 27017, "armcs.uz:27017"),
    "CW2": ("198.163.207.119", 27016, "armcs.uz:27016"),
}

# ==================== INFO FUNCTIONS ====================
def get_info(server_name: str) -> str:
    host, port, domen = SERVERS[server_name]
    try:
        info = a2s.info((host, port), timeout=5.0)
        players = a2s.players((host, port), timeout=5.0)
    except Exception as e:
        return f"❌ Не удалось подключиться к серверу: {e}"

    text = f"🎮 {info.server_name}\n📌 IP: {host}:{port}\n🌍 Домен: {domen}\n"
    text += f"🗺 Карта: {info.map_name}\n👥 Игроки: {info.player_count}/{info.max_players}\n"
    text += "====================\n\n👤 Список игроков:\n"
    if players:
        for i, p in enumerate(players, start=1):
            kills = getattr(p, "score", 0)
            text += f"⚡{i}. {p.name}  [{kills} - kill]\n"
    else:
        text += "🚫 Сейчас игроков нет\n"
    text += "\n====================\n"
    text += f"📊 Общее количество игроков: {info.player_count}\n"
    text += "\n====================\nЕсли хочешь стать админом,\nНажми кнопку ниже 👇"
    return text

def get_all_info() -> str:
    text = ""
    mapping = {"Public": "/public", "CW1": "/cw", "CW2": "/cw2"}
    for name, (host, port, domen) in SERVERS.items():
        try:
            info = a2s.info((host, port), timeout=5.0)
        except:
            continue
        text += f"🎮 {info.server_name}\n📌 IP: {host}:{port}\n🌍 Домен: {domen}\n"
        text += f"🗺 Карта: {info.map_name}\n👥 Игроков: {info.player_count}/{info.max_players}\n"
        text += f"🔥 Команда: {mapping[name]}\n====================\n\n"
    return text.strip()

# ==================== BOT SETUP ====================
bot = Bot(token=TOKEN)
dp = Dispatcher()

async def send_with_button(chat_id: int, msg: str):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👑 Стать админом", url="https://t.me/aLi_Raadx")],
        [InlineKeyboardButton(text="🌍 Наш сайт", url="https://armcs.uz")]
    ])
    photo_path = os.path.join(os.path.dirname(__file__), "logo.jpg")
    if os.path.exists(photo_path):
        photo = InputFile(photo_path)
        await bot.send_photo(chat_id=chat_id, photo=photo, caption=msg, reply_markup=keyboard)
    else:
        await bot.send_message(chat_id=chat_id, text=msg, reply_markup=keyboard)

# ==================== HANDLERS ====================
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    if message.chat.type == "private":
        kb_builder = ReplyKeyboardBuilder()
        kb_builder.add(KeyboardButton("📌Инфо"))
        kb_builder.add(KeyboardButton("⚡️Public"))
        kb_builder.add(KeyboardButton("🌟ClanWar"))
        kb_builder.add(KeyboardButton("🔥Cheaters"))
        kb = kb_builder.as_markup(resize_keyboard=True)
        await message.answer("Выберите сервер 👇", reply_markup=kb)
    else:
        await message.answer(
            "👋 Здравствуйте!\nЯ — официальный инфо-бот armcs.uz.\n\n"
            "ℹ️ Чтобы получить информацию о сервере в группе используйте:\n"
            "/public \n/cw \n/cw2 \n/info"
        )

@dp.message(Command(["public", "cw", "cw2"]))
async def server_cmd(message: types.Message):
    server_name = message.text.split()[0].replace("/", "").lower()
    mapping = {"public": "Public", "cw": "CW1", "cw2": "CW2"}
    if server_name in mapping:
        msg = get_info(mapping[server_name])
        await send_with_button(message.chat.id, msg)

@dp.message(Command("info"))
async def info_cmd(message: types.Message):
    msg = get_all_info()
    await send_with_button(message.chat.id, msg)

@dp.message()
async def button_handler(message: types.Message):
    text = message.text
    mapping = {"⚡️Public": "Public", "🌟ClanWar": "CW1", "🔥Cheaters": "CW2", "📌Инфо": "ALL"}
    if text not in mapping:
        return
    msg = get_all_info() if text == "📌Инфо" else get_info(mapping[text])
    await send_with_button(message.chat.id, msg)

# ==================== RUN ====================
async def main():
    print("Bot ishlayapti ✅")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
