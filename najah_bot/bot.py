#!/usr/bin/env python3
"""
Telegram Bot لطلاب جامعة النجاح
يسجل المشتركين ويراقب أخبار الجامعة كل 5 دقائق
ويرسل إشعارات عند وجود عطلة أو تعليق دوام
"""

import sqlite3
import asyncio
import logging
from datetime import datetime
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes
import aiohttp

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ثوابت
DB_PATH = 'najah_bot.db'
CHECK_INTERVAL = 300  # 5 دقائق بالثواني
NAJAH_NEWS_URL = 'https://www.najah.edu/ar/news'  # رابط أخبار جامعة النجاح

# كلمات مفتاحية للدلالة على عطلة أو تعليق دوام
HOLIDAY_KEYWORDS = [
    'عطلة', 'تعطيل', 'تعليق', 'دوام', 'إغلاق', 
    'holiday', 'vacation', 'suspended', 'closed'
]


class Database:
    """إدارة قاعدة البيانات SQLite"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """إنشاء الجداول المطلوبة"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # جدول المشتركين
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subscribers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER UNIQUE NOT NULL,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # جدول الإعلانات المرسلة
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sent_announcements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT,
                url TEXT,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("تم تهيئة قاعدة البيانات بنجاح")
    
    def add_subscriber(self, chat_id: int, username: str, first_name: str, last_name: str = None) -> bool:
        """إضافة مشترك جديد"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO subscribers 
                (chat_id, username, first_name, last_name, subscribed_at, is_active)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, 1)
            ''', (chat_id, username, first_name, last_name))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"خطأ في إضافة المشترك: {e}")
            return False
    
    def remove_subscriber(self, chat_id: int) -> bool:
        """إزالة مشترك"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('UPDATE subscribers SET is_active = 0 WHERE chat_id = ?', (chat_id,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"خطأ في إزالة المشترك: {e}")
            return False
    
    def get_active_subscribers(self) -> list:
        """الحصول على قائمة المشتركين النشطين"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT chat_id FROM subscribers WHERE is_active = 1')
            subscribers = [row[0] for row in cursor.fetchall()]
            
            conn.close()
            return subscribers
        except Exception as e:
            logger.error(f"خطأ في جلب المشتركين: {e}")
            return []
    
    def is_announcement_sent(self, title: str) -> bool:
        """التحقق مما إذا كان الإعلان قد أُرسل من قبل"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM sent_announcements WHERE title = ?', (title,))
            count = cursor.fetchone()[0]
            
            conn.close()
            return count > 0
        except Exception as e:
            logger.error(f"خطأ في التحقق من الإعلان: {e}")
            return False
    
    def mark_announcement_sent(self, title: str, content: str, url: str):
        """تسجيل إعلان كمرسل"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO sent_announcements (title, content, url)
                VALUES (?, ?, ?)
            ''', (title, content, url))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"خطأ في تسجيل الإعلان: {e}")


class NajahNewsMonitor:
    """مراقبة أخبار جامعة النجاح"""
    
    def __init__(self):
        self.session = None
    
    async def start_session(self):
        """بدء جلسة HTTP"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
    
    async def close_session(self):
        """إغلاق جلسة HTTP"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def fetch_news(self) -> list:
        """جلب الأخبار من موقع الجامعة"""
        news_items = []
        
        try:
            # ملاحظة: هذا مثال، في الواقع قد تحتاج لاستخدام RSS أو API رسمي
            # هنا نستخدم scraping بسيط كمثال
            async with self.session.get(NAJAH_NEWS_URL) as response:
                if response.status == 200:
                    html = await response.text()
                    # تحليل HTML لاستخراج الأخبار (مثال مبسط)
                    # في التطبيق الحقيقي ستحتاج لاستخدام BeautifulSoup أو similar
                    news_items = self.parse_news(html)
        except Exception as e:
            logger.error(f"خطأ في جلب الأخبار: {e}")
        
        return news_items
    
    def parse_news(self, html: str) -> list:
        """تحليل HTML لاستخراج الأخبار"""
        # هذا مثال مبسط - في الواقع ستحتاج لتحليل فعلي للـ HTML
        # يمكنك استخدام BeautifulSoup هنا
        news_items = []
        
        # مثال افتراضي للأخبار
        # في التطبيق الحقيقي، استبدل هذا بتحليل فعلي
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            
            # ابحث عن عناصر الأخبار (تعديل حسب هيكل موقع النجاح الفعلي)
            news_elements = soup.find_all('article', limit=10)
            
            for element in news_elements:
                title_elem = element.find('h2') or element.find('h3')
                link_elem = element.find('a')
                
                if title_elem and link_elem:
                    title = title_elem.get_text(strip=True)
                    link = link_elem.get('href', '')
                    if not link.startswith('http'):
                        link = f'https://www.najah.edu{link}'
                    
                    news_items.append({
                        'title': title,
                        'content': element.get_text(strip=True)[:200],
                        'url': link
                    })
        except ImportError:
            logger.warning("BeautifulSoup غير مثبت، استخدام طريقة بديلة")
            # طريقة بديلة بدون BeautifulSoup
            pass
        except Exception as e:
            logger.error(f"خطأ في تحليل الأخبار: {e}")
        
        return news_items
    
    def is_holiday_announcement(self, title: str, content: str) -> bool:
        """التحقق مما إذا كان الإعلان عن عطلة أو تعليق دوام"""
        text = f"{title} {content}".lower()
        return any(keyword.lower() in text for keyword in HOLIDAY_KEYWORDS)


class NajahBot:
    """بوت تليجرام الرئيسي"""
    
    def __init__(self, token: str):
        self.token = token
        self.db = Database(DB_PATH)
        self.monitor = NajahNewsMonitor()
        self.application = None
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /start command"""
        user = update.effective_user
        chat_id = update.effective_chat.id
        
        self.db.add_subscriber(
            chat_id=chat_id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )
        
        welcome_message = f"""
🎓 مرحبًا {user.first_name}!

أهلاً بك في بوت جامعة النجاح للإشعارات.

سأقوم بإعلامك فورًا عند وجود:
• عطلة رسمية
• تعليق دوام
• أي إعلان مهم من الجامعة

استخدم الأوامر التالية:
/help - لعرض المساعدة
/unsubscribe - لإلغاء الاشتراك
/status - لعرض حالة اشتراكك

تم تسجيلك بنجاح! ✅
        """
        
        await update.message.reply_text(welcome_message)
        logger.info(f"مشترك جديد: {user.first_name} ({chat_id})")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /help command"""
        help_message = """
📚 مساعدة بوت جامعة النجاح

الأوامر المتاحة:
/start - البدء واستخدام البوت
/help - عرض هذه الرسالة
/unsubscribe - إلغاء الاشتراك
/status - عرض حالة الاشتراك

البوت يراقب أخبار جامعة النجاح كل 5 دقائق
ويرسلك إشعارات فورية عند وجود عطلة أو تعليق دوام.

للدعم والتواصل: @najah_support
        """
        await update.message.reply_text(help_message)
    
    async def unsubscribe_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /unsubscribe command"""
        chat_id = update.effective_chat.id
        self.db.remove_subscriber(chat_id)
        
        await update.message.reply_text(
            "❌ تم إلغاء اشتراكك بنجاح.\n"
            "يمكنك العودة للاشتراك في أي وقت باستخدام /start"
        )
        logger.info(f"تم إلغاء اشتراك: {chat_id}")
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /status command"""
        chat_id = update.effective_chat.id
        
        # تحقق من حالة المشترك
        subscribers = self.db.get_active_subscribers()
        is_subscribed = chat_id in subscribers
        
        if is_subscribed:
            status_message = "✅ أنت مشترك حاليًا في خدمة الإشعارات."
        else:
            status_message = "❌ لست مشتركًا حاليًا.\nاستخدم /start للاشتراك."
        
        total_subscribers = len(subscribers)
        status_message += f"\n\n📊 إجمالي المشتركين: {total_subscribers}"
        
        await update.message.reply_text(status_message)
    
    async def check_news_periodically(self, context: ContextTypes.DEFAULT_TYPE):
        """فحص الأخبار بشكل دوري"""
        logger.info("جاري فحص أخبار جامعة النجاح...")
        
        try:
            news_items = await self.monitor.fetch_news()
            
            for news in news_items:
                if self.monitor.is_holiday_announcement(news['title'], news.get('content', '')):
                    if not self.db.is_announcement_sent(news['title']):
                        await self.send_announcement(news)
                        self.db.mark_announcement_sent(
                            news['title'],
                            news.get('content', ''),
                            news['url']
                        )
                        logger.info(f"تم إرسال إعلان: {news['title']}")
        except Exception as e:
            logger.error(f"خطأ في فحص الأخبار: {e}")
    
    async def send_announcement(self, news: dict):
        """إرسال إعلان لجميع المشتركين"""
        subscribers = self.db.get_active_subscribers()
        
        message = f"""
🚨 إعلان عاجل من جامعة النجاح

📌 العنوان: {news['title']}

{news.get('content', '')}

🔗 للمزيد: {news['url']}

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}
        """
        
        bot = Bot(token=self.token)
        
        for chat_id in subscribers:
            try:
                await bot.send_message(
                    chat_id=chat_id,
                    text=message,
                    parse_mode='HTML'
                )
                await asyncio.sleep(0.1)  # تجنب rate limiting
            except Exception as e:
                logger.error(f"خطأ في إرسال الإعلان إلى {chat_id}: {e}")
    
    async def post_init(self, application):
        """تهيئة بعد بدء التطبيق"""
        await self.monitor.start_session()
        logger.info("تم بدء مراقبة الأخبار")
    
    async def post_shutdown(self, application):
        """تنظيف عند الإيقاف"""
        await self.monitor.close_session()
        logger.info("تم إيقاف مراقبة الأخبار")
    
    def run(self):
        """تشغيل البوت"""
        # إنشاء التطبيق
        self.application = Application.builder().token(self.token).build()
        
        # إضافة معالجات الأوامر
        self.application.add_handler(CommandHandler('start', self.start_command))
        self.application.add_handler(CommandHandler('help', self.help_command))
        self.application.add_handler(CommandHandler('unsubscribe', self.unsubscribe_command))
        self.application.add_handler(CommandHandler('status', self.status_command))
        
        # إضافة وظيفة الفحص الدوري
        self.application.job_queue.run_repeating(
            self.check_news_periodically,
            interval=CHECK_INTERVAL,
            first=10  # ابدأ بعد 10 ثواني
        )
        
        # إعداد دوال التهيئة والتنظيف
        self.application.post_init = self.post_init
        self.application.post_shutdown = self.post_shutdown
        
        logger.info("جاري تشغيل البوت...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)


def main():
    """الدالة الرئيسية"""
    import os
    
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        print("❌ خطأ: يرجى设置 متغير البيئة TELEGRAM_BOT_TOKEN")
        print("مثال: export TELEGRAM_BOT_TOKEN='your_bot_token_here'")
        return
    
    bot = NajahBot(token)
    bot.run()


if __name__ == '__main__':
    main()
