import telebot
import os

# ضع التوكن الخاص بك هنا
API_TOKEN = '8686210830:AAG7FXgngesYgSFCElfuwAkNHNjk-Ckjd8k'
# ضع الأيدي (ID) الخاص بحسابك الشخصي
ADMIN_ID = 123456789 

bot = telebot.TeleBot(API_TOKEN)
GROUPS_FILE = "groups.txt"

# وظيفة لتحميل المجموعات وتجنب التكرار
def load_groups():
    if not os.path.exists(GROUPS_FILE):
        return set()
    with open(GROUPS_FILE, "r") as f:
        # استخدام set يمنع التكرار تلقائياً
        return {line.strip() for line in f if line.strip()}

# وظيفة لحفظ مجموعة جديدة
def save_group(chat_id):
    groups = load_groups()
    if str(chat_id) not in groups:
        with open(GROUPS_FILE, "a") as f:
            f.write(f"{chat_id}\n")
        return True
    return False

# استقبال الرسائل لتخزين معرف المجموعات
@bot.message_handler(content_types=['text', 'new_chat_members', 'group_chat_created'])
def auto_register(message):
    if message.chat.type in ['group', 'supergroup']:
        if save_group(message.chat.id):
            print(f"✅ تم تسجيل مجموعة جديدة: {message.chat.title}")

# النشر (عند إرسال رسالة خاصة من الأدمن)
@bot.message_handler(func=lambda message: message.from_user.id == ADMIN_ID and message.chat.type == 'private')
def start_broadcast(message):
    groups = list(load_groups()) # تحويلها لقائمة للنشر
    if not groups:
        bot.reply_to(message, "❌ لا توجد مجموعات مسجلة.")
        return

    bot.reply_to(message, f"⏳ جاري النشر في {len(groups)} مجموعة...")
    
    sent_count = 0
    fail_count = 0

    for group_id in groups:
        try:
            # تم استخدام copy_message لإرسال أي نوع (نص، صورة، فيديو)
            bot.copy_message(chat_id=group_id, from_chat_id=message.chat.id, message_id=message.message_id)
            sent_count += 1
        except Exception:
            fail_count += 1

    bot.send_message(message.chat.id, f"✅ اكتمل النشر!\nنجاح: {sent_count}\nفشل: {fail_count}")

print("🚀 البوت يعمل الآن بدون مشاكل...")
# استخدام infinity_polling يحل أغلب مشاكل التحذيرات والتعليق
bot.infinity_polling(timeout=10, long_polling_timeout=5)
