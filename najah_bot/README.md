# 🎓 بوت جامعة النجاح للإشعارات

بوت تليجرام لطلاب جامعة النجاح يراقب أخبار الجامعة ويرسل إشعارات فورية عند وجود عطلة أو تعليق دوام.

## ✨ المميزات

- تسجيل المشتركين وحفظهم في قاعدة بيانات SQLite
- مراقبة أخبار جامعة النجاح كل 5 دقائق تلقائيًا
- كشف الإعلانات المتعلقة بالعطلات وتعليق الدوام باستخدام كلمات مفتاحية
- إرسال إشعارات فورية لجميع المشتركين
- منع تكرار إرسال نفس الإعلان
- واجهة عربية كاملة مع أوامر سهلة

## 📋 المتطلبات

- Python 3.8+
- Token من Telegram Bot (من @BotFather)

## 🚀 التثبيت

### 1. استنساخ المشروع

```bash
cd najah_bot
```

### 2. تثبيت المكتبات المطلوبة

```bash
pip install -r requirements.txt
```

### 3. إعداد Token البوت

احصل على Token من @BotFather في تليجرام، ثم:

```bash
export TELEGRAM_BOT_TOKEN='your_token_here'
```

أو على Windows:

```cmd
set TELEGRAM_BOT_TOKEN=your_token_here
```

## 🎯 التشغيل

```bash
python bot.py
```

## 📱 الأوامر المتاحة

| الأمر | الوصف |
|-------|-------|
| `/start` | البدء وتسجيل المشترك |
| `/help` | عرض رسالة المساعدة |
| `/unsubscribe` | إلغاء الاشتراك |
| `/status` | عرض حالة الاشتراك وعدد المشتركين |

## 🗄️ قاعدة البيانات

يستخدم البوت قاعدة بيانات SQLite (`najah_bot.db`) تحتوي على:

### جدول المشتركين (subscribers)
- `chat_id`: معرف المستخدم في تليجرام
- `username`: اسم المستخدم
- `first_name`: الاسم الأول
- `last_name`: اسم العائلة
- `subscribed_at`: تاريخ الاشتراك
- `is_active`: حالة الاشتراك

### جدول الإعلانات المرسلة (sent_announcements)
- `title`: عنوان الإعلان
- `content`: محتوى الإعلان
- `url`: رابط الإعلان
- `sent_at`: تاريخ الإرسال

## ⚙️ التكوين

يمكن تعديل الثوابت التالية في `bot.py`:

```python
DB_PATH = 'najah_bot.db'              # مسار قاعدة البيانات
CHECK_INTERVAL = 300                   # فترة الفحص بالثواني (5 دقائق)
NAJAH_NEWS_URL = 'https://www.najah.edu/ar/news'  # رابط الأخبار
```

## 🔍 كيفية عمل كشف العطلات

يستخدم البوت قائمة من الكلمات المفتاحية للكشف عن الإعلانات المهمة:

```python
HOLIDAY_KEYWORDS = [
    'عطلة', 'تعطيل', 'تعليق', 'دوام', 'إغلاق',
    'holiday', 'vacation', 'suspended', 'closed'
]
```

إذا احتوى عنوان أو محتوى الخبر على أي من هذه الكلمات، سيتم إرساله للمشتركين.

## 📝 ملاحظات هامة

1. **موقع الجامعة**: قد يحتاج كود الـ scraping للتحديث حسب هيكل موقع جامعة النجاح الفعلي
2. **Rate Limiting**: البوت ينتظر 0.1 ثانية بين كل رسالة لتجنب حظر Telegram
3. **الإعلانات المكررة**: يتم تخزين الإعلانات المرسلة لمنع التكرار

## 🛠️ التطوير

### إضافة مصادر أخبار إضافية

```python
# في class NajahNewsMonitor
async def fetch_news(self) -> list:
    news_items = []
    
    # مصدر 1: موقع الجامعة
    news_items.extend(await self.fetch_from_website())
    
    # مصدر 2: RSS Feed (إذا توفر)
    news_items.extend(await self.fetch_from_rss())
    
    return news_items
```

### تحسين كشف العطلات

يمكن استخدام معالجة لغة طبيعية (NLP) لتحسين دقة الكشف:

```python
from transformers import pipeline

classifier = pipeline("text-classification", model="...")

def is_holiday_announcement(self, title: str, content: str) -> bool:
    text = f"{title} {content}"
    result = classifier(text)
    return result[0]['label'] == 'HOLIDAY'
```

## 📞 الدعم

للدعم الفني أو الإبلاغ عن مشاكل، يرجى التواصل عبر:
- Email: support@najah.edu
- Telegram: @najah_support

## 📄 الترخيص

هذا المشروع مفتوح المصدر للاستخدام التعليمي.

---

**جامعة النجاح الوطنية** - نابلس، فلسطين 🇵🇸
