import os
import asyncio
import threading
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton

# --- ДАННЫЕ (ЗАМЕНИ НА СВОИ) ---
API_TOKEN = '8478723313:AAGzqoYAjbUOHwU9cY6yam0T4JvMmFX3ZTw'
# Ссылку вставишь после того, как создашь проект на Render (см. ниже)
WEBAPP_URL = 'https://tg-reaction-game.onrender.com' 

app = Flask(__name__)
# Используем стандартный threading для облака
socketio = SocketIO(app, cors_allowed_origins="*")

# Глобальные настройки
current_settings = {
    "speed": 7,
    "min_limit": 3,
    "max_limit": 60,
    "target_width": 18,
    "fail_on_edge": True,
    "bounce_mode": False,
    "color_bar": "#ffffff",
    "color_bg": "#222222",
    "color_target": "#00ff78"  # <--- Проверь, чтобы это было здесь
}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('update_settings')
def handle_settings(data):
    global current_settings
    current_settings = data
    emit('settings_changed', data, broadcast=True)

@socketio.on('master_start')
def handle_start():
    emit('start_level', current_settings, broadcast=True)

@socketio.on('player_press')
def handle_press(data):
    emit('show_result', data, broadcast=True)

# Бот
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎮 Запустить игру🎮 ", web_app=WebAppInfo(url=WEBAPP_URL))]
    ])
    await message.answer(f"Reaction Test готов!\nСсылка: {WEBAPP_URL}", reply_markup=markup)

async def start_bot():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

def run_bot():
    asyncio.run(start_bot())

if __name__ == '__main__':
    # Запуск бота в потоке
    threading.Thread(target=run_bot, daemon=True).start()
    # Запуск сервера
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host='0.0.0.0', port=port)

