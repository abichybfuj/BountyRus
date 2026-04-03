import telebot
import feedparser
import time
import threading
from datetime import datetime, timedelta

# --- الإعدادات ---
TOKEN = '8686210830:AAGZmXopHLTELnyszWr7wsyhouPmr74vVjk' # ضع التوكن الخاص بك هنا
YOUTUBE_RSS_URL = 'https://youtube.com' # معرف قناة Bandai Namco

bot = telebot.TeleBot(TOKEN)

# قاعدة بيانات بسيطة
users_data = {} # {user_id: {'points': 0, 'last_gift': None}}
subscribers = set() # قائمة اليوزرات لإرسال الإشعارات لهم
last_video_link = None # لتجنب تكرار إرسال نفس الفيديو

def get_user(user_id):
    if user_id not in users_data:
        users_data[user_id] = {'points': 0, 'last_gift': None}
    return users_data[user_id]

# --- وظيفة فحص اليوتيوب التلقائي ---
def check_youtube():
    global last_video_link
    while True:
        try:
            feed = feedparser.parse(YOUTUBE_RSS_URL)
            if feed.entries:
                latest_video = feed.entries[0]
                video_link = latest_video.link
                video_title = latest_video.title

                # إذا كان الفيديو جديداً وغير مرسل سابقاً
                if last_video_link != video_link:
                    last_video_link = video_link
                    message_text = f"🚨 **فيديو جديد من باونتي راش!**\n\n🎬 العنوان: {video_title}\n🔗 الرابط: {video_link}"
                    
                    # إرسال لكل المشتركين
                    for user_id in list(subscribers):
                        try:
                            bot.send_message(user_id, message_text, parse_mode="Markdown")
                        except:
                            pass # في حال قام المستخدم بحظر البوت
            
        except Exception as e:
            print(f"Error checking YouTube: {e}")
            
        time.sleep(300) # الانتظار 5 دقائق (300 ثانية)

# تشغيل الفحص في خلفية البرنامج (Thread) لكي لا يتوقف البوت
threading.Thread(target=check_youtube, daemon=True).start()

# --- الأوامر الرئيسية ---

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    get_user(user_id)
    subscribers.add(user_id) # إضافة المستخدم لقائمة الإشعارات
    
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("🎁 هدية يومية", "💰 نقاطي", "🛒 متجر الحسابات", "📺 آخر فيديو")
    bot.send_message(message.chat.id, "أهلاً بك! تم تفعيل إشعارات باونتي راش التلقائية (كل 5 دقائق) ✅", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🎁 هدية يومية")
def daily_gift(message):
    user = get_user(message.from_user.id)
    now = datetime.now()
    if user['last_gift'] and now - user['last_gift'] < timedelta(days=1):
        bot.reply_to(message, "❌ استلمت هديتك اليوم، عد غداً!")
    else:
        user['points'] += 5
        user['last_gift'] = now
        bot.reply_to(message, f"✅ مبروك! حصلت على 5 نقاط. نقاطك الآن: {user['points']}")

@bot.message_handler(func=lambda m: m.text == "💰 نقاطي")
def my_points(message):
    user = get_user(message.from_user.id)
    bot.reply_to(message, f"📊 نقاطك الحالية: {user['points']}")

@bot.message_handler(func=lambda m: m.text == "🛒 متجر الحسابات")
def store(message):
    user = get_user(message.from_user.id)
    if user['points'] < 10:
        bot.reply_to(message, "⚠️ تحتاج 10 نقاط لشراء حساب باونتي عشوائي!")
    else:
        user['points'] -= 10
        bot.reply_to(message, "✅ تم الشراء! الحساب: random_acc_1@bounty.com | الباسورد: 998877")

@bot.message_handler(func=lambda m: m.text == "📺 آخر فيديو")
def manual_check(message):
    feed = feedparser.parse(YOUTUBE_RSS_URL)
    if feed.entries:
        bot.reply_to(message, f"📺 آخر فيديو متوفر:\n{feed.entries[0].link}")

print("البوت يعمل ويفحص اليوتيوب كل 5 دقائق... 🚀")
bot.infinity_polling()
