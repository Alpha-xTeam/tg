# بوت تحميل من يوتيوب، تيك توك، وإنستقرام

بوت تيليجرام متقدم لتحميل المحتوى من منصات التواصل الاجتماعي المختلفة مع دعم الرفع إلى Supabase وإدارة المستخدمين والإحصائيات.

## ✨ المميزات

- **تحميل من يوتيوب**: فيديو وصوت بجودات متعددة
- **تحميل من تيك توك**: فيديوهات، صور، وعروض شرائية (Slideshow)
- **تحميل من إنستقرام**: منشورات، ريلز، وقوالب متعددة الصور
- **دعم الكوكيز**: تحميل الكوكيز تلقائيًا من Supabase لتجاوز الحظر
- **الرفع إلى التخزين السحابي**: رفع الملفات المحملة إلى Supabase Storage
- **إدارة المستخدمين**: tracking للمستخدمين الجدد والمتكررين
- **إدارة الإحصائيات**: عد عمليات التحميل لكل خدمة
- **قناة إجبارية للتحديث**: خاصية الإشتراك الإجباري في قناة تيليجرام
- **لوحة تحكم إدارية**: عبر المتغيرات البيئية
- **دعم الوكيل (Proxy)**: لتجاوز الحظر الجغرافي

## 📋 المتطلبات

- Python 3.7+
- حساب Supabase
- توكن بوت تيليجرام
- متغيرات بيئية محددة (انظر أدناه)

## 🛠️ التثبيت

1. استنساخ المستودع:
```bash
git clone <repository-url>
cd telegram-bot
```

2. تثبيت المتطلبات:
```bash
pip install -r requirements.txt
```

3. إنشاء ملف `.env` في الجذر وإضافة المتغيرات التالية:
```env
TELEGRAM_TOKEN=your_telegram_bot_token
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
YOUTUBE_API_KEY=your_youtube_data_api_key_v3
ADMIN_ID=your_telegram_user_id
PROXY_URL=http://your_proxy_server:port  # اختياري
```

## 🔧 المتغيرات البيئية

| المتغير | الوصف | مطلوب |
|--------|-------|--------|
| `TELEGRAM_TOKEN` | توكن بوت تيليجرام من @BotFather | نعم |
| `SUPABASE_URL` | رابط مشروع Supabase | نعم |
| `SUPABASE_KEY` | مفتاح anon لمشروع Supabase | نعم |
| `YOUTUBE_API_KEY` | مفتاح بيانات يوتيوب API v3 | نعم (لجلب المعلومات عبر API) |
| `ADMIN_ID` | معرف المستخدم الإداري في تيليجرام | نعم |
| `PROXY_URL` | عنوان الوكيل HTTP/HTTPS (اختياري) | لا |

## 🗄️ إعداد قاعدة البيانات

يحتاج البوت إلى جدولين في قاعدة بيانات Supabase:

### جدول `config`
```sql
create table config (
  id integer primary key,
  channel_id text,
  is_force_sub boolean,
  blocked_users text[],
  youtube_downloads integer default 0,
  tiktok_downloads integer default 0,
  instagram_downloads integer default 0
);

-- إدخال القيم الافتراضية
insert into config (id, channel_id, is_force_sub, blocked_users) 
values (1, '@your_channel', false, '{}');
```

### جدول `users`
```sql
create table users (
  user_id bigint primary key,
  first_name text,
  username text,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);
```

## ▶️ التشغيل

```bash
python bot.py
```

سيظهر في الطرفية رسائل تفيد باتصال البوت وتحديث الكوكيز.

## 📁 структура المشروع

```
telegram-bot/
│
├── bot.py              # ملف البوت الرئيسي
├── requirements.txt    # قائمة المتطلبات
├── README.md           # هذا الملف
├── test.py             # ملفات اختبار (للاختبار والتطوير)
├── test_regex.py
└── test_full.py
```

## ⚙️ كيف يعمل البوت

1. عند بدء التشغيل:
   - تحميل المتغيرات البيئية
   - تحديث الكوكيز من Supabase storage
   - تهيئة اتصال Supabase
   - إنشاء مجلد التحميل (`/tmp/downloads`)

2. عند استلام رسالة:
   - فحص ما إذا كان المستخدم مشترك في القناة الإجبارية (إذا كانت مفعلة)
   - إضافة/تحديث المستخدم في قاعدة البيانات
   - تحليل الرابط لتحديد المنصة
   - تحميل المحتوى باستخدام الطريقة المناسبة
   - رفع الملف إلى Supabase وإرسال الرابط للمستخدم
   - زيادة الإحصائيات الخاصة بالمنصة

## 🔐 الأمان والخصوصية

- لا يتم تخزين أي بيانات حساسة للمستخدمين кроме معرّف تيليجرام والاسم
- يتم حذف الملفات المحملة محليًا بعد الرفع إلى Supabase (بشكل غير مباشر عبر استخدام `/tmp`)
- الكوكيز يتم تحديثها من مصدر موثوق (Supabase) ولا تُشارك مع أطراف ثالثة

## 🤝 المساهمة

مساهماتكم مرحب بها! يرجى:
1. Fork المستودع
2. إنشاء فرع لميزة أو إصلاح (`git checkout -b feature/amazing-feature`)
3. commit التغييرات (`git commit -m 'Add amazing feature'`)
4. push إلى الفرع (`git push origin feature/amazing-feature`)
5. فتح Pull Request

## 📄 الترخيص

هذا المشروع مرخص تحت ترخيص MIT - انظر ملف [LICENSE](LICNACE) للمزيد من التفاصيل.

---

تم التطوير بـ ❤️ باستخدام Python ومكتباتTeleBot, yt-dlp, وinstaloader