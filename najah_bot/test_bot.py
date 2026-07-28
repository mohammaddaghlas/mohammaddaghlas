#!/usr/bin/env python3
"""
نموذج اختبار لبوت جامعة النجاح
يمكن استخدامه لاختبار الوظائف دون الاتصال بـ Telegram
"""

import sqlite3
import sys
from datetime import datetime

DB_PATH = 'najah_bot.db'


def test_database():
    """اختبار وظائف قاعدة البيانات"""
    print("🧪 اختبار قاعدة البيانات...\n")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # التحقق من وجود الجداول
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print("✅ الجداول الموجودة:")
    for table in tables:
        print(f"   - {table[0]}")
    
    # عرض هيكل جدول المشتركين
    print("\n📋 هيكل جدول subscribers:")
    cursor.execute("PRAGMA table_info(subscribers)")
    for column in cursor.fetchall():
        print(f"   - {column[1]} ({column[2]})")
    
    # عرض هيكل جدول الإعلانات
    print("\n📋 هيكل جدول sent_announcements:")
    cursor.execute("PRAGMA table_info(sent_announcements)")
    for column in cursor.fetchall():
        print(f"   - {column[1]} ({column[2]})")
    
    # عرض إحصائيات
    cursor.execute("SELECT COUNT(*) FROM subscribers WHERE is_active = 1")
    active_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM sent_announcements")
    announcements_count = cursor.fetchone()[0]
    
    print(f"\n📊 الإحصائيات:")
    print(f"   - المشتركين النشطين: {active_count}")
    print(f"   - الإعلانات المرسلة: {announcements_count}")
    
    conn.close()
    print("\n✅ اكتمل اختبار قاعدة البيانات بنجاح!")


def test_keyword_detection():
    """اختبار كشف الكلمات المفتاحية"""
    print("\n" + "="*50)
    print("🧪 اختبار كشف الكلمات المفتاحية...\n")
    
    HOLIDAY_KEYWORDS = [
        'عطلة', 'تعطيل', 'تعليق', 'دوام', 'إغلاق',
        'holiday', 'vacation', 'suspended', 'closed'
    ]
    
    test_cases = [
        ("تعطيل الدراسة يوم الخميس", True),
        ("عطلة رسمية بمناسبة عيد الأضحى", True),
        ("تعليق الدوام بسبب الأحوال الجوية", True),
        ("إغلاق المكتبة المركزية", True),
        ("امتحان منتصف الفصل", False),
        ("ورشة عمل حول البرمجة", False),
        ("Holiday due to weather", True),
        ("Classes suspended tomorrow", True),
        ("محاضرة إضافية", False),
    ]
    
    passed = 0
    failed = 0
    
    for text, expected in test_cases:
        detected = any(keyword.lower() in text.lower() for keyword in HOLIDAY_KEYWORDS)
        status = "✅" if detected == expected else "❌"
        
        if detected == expected:
            passed += 1
        else:
            failed += 1
        
        print(f"{status} '{text}'")
        print(f"   المتوقع: {expected}, النتيجة: {detected}\n")
    
    print(f"📊 النتائج: {passed} ناجح، {failed} فاشل")
    print("✅ اكتمل اختبار كشف الكلمات المفتاحية!")


def simulate_news_check():
    """محاكاة فحص الأخبار"""
    print("\n" + "="*50)
    print("🧪 محاكاة فحص الأخبار...\n")
    
    sample_news = [
        {
            'title': 'تعطيل الدراسة يوم الخميس الموافق 15 فبراير',
            'content': 'تعلن جامعة النجاح عن تعطيل الدراسة يوم الخميس...',
            'url': 'https://www.najah.edu/ar/news/12345'
        },
        {
            'title': 'ورشة عمل حول الذكاء الاصطناعي',
            'content': 'تنظم كلية الهندسة ورشة عمل...',
            'url': 'https://www.najah.edu/ar/news/12346'
        },
        {
            'title': 'تعليق الدوام بسبب الأحوال الجوية',
            'content': 'بسبب العاصفة الثلجية المتوقعة...',
            'url': 'https://www.najah.edu/ar/news/12347'
        }
    ]
    
    HOLIDAY_KEYWORDS = [
        'عطلة', 'تعطيل', 'تعليق', 'دوام', 'إغلاق',
        'holiday', 'vacation', 'suspended', 'closed'
    ]
    
    print("الأخبار التي سيتم إرسالها:\n")
    
    for i, news in enumerate(sample_news, 1):
        is_holiday = any(
            keyword.lower() in f"{news['title']} {news['content']}".lower()
            for keyword in HOLIDAY_KEYWORDS
        )
        
        if is_holiday:
            print(f"{i}. 🚨 {news['title']}")
            print(f"   الرابط: {news['url']}")
            print(f"   الحالة: سيتم الإرسال ✅\n")
        else:
            print(f"{i}. 📰 {news['title']}")
            print(f"   الحالة: لن يتم الإرسال ❌\n")
    
    print("✅ اكتملت المحاكاة!")


def main():
    """الدالة الرئيسية للاختبار"""
    print("="*50)
    print("🎓 نظام اختبار بوت جامعة النجاح")
    print("="*50)
    
    if len(sys.argv) > 1:
        choice = sys.argv[1]
        
        if choice == 'db':
            test_database()
        elif choice == 'keywords':
            test_keyword_detection()
        elif choice == 'simulate':
            simulate_news_check()
        else:
            print(f"خيار غير معروف: {choice}")
            print("الخيارات المتاحة: db, keywords, simulate")
    else:
        # تشغيل جميع الاختبارات
        test_database()
        test_keyword_detection()
        simulate_news_check()
        
        print("\n" + "="*50)
        print("✅ اكتملت جميع الاختبارات بنجاح!")
        print("="*50)


if __name__ == '__main__':
    main()
