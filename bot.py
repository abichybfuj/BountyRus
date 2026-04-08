import telebot
import os
from flask import Flask
from threading import Thread

# تشغيل سيرفر ويب بسيط لمنع تعليق Render
app = Flask(__name__)
@app.route('/')
def index(): return "OK"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# إعدادات البوت
TOKEN = '8686210830:AAG7FXgngesYgSFCElfuwAkNHNjk-Ckjd8k'
ADMIN = 8500403510 # ضـع الأيـدي حـقـك هـنـا

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "البوت شغال!")

@bot.message_handler(func=lambda m: m.from_user.id == ADMIN and m.chat.type == 'private')
def broadcast(message):
    # كود النشر المبسط
    bot.reply_to(message, "تم استلام رسالة النشر")

if __name__ == "__main__":
    Thread(target=run).start()
    bot.remove_webhook()
    bot.infinity_polling(skip_pending=True)
