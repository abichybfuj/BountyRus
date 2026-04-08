import telebot
import os

# ضع التوكن الخاص بك هنا
API_TOKEN = '8686210830:AAGZmXopHLTELnyszWr7wsyhouPmr74vVjk'
# ضع الأيدي (ID) الخاص بحسابك الشخصي لكي لا ينشر البوت رسائل الغرباء
ADMIN_ID = 123456789  # يمكنك الحصول عليه من بوت @userinfobot

bot = telebot.TeleBot(API_TOKEN)
GROUPS_FILE = "groups.txt"

# وظيفة لتحميل المجموعات من الملف
def load_groups():
    if not os.path.exists(GROUPS_FILE):
        return set()
    with open(GROUPS_FILE, "r") as f:
        return set(line.strip() for line in f if line.strip())

# وظيفة لحفظ مجموعة جديدة في الملف
def save_group(chat_id):
    groups = load_groups()
    if str(chat_id) not in groups:
        with open(GROUPS_FILE, "a") as f:
            f.write(f"{chat_id}\n")
        return True
    return False

# استقبال أي رسالة في المجموعات لتخزين "الآيدي" تلقائياً
@bot.message_handler(content_types=['text', 'new_chat_members'])
def auto_register(message):
    if message.chat.type in ['group', 'supergroup']:
        if save_group(message.chat.id):
            print(f"✅ تم تسجيل مجموعة جديدة: {message.chat.title} ({message.chat.id})")

# محرك النشر: أي رسالة ترسلها أنت للبوت في "الخاص" سيتم نشرها للجميع
@bot.message_handler(func=lambda message: message.from_user.id == ADMIN_ID and message.chat.type == 'private')
def start_broadcast(message):
    groups = load_groups()
    if not groups:
        bot.reply_to(message, "❌ لا توجد مجموعات مسجلة حالياً.")
        return

    sent_count = 0
    fail_count = 0
    
    bot.reply_to(message, f"⏳ جاري النشر في {len(groups)} مجموعة...")

    for group_id in groups:
        try:
            # استخدام copy_message يرسل الرسالة وكأنها من البوت مباشرة (بدون كلمة Forwarded)
            bot.copy_message(chat_id=group_id, from_chat_id=message.chat.id, message_id=message.message_id)
            sent_count += 1
        except Exception as e:
            print(f"فشل الإرسال للمجموعة {group_id}: {e}")
            fail_count += 1

    bot.send_message(message.chat.id, f"✅ اكتمل النشر!\nتم بنجاح: {sent_count}\nفشل: {fail_count}")

print("البوت يعمل... أضف البوت للمجموعات وارسل له أي رسالة في الخاص لينشرها.")
bot.polling(none_stop=True)
