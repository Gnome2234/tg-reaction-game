import os
import asyncio
import threading
import sys
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = '8478723313:AAGzqoYAjbUOHwU9cY6yam0T4JvMmFX3ZTw'
WEBAPP_URL = 'https://tg-reaction-game.onrender.com' 

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Начальные настройки
current_settings = {
    "speed": 7,
    "min_limit": -60,
    "max_limit": 60,
    "target_width": 18,
    "fail_on_edge": True,
    "bounce_mode": False,
    "color_bar": "#ffffff",
    "color_bg": "#222222",
    "color_target": "#00ff78"
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

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Играть 🎮", web_app=WebAppInfo(url=WEBAPP_URL))]
    ])
    await message.answer("🕹️ Reaction Game: Master Panel v3.0", reply_markup=markup)

if __name__ == '__main__':
    threading.Thread(target=lambda: asyncio.run(dp.start_polling(bot)), daemon=True).start()
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host='0.0.0.0', port=port)
