import asyncio
import threading
import sys
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton

# --- КОНФИГ ---
API_TOKEN = '8478723313:AAGzqoYAjbUOHwU9cY6yam0T4JvMmFX3ZTw'
WEBAPP_URL = 'https://paraphysate-conner-subovoid.ngrok-free.dev/' 

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# СЕРВЕРНЫЕ НАСТРОЙКИ (по умолчанию)
current_game_settings = {
    "speed": 7,
    "fail_on_edge": True
}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('update_settings')
def handle_settings(data):
    global current_game_settings
    current_game_settings["speed"] = data.get("speed", 7)
    current_game_settings["fail_on_edge"] = data.get("fail_on_edge", True)
    # Рассылаем всем новые настройки
    emit('settings_changed', current_game_settings, broadcast=True)

@socketio.on('master_start')
def handle_start():
    # При старте отправляем команду и текущие настройки
    emit('start_level', current_game_settings, broadcast=True)

@socketio.on('player_press')
def handle_press(data):
    emit('show_result', data, broadcast=True)

def run_flask():
    try:
        socketio.run(app, host='0.0.0.0', port=5000, debug=False, use_reloader=False)
    except Exception as e:
        print(f"Ошибка Flask: {e}")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Играть2 🎮", web_app=WebAppInfo(url=WEBAPP_URL))]
    ])
    await message.answer("Открой Mini App для игры:", reply_markup=markup)

async def run_bot():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    threading.Thread(target=run_flask, daemon=True).start()
    try:
        asyncio.run(run_bot())
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)