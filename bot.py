import telebot
import os
from flask import Flask
from threading import Thread

# 1. جزء الـ Flask عشان يرضي سيرفر Render وما يعطيك كتابة برتقالية
app = Flask('')

@app.route('/')
def home():
    return "البوت شغال 100%"

def run():
    # Render يحتاج يشوف بورت مفتوح عشان ما يقفل البوت
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# 2. إعدادات البوت (تأكد من وضع التوكن الجديد)
API_TOKEN = '8686210830:AAG7FXgngesYgSFCElfuwAkNHNjk-Ckjd8k' 
ADMIN_ID = 123456789  # ضع الأيدي حقك هنا

bot = telebot.TeleBot(API_TOKEN)
GROUPS_FILE = "groups.txt"

def load_groups():
    if not os.path.exists(GROUPS_FILE): return set()
    with open(GROUPS_FILE, "r") as f:
        return {line.strip() for line in f if line.strip()}

def save_group(chat_id):
    groups = load_groups()
    if str(chat_id) not in groups:
        with open(GROUPS_FILE, "a") as f:
            f.write(f"{chat_id}\n")
        return True
    return False

@bot.message_handler(content_types=)
def auto_register(message):
    if message.chat.type in ['group', 'supergroup']:
        save_group(message.chat.id)

@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID and m.chat.type == 'private')
def start_broadcast(message):
    groups = load_groups()
    if not groups:
        bot.reply_to(message, "❌ القائمة فارغة.")
        return
    bot.reply_to(message, f"⏳ جاري النشر في {len(groups)} مجموعة...")
    sent = 0
    for group_id in groups:
        try:
            bot.copy_message(chat_id=group_id, from_chat_id=message.chat.id, message_id=message.message_id)
            sent += 1
        except: continue
    bot.send_message(message.chat.id, f"✅ تم النشر في: {sent}")

# 3. تشغيل البوت مع تنظيف الاتصالات القديمة
if __name__ == "__main__":
    print("🚀 البوت يبدأ العمل...")
    keep_alive() # يفتح البورت الوهمي
    bot.remove_webhook() # ينهي أي تعارض قديم (Conflict 409)
    bot.infinity_polling(skip_pending=True) # يمنع تعليق الرسائل القديمة
