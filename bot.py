import telebot
import feedparser
import time
import threading
from datetime import datetime, timedelta

# --- الإعدادات ---
TOKEN = '8686210830:AAGZmXopHLTELnyszWr7wsyhouPmr74vVjk' 
YOUTUBE_RSS_URL = 'https://youtube.com' # تأكد من وضع رابط RSS الصحيح للقناة

# إضافة logger لمراقبة الأخطاء
bot = telebot.TeleBot(TOKEN)

# --- حذف أي Webhook قديم قبل البدء لمنع التعارض 409 ---
bot.remove_webhook()

users_data = {} 
subscribers = set() 
last_video_link = None 

def get_user(user_id):
    if user_id not in users_data:
        users_data[user_id] = {'points': 0, 'last_gift': None}
    return users_data[user_id]

def check_youtube():
    global last_video_link
    while True:
        try:
            feed = feedparser.parse(YOUTUBE_RSS_URL)
            if feed.entries:
                latest_video = feed.entries[0]
                video_link = latest_video.link
                video_title = latest_video.title

                if last_video_link != video_link:
                    last_video_link = video_link
                    message_text = f"🚨 **فيديو جديد من باونتي راش!**\n\n🎬 العنوان: {video_title}\n🔗 الرابط: {video_link}"
                    
                    for user_id in list(subscribers):
                        try:
                            bot.send_message(user_id, message_text, parse_mode="Markdown")
                        except:
                            pass 
            
        except Exception as e:
            print(f"Error checking YouTube: {e}")
            
        time.sleep(300) 

threading.Thread(target=check_youtube, daemon=True).start()

# الأوامر (نفس الأوامر السابقة بدون تغيير)
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    get_user(user_id)
    subscribers.add(user_id)
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("🎁 هدية يومية", "💰 نقاطي", "🛒 متجر الحسابات", "📺 آخر فيديو")
    bot.send_message(message.chat.id, "أهلاً بك! تم تفعيل الإشعارات ✅", reply_markup=markup)

# ... (باقي الأوامر تبقى كما هي في كودك) ...

print("البوت يعمل بنظام الحماية من التضارب... 🚀")

# التعديل الأهم هنا: skip_pending=True يتجاهل أي طلبات قديمة تسبب التعارض
bot.infinity_polling(skip_pending=True)
