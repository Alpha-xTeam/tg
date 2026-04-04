# استيراد مكتبة TeleBot لإنشاء بوت تيليجرام
import telebot

# استيراد مكتبة os للتعامل مع الملفات والمجلدات
import os

# استيراد مكتبة re لمعالجة النصوص (Regex)
import re

# استيراد مكتبة json للتعامل مع ملفات الإعدادات
import json

# استيراد مكتبة dotenv لتحميل المتغيرات البيئية
from dotenv import load_dotenv
load_dotenv()

# استيراد مكتبة supabase للتعامل مع قاعدة البيانات
try:
    from supabase import create_client, Client
except ImportError:
    # في حالة فشل تثبيت مكتبة supabase الكاملة، نستخدم المكونات الأساسية
    from postgrest import PostgrestClient
    from storage3 import StorageClient
    
    class Client:
        def __init__(self, url, key):
            self.table = lambda name: PostgrestClient(f"{url}/rest/v1", headers={"apikey": key, "Authorization": f"Bearer {key}"}).table(name)
            self.storage = StorageClient(f"{url}/storage/v1", headers={"apikey": key, "Authorization": f"Bearer {key}"})
    
    def create_client(url, key):
        return Client(url, key)

# استيراد مكتبة yt-dlp لتحميل الفيديوهات
import yt_dlp
import requests

# إعدادات yt-dlp المتقدمة (مستوحاة من youtube-downloader-api)
YTDL_COMMON_PARAMS = {
    'quiet': True,
    'no_warnings': True,
    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
    'cookiefile': 'cookies.txt', # إضافة ملف الكوكيز لمحاكاة التصفح الحقيقي
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-us,en;q=0.5',
        'Referer': 'https://www.youtube.com/',
        'Origin': 'https://www.youtube.com',
        'Sec-Fetch-Mode': 'navigate',
    }
}

# مجلد حفظ الملفات المحملة
# نستخدم /tmp لدعم الاستضافات التي تملك نظام ملفات للقراءة فقط
OUTPUT = "/tmp/downloads"

# جلب ملف الكوكيز من رابط خارجي وتخزينه
COOKIES_FILE = "cookies.txt"
INSTA_COOKIES_FILE = "cookies2.txt"

def validate_and_fix_cookies(file_path):
    """تحقق من صلاحية ملف الكوكيز وإصلاح أي تنسيق مفقود"""
    if not os.path.exists(file_path):
        return False
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # التأكد من وجود الهيدر المطلوب لـ yt-dlp
        header = "# Netscape HTTP Cookie File"
        if lines and header not in lines[0]:
            lines.insert(0, f"{header}\n# This is a fixed file\n\n")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            return True
            
        # التحقق من وجود بيانات (على الأقل 4 أسطر مع الهيدر)
        return len(lines) > 3
    except Exception:
        return False

def update_cookies_from_url():
    # تحديث كوكيز يوتيوب
    if os.path.exists(COOKIES_FILE):
        if validate_and_fix_cookies(COOKIES_FILE):
            print(f"✅ YouTube cookies validated.")
        else:
            print(f"⚠️ YouTube cookies invalid.")
    
    # تحديث كوكيز انستا (cookies2.txt)
    if os.path.exists(INSTA_COOKIES_FILE):
        if validate_and_fix_cookies(INSTA_COOKIES_FILE):
            print(f"✅ Instagram cookies validated.")
    
    yt_url = "https://dkdxufqgmhigfhnkisdt.supabase.co/storage/v1/object/public/downloads/cookies.txt"
    insta_url = "https://dkdxufqgmhigfhnkisdt.supabase.co/storage/v1/object/public/downloads/cookies2.txt"
    
    try:
        import requests
        # تحميل كوكيز يوتيوب
        res1 = requests.get(yt_url, timeout=10)
        if res1.status_code == 200:
            with open(COOKIES_FILE, "wb") as f:
                f.write(res1.content)
            validate_and_fix_cookies(COOKIES_FILE)
            
        # تحميل كوكيز انستا
        res2 = requests.get(insta_url, timeout=10)
        if res2.status_code == 200:
            with open(INSTA_COOKIES_FILE, "wb") as f:
                f.write(res2.content)
            validate_and_fix_cookies(INSTA_COOKIES_FILE)
            print(f"✅ All cookies updated from Supabase.")
            return True
            
    except Exception as e:
        print(f"❌ Error downloading cookies: {e}")
    return False

# تشغيل تحديث الكوكيز عند بدء البوت
update_cookies_from_url()

# استيراد مكتبة instaloader لتحميل من إنستقرام
import instaloader
L = instaloader.Instaloader(
    dirname_pattern=OUTPUT,
    filename_pattern='{shortcode}',
    download_video_thumbnails=False,
    download_geotags=False,
    download_comments=False,
    save_metadata=False,
    compress_json=False
)

# توكن البوت
BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")

# إعدادات Supabase
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in Environment Variables")
    # محاولة التحميل من ملف .env يدوياً للتأكد في حال لم يتم تحميله تلقائياً
    from dotenv import load_dotenv
    load_dotenv()
    SUPABASE_URL = os.environ.get("SUPABASE_URL")
    SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# مفتاح YouTube API v3
YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")

# إعدادات الأدمن
ADMIN_ID = os.environ.get("ADMIN_ID")

if SUPABASE_URL and SUPABASE_KEY:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    print("❌ Failed to initialize Supabase client: Missing credentials.")
    supabase = None

# اسم الـ Bucket في Supabase
STORAGE_BUCKET = "downloads"

def delete_from_supabase(file_name):
    try:
        if not supabase: return
        res = supabase.storage.from_(STORAGE_BUCKET).remove([file_name])
        # التحقق مما إذا كان الحذف ناجحاً أو إذا كانت هناك أخطاء مخفية
        print(f"File {file_name} delete response: {res}")
    except Exception as e:
        print(f"Delete error: {e}")

def upload_to_supabase(file_path, file_name):
    try:
        with open(file_path, 'rb') as f:
            supabase.storage.from_(STORAGE_BUCKET).upload(
                path=file_name,
                file=f,
                file_options={"cache-control": "3600", "upsert": "true"}
            )
        # الحصول على رابط الملف العام
        # بناء الرابط العام لـ Supabase Storage: 
        # https://<project_id>.supabase.co/storage/v1/object/public/<bucket>/<file_name>
        res = f"{SUPABASE_URL}/storage/v1/object/public/{STORAGE_BUCKET}/{file_name}"
        return res
    except Exception as e:
        print(f"Upload error: {e}")
        return None

if not BOT_TOKEN:
    print("خطأ: لم يتم العثور على توكن البوت (TELEGRAM_TOKEN). تأكد من تعيينه كمتغير بيئي.")
    exit(1)

# الحد الأقصى لحجم الملف المسموح (50 ميجا)
MAX_SIZE = 50 * 1024 * 1024

# إعدادات الأدمن
ADMIN_ID = int(os.environ.get("ADMIN_ID", 949712684))

# إعدادات افتراضية
default_config = {
    "channel_id": "@your_channel", # يرجى تغيير هذا المعرف
    "is_force_sub": False,
    "blocked_users": []
}

def get_config():
    try:
        response = supabase.table("config").select("*").eq("id", 1).execute()
        if response.data:
            return response.data[0]
        return default_config
    except Exception as e:
        print(f"Error fetching config: {e}")
        return default_config

def update_config(new_config):
    try:
        supabase.table("config").update(new_config).eq("id", 1).execute()
    except Exception as e:
        print(f"Error updating config: {e}")

def increment_stat(stat_name):
    try:
        config = get_config()
        current_value = config.get(stat_name, 0)
        supabase.table("config").update({stat_name: current_value + 1}).eq("id", 1).execute()
    except Exception as e:
        print(f"Error incrementing {stat_name}: {e}")

def check_sub(user_id):
    config = get_config()
    if not config["is_force_sub"]:
        return True
    try:
        member = bot.get_chat_member(config["channel_id"], user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
        return False
    except:
        return True # في حال كان التوكن ليس أدمن في القناة


def add_user(user):
    try:
        # التحقق إذا كان المستخدم موجوداً مسبقاً
        response = supabase.table("users").select("*").eq("user_id", user.id).execute()
        is_new_user = len(response.data) == 0
        
        user_data = {
            "user_id": user.id,
            "first_name": user.first_name,
            "username": user.username
        }
        
        if is_new_user:
            supabase.table("users").insert(user_data).execute()
        else:
            supabase.table("users").update(user_data).eq("user_id", user.id).execute()
            
        return is_new_user
    except Exception as e:
        print(f"Error adding user: {e}")
        return False

def get_all_users():
    try:
        response = supabase.table("users").select("*").execute()
        return {str(u["user_id"]): u for u in response.data}
    except Exception as e:
        print(f"Error getting users: {e}")
        return {}

def get_users_list():
    try:
        response = supabase.table("users").select("user_id").execute()
        return [str(u["user_id"]) for u in response.data]
    except Exception as e:
        print(f"Error getting users list: {e}")
        return []


# إنشاء كائن البوت باستخدام التوكن
bot = telebot.TeleBot(BOT_TOKEN, threaded=True)

# تحسين إعدادات الاتصال لتجنب المهلة (Timeout)
from telebot import apihelper
apihelper.CONNECT_TIMEOUT = 60
apihelper.READ_TIMEOUT = 120

# إنشاء مجلد التحميل إذا لم يكن موجودًا
os.makedirs(OUTPUT, exist_ok=True)

# إعدادات البروكسي لتجاوز حظر يوتيوب (اختياري)
PROXY = os.environ.get("PROXY_URL")

# إعدادات الـ PO Token (لتجاوز حماية يوتيوب الجديدة)
# استخدم أداة youtube-po-token-generator للحصول على هذه القيم
YOUTUBE_PO_TOKEN = os.environ.get("YOUTUBE_PO_TOKEN") or "Mnh2rX_7fhZWq3aRVJo3KvnAfjdNqJMKfqOMvbicacVt-unCK9yqsIVuSsMxdEKRE6N9MzV21D_qu4mijjE-upKm2KnqESEOzTybDC5ZPCF47CDRFgsBJ-4TSJcpNblhy_u5U7KdowIXAzWrdyesvU_mzPGE4fHnW8Y="
YOUTUBE_VISITOR_DATA = os.environ.get("YOUTUBE_VISITOR_DATA") or "CgtFU2xQV3dicDI3MCikiL7OBjIKCgJJURIEGgAgXg%3D%3D"

# التحقق من صلاحية ملف الكوكيز
def validate_and_fix_cookies(cookie_file):
    if not os.path.exists(cookie_file):
        return False
    try:
        with open(cookie_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        valid_lines = []
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                valid_lines.append(line)
                continue
            parts = line.split('\t')
            if len(parts) >= 7:
                valid_lines.append(line)
            else:
                print(f"⚠️ Removing invalid cookie line: {line[:80]}...")
        if len(valid_lines) < len(lines):
            with open(cookie_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(valid_lines) + '\n')
            print(f"✅ Fixed cookies file: removed {len(lines) - len(valid_lines)} invalid lines")
        return any(not l.startswith('#') and l.strip() for l in valid_lines)
    except Exception as e:
        print(f"❌ Cookie validation error: {e}")
        return False

# قاموس لتتبع حالة كل مستخدم (رابط الفيديو المختار)
user_data = {}

# تتبع حالة الاشتراك (لتجنب تكرار إرسال رسالة للمطور)
user_subscription_notified = set()

# دالة جلب معلومات اليوتيوب باستخدام Google API كخيار أول
def get_yt_info_via_api(url):
    try:
        # استخراج الـ ID من الرابط
        import re
        video_id = None
        patterns = [r"v=([a-zA-Z0-9_-]+)", r"be/([a-zA-Z0-9_-]+)", r"shorts/([a-zA-Z0-9_-]+)"]
        for p in patterns:
            match = re.search(p, url)
            if match:
                video_id = match.group(1)
                break
        
        if not video_id: return None

        api_url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,contentDetails,statistics&id={video_id}&key={YOUTUBE_API_KEY}"
        response = requests.get(api_url, timeout=10)
        data = response.json()
        
        if "items" in data and len(data["items"]) > 0:
            item = data["items"][0]
            return {
                "title": item["snippet"]["title"],
                "thumbnail": item["snippet"]["thumbnails"]["high"]["url"],
                "id": video_id
            }
    except:
        pass
    return None

# دالة جلب معلومات اليوتيوب والجودات المتاحة
def get_yt_formats(url):
    # الطريقة الأولى: yt-dlp (الأكثر استقراراً وتحديثاً)
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True,
            'extract_flat': False,
            'skip_download': True,
        }

        # إضافة الكوكيز إن وجدت
        if os.path.exists(COOKIES_FILE):
            ydl_opts['cookiefile'] = COOKIES_FILE

        # إضافة البروكسي إن وجد
        if PROXY:
            ydl_opts['proxy'] = PROXY

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if not info:
                return None

            formats = []
            seen_resolutions = set()

            # جلب الفيديوهات progressive (صوت + صورة)
            for f in info.get('formats', []):
                if not f.get('vcodec') or not f.get('acodec') or f.get('acodec') == 'none':
                    continue

                resolution = f.get('resolution') or f"{f.get('height', '?')}p"
                ext = f.get('ext', 'mp4')
                filesize = f.get('filesize', 0) or 0

                # تجنب التكرار
                res_key = f"{resolution}_{ext}"
                if res_key in seen_resolutions:
                    continue
                seen_resolutions.add(res_key)

                formats.append({
                    'format_id': f"ydl_{f['format_id']}",
                    'resolution': resolution,
                    'ext': ext,
                    'filesize': filesize,
                    'actual_format_id': f['format_id']
                })

            # إذا لم توجد progressive، نستخدم best video + best audio merge
            if not formats:
                formats.append({
                    'format_id': 'ydl_best',
                    'resolution': 'Best Available',
                    'ext': 'mp4',
                    'filesize': 0,
                    'actual_format_id': 'bv*+ba/b'
                })

            return {
                'title': info.get('title', 'Video'),
                'thumbnail': info.get('thumbnail'),
                'formats': formats[:10],  # حد أقصى 10 جودات
                'method': 'yt-dlp'
            }
    except Exception as e:
        print(f"yt-dlp info fetch failed: {e}")

    # Fallback: Google API
    api_info = get_yt_info_via_api(url)
    if api_info:
        return {
            'title': api_info['title'],
            'thumbnail': api_info['thumbnail'],
            'formats': [{'format_id': 'default', 'resolution': 'High Quality', 'ext': 'mp4', 'filesize': 0}],
            'method': 'api'
        }

    return None

# دالة تحميل من يوتيوب باستخدام الجودة المختارة
def download_vd(url, format_id=None):
    try:
        ydl_opts = YTDL_COMMON_PARAMS.copy()
        ydl_opts.update({
            'outtmpl': f'{OUTPUT}/%(title)s_%(id)s.%(ext)s',
            'quiet': True,
            'no_warnings': True,
        })

        if PROXY:
            ydl_opts['proxy'] = PROXY

        # تحديد الجودة المطلوبة
        if format_id:
            if format_id.startswith('ydl_'):
                # استخدام format_id الحقيقي من yt-dlp
                actual_id = format_id.replace('ydl_', '')
                if actual_id in ('bv*+ba/b', 'best'):
                    ydl_opts['format'] = 'bv*+ba/b'
                else:
                    ydl_opts['format'] = actual_id
            else:
                # fallback: صيغة قديمة
                ydl_opts['format'] = format_id
        else:
            ydl_opts['format'] = 'bv*+ba/b'

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if not info:
                return None, None

            file_path = ydl.prepare_filename(info)
            # التعامل مع الملفات التي قد تغير امتدادها
            if not os.path.exists(file_path):
                base, _ = os.path.splitext(file_path)
                for ext in ['.mp4', '.mkv', '.webm', '.flv']:
                    if os.path.exists(base + ext):
                        file_path = base + ext
                        break

            if os.path.exists(file_path):
                safe_file_name = re.sub(r'[^a-zA-Z0-9._-]', '_', os.path.basename(file_path))
                upload_to_supabase(file_path, safe_file_name)
                return file_path, info.get('title', 'Video')

    except Exception as e:
        print(f"download_vd Error: {e}")

    return None, None

# دالة تحميل الصوت فقط من يوتيوب
def download_mp3(url):
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True,
            'format': 'bestaudio/best',
            'outtmpl': f'{OUTPUT}/%(title)s_%(id)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        if PROXY:
            ydl_opts['proxy'] = PROXY

        if os.path.exists(COOKIES_FILE):
            ydl_opts['cookiefile'] = COOKIES_FILE

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if not info:
                return None, None

            # yt-dlp مع FFmpegExtractAudio يحول الملف إلى mp3
            # اسم الملف قد يتغير بعد التحويل
            safe_title = re.sub(r'[\\/*?:"<>|]', "_", info.get('title', 'Audio'))
            expected_path = os.path.join(OUTPUT, f"{safe_title}.mp3")

            # البحث عن الملف الفعلي (yt-dlp قد يستخدم اسم مختلف قليلاً)
            if os.path.exists(expected_path):
                file_path = expected_path
            else:
                # البحث عن أي ملف mp3 في المجلد
                for f in os.listdir(OUTPUT):
                    if f.endswith('.mp3') and safe_title.split('_')[0] in f:
                        file_path = os.path.join(OUTPUT, f)
                        break
                else:
                    # fallback: استخدام prepare_filename
                    file_path = ydl.prepare_filename(info)
                    base, _ = os.path.splitext(file_path)
                    file_path = base + '.mp3'
                    if not os.path.exists(file_path):
                        return None, None

            safe_file_name = re.sub(r'[^a-zA-Z0-9._-]', '_', os.path.basename(file_path))
            upload_to_supabase(file_path, safe_file_name)
            return file_path, info.get('title', 'Audio')

    except Exception as e:
        print(f"download_mp3 Error: {e}")
        return None, None


# دالة تحميل صور تيك توك (yt-dlp لا يدعم روابط /photo/)
def download_tiktok_photos(url):
    try:
        # استخراج معرف الفيديو من الرابط
        match = re.search(r'/photo/(\d+)', url)
        if not match:
            return [], None

        video_id = match.group(1)
        safe_title = f"tiktok_photo_{video_id}"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.tiktok.com/',
            'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="121", "Google Chrome";v="121"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }

        # استخدام صفحة الـ Embed للحصول على بيانات الصور
        embed_url = f'https://www.tiktok.com/embed/v2/{video_id}'
        response = requests.get(embed_url, headers=headers, timeout=30, allow_redirects=True)

        # إذا فشل الـ embed أو المحتوى قليل، حاول الرابط الأصلي
        if response.status_code != 200 or len(response.text) < 10000:
            print(f"Embed page returned {response.status_code}, trying original URL...")
            response = requests.get(url, headers=headers, timeout=30, allow_redirects=True)

        html_content = response.text
        print(f"[DEBUG] Embed page length: {len(html_content)}")

        # استخراج روابط الصور من الصفحة
        import json
        image_urls = []

        # الطريقة 1: البحث عن روابط photomode-image في HTML
        raw_urls = re.findall(r'(https://p\d+-[\w.-]+\.tiktokcdn\.com[^\s"<>\\]+)', html_content)
        print(f"[DEBUG] Raw tiktokcdn URLs found: {len(raw_urls)}")

        # فلترة: نريد فقط صور الـ photomode (وليس الصور المصغرة أو الأفاتار)
        seen = set()
        for raw_url in raw_urls:
            # تنظيف الروابط من HTML entities
            clean_url = raw_url.replace('&amp;', '&').replace('\u0026', '&')

            # فقط صور الـ photomode
            if 'photomode-image' not in clean_url:
                continue

            # إزالة التكرار باستخدام الجزء الأساسي من الرابط (بدون معاملات CDN)
            id_match = re.search(r'/([a-f0-9]{32})~', clean_url)
            if id_match:
                img_id = id_match.group(1)
                if img_id in seen:
                    continue
                seen.add(img_id)
                image_urls.append(clean_url)

        print(f"[DEBUG] After photomode filtering: {len(image_urls)} images")

        # الطريقة 2: إذا لم نجد صور، حاول استخراج من __UNIVERSAL_DATA
        if not image_urls:
            uni_match = html_content.find('__UNIVERSAL_DATA_FOR_REHYDRATION__')
            if uni_match >= 0:
                tag_start = html_content.find('>', uni_match)
                tag_end = html_content.find('</script>', tag_start)
                if tag_start >= 0 and tag_end >= 0:
                    try:
                        data = json.loads(html_content[tag_start+1:tag_end])
                        # البحث عن image URLs في البيانات
                        def find_image_urls(obj, found=None, depth=0):
                            if found is None:
                                found = []
                            if depth > 15:
                                return found
                            if isinstance(obj, dict):
                                for key, value in obj.items():
                                    if key == 'imageURL' and isinstance(value, dict):
                                        url_list = value.get('urlList', [])
                                        if url_list:
                                            found.append(url_list[0])
                                    elif key == 'imageList' and isinstance(value, list):
                                        for item in value:
                                            if isinstance(item, dict):
                                                url_list = item.get('imageURL', {}).get('urlList', [])
                                                if url_list:
                                                    found.append(url_list[0])
                                    else:
                                        find_image_urls(value, found, depth+1)
                            elif isinstance(obj, list):
                                for item in obj:
                                    find_image_urls(item, found, depth+1)
                            return found

                        image_urls = find_image_urls(data)
                        print(f"Found {len(image_urls)} images from UNIVERSAL_DATA")
                    except:
                        pass

        # الطريقة 3: البحث عن أي روابط صور من tiktokcdn (بدون فلتر photomode)
        if not image_urls:
            all_cdn_urls = re.findall(r'(https://p\d+-[\w.-]+\.tiktokcdn\.com/[^\s"<>\\]+)', html_content)
            # فلترة الصور الكبيرة فقط (تجنب الصور المصغرة)
            for raw_url in all_cdn_urls:
                clean_url = raw_url.replace('&amp;', '&').replace('\u0026', '&')
                # تجنب صور الأفاتار والصور المصغرة
                if any(x in clean_url.lower() for x in ['avatar', 'cropcenter', 'thumbnail', 'favicon']):
                    continue
                # استخراج المعرف الفريد
                id_match = re.search(r'/([a-f0-9]{32})~', clean_url)
                if id_match:
                    img_id = id_match.group(1)
                    if img_id not in seen:
                        seen.add(img_id)
                        image_urls.append(clean_url)
            print(f"[DEBUG] After method 3 (broad CDN scan): {len(image_urls)} images")

        # الطريقة 4: استخدام cloudscraper كحل أخير
        if not image_urls:
            try:
                import cloudscraper
                scraper = cloudscraper.create_scraper()
                scrape_response = scraper.get(embed_url, timeout=30)
                if scrape_response.status_code == 200:
                    print(f"[DEBUG] cloudscraper page length: {len(scrape_response.text)}")
                    cloud_urls = re.findall(r'(https://p\d+-[\w.-]+\.tiktokcdn\.com/[^\s"<>\\]+)', scrape_response.text)
                    for raw_url in cloud_urls:
                        clean_url = raw_url.replace('&amp;', '&').replace('\u0026', '&')
                        if 'photomode-image' in clean_url or 'photomode' in clean_url:
                            id_match = re.search(r'/([a-f0-9]{32})~', clean_url)
                            if id_match:
                                img_id = id_match.group(1)
                                if img_id not in seen:
                                    seen.add(img_id)
                                    image_urls.append(clean_url)
                    print(f"[DEBUG] After cloudscraper: {len(image_urls)} images")
            except Exception as e:
                print(f"[DEBUG] cloudscraper failed: {e}")

        if not image_urls:
            print(f"TikTok Photo: No images found. Page length: {len(html_content)}, embed status: {response.status_code}")
            # Save HTML for debugging
            try:
                with open("/tmp/tiktok_debug.html", "w", encoding="utf-8") as f:
                    f.write(html_content[:5000])
                print("[DEBUG] Saved page snippet to /tmp/tiktok_debug.html")
            except:
                pass
            return [], None

        print(f"✅ Found {len(image_urls)} TikTok photos")

        # تحميل الصور
        files = []
        for idx, img_url in enumerate(image_urls[:20], 1):
            try:
                img_response = requests.get(img_url, headers=headers, timeout=30)
                if img_response.status_code == 200:
                    file_path = os.path.join(OUTPUT, f"{safe_title}_{idx}.jpg")
                    with open(file_path, 'wb') as f:
                        f.write(img_response.content)

                    if os.path.exists(file_path):
                        safe_file_name = re.sub(r'[^a-zA-Z0-9._-]', '_', os.path.basename(file_path))
                        upload_to_supabase(file_path, safe_file_name)
                        files.append({
                            'path': file_path,
                            'type': 'photo'
                        })
                        print(f"✅ Downloaded TikTok photo {idx}/{len(image_urls)}")
            except Exception as e:
                print(f"Failed to download TikTok photo {idx}: {e}")
                continue

        if not files:
            return [], None

        return files, safe_title

    except Exception as e:
        print(f"TikTok Photo Download Error: {e}")
        return [], None

# دالة تحميل فيديو أو صور من تيك توك أو انستقرام
def download_social(url, platform="social"):
    # معالجة خاصة لصور تيك توك أولاً (yt-dlp لا يدعم روابط /photo/)
    if "tiktok.com" in url and "/photo/" in url:
        print(f"TikTok photo URL detected: {url}")
        return download_tiktok_photos(url)

    if "instagram.com" in url:
        try:
            # استخراج الكود القصير من الرابط (shortcode)
            # مثال: https://www.instagram.com/reels/C42n6f4sy1F/ -> C42n6f4sy1F
            match = re.search(r'/(?:p|reels|reel|tv)/([A-Za-z0-9_-]+)', url)
            if not match:
                return [], None

            shortcode = match.group(1)
            post = instaloader.Post.from_shortcode(L.context, shortcode)

            files = []

            # التحقق مما إذا كان المنشور يحتوي على عدة وسائط (Carousel/Slideshow)
            if post.typename == 'GraphSidecar':
                L.download_post(post, target=OUTPUT)
                # نمر على كل وسيط داخل البوست
                for node in post.get_sidecar_nodes():
                    # الأسماء الافتراضية لـ instaloader تكون {shortcode}_{index}
                    index = len(files) + 1
                    # قد يختلف الاسم حسب نوع الملف (jpg أو mp4)
                    for ext in ['jpg', 'mp4']:
                        # instaloader يحفظ الصور بـ {shortcode}_1.jpg والفيديوهات بـ {shortcode}_1.mp4 الخ
                        potential_path = os.path.join(OUTPUT, f"{shortcode}_{index}.{ext}")
                        if os.path.exists(potential_path):
                            safe_file_name = re.sub(r'[^a-zA-Z0-9._-]', '_', os.path.basename(potential_path))
                            upload_to_supabase(potential_path, safe_file_name)
                            files.append({
                                'path': potential_path,
                                'type': 'video' if ext == 'mp4' else 'photo'
                            })
                            break
            elif post.is_video:
                # التحميل يتم في مجلد OUTPUT
                L.download_post(post, target=OUTPUT)

                # البحث عن ملف الفيديو المحمل (غالباً سيكون بنفس اسم الـ shortcode)
                file_path = os.path.join(OUTPUT, f"{shortcode}.mp4")
                if os.path.exists(file_path):
                    # الرفع لـ Supabase
                    safe_file_name = re.sub(r'[^a-zA-Z0-9._-]', '_', os.path.basename(file_path))
                    upload_to_supabase(file_path, safe_file_name)
                    files.append({'path': file_path, 'type': 'video'})
            else:
                L.download_post(post, target=OUTPUT)
                file_path = os.path.join(OUTPUT, f"{shortcode}.jpg")
                if os.path.exists(file_path):
                    safe_file_name = re.sub(r'[^a-zA-Z0-9._-]', '_', os.path.basename(file_path))
                    upload_to_supabase(file_path, safe_file_name)
                    files.append({'path': file_path, 'type': 'photo'})

            return files, post.caption[:50] if post.caption else platform

        except Exception as e:
            print(f"Instaloader Error: {e}")
            # في حال فشل instaloader، ننتقل للطريقة القديمة (yt-dlp) كنسخة احتياطية
            pass

    try:
        # الطريقة الأولى: yt-dlp مع دعم كامل للـ Carousel
        ydl_opts = {
            'outtmpl': f'{OUTPUT}/%(title)s_%(id)s.%(ext)s',
            'format': 'best[ext=mp4]/best[ext=jpg]/best[ext=png]/best',
            'quiet': True,
            'no_warnings': True,
            'skip_unavailable_fragments': True,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
            }
        }

        # إضافة ملف الكوكيز إن وجد لتجاوز حظر انستقرام
        if os.path.exists(INSTA_COOKIES_FILE):
            ydl_opts['cookiefile'] = INSTA_COOKIES_FILE
        elif os.path.exists(COOKIES_FILE):
            ydl_opts['cookiefile'] = COOKIES_FILE

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

            files = []

            # الحالة 1: منشور يحتوي على عدة عناصر (Carousel/Playlist)
            if 'entries' in info and info['entries']:
                for entry in info['entries']:
                    if not entry:
                        continue
                    file_path = ydl.prepare_filename(entry)
                    if os.path.exists(file_path):
                        ext = os.path.splitext(file_path)[1].lower()
                        file_type = 'video' if ext == '.mp4' else 'photo'
                        safe_file_name = re.sub(r'[^a-zA-Z0-9._-]', '_', os.path.basename(file_path))
                        upload_to_supabase(file_path, safe_file_name)
                        files.append({'path': file_path, 'type': file_type})

            # الحالة 2: عنصر واحد (فيديو أو صورة واحدة)
            else:
                file_path = ydl.prepare_filename(info)
                # البحث عن الملف الفعلي (قد يختلف الامتداد)
                if not os.path.exists(file_path):
                    base_path = os.path.splitext(file_path)[0]
                    for ext in ['mp4', 'jpg', 'jpeg', 'png', 'webp', 'gif']:
                        temp_path = f'{base_path}.{ext}'
                        if os.path.exists(temp_path):
                            file_path = temp_path
                            break

                if os.path.exists(file_path):
                    ext = os.path.splitext(file_path)[1].lower()
                    file_type = 'video' if ext == '.mp4' else 'photo'
                    safe_file_name = re.sub(r'[^a-zA-Z0-9._-]', '_', os.path.basename(file_path))
                    upload_to_supabase(file_path, safe_file_name)
                    files.append({'path': file_path, 'type': file_type})

            # الحالة 3: تيك توك متعدد الصور — yt-dlp يحفظ كل صورة كملف منفصل
            # مع نفس القاعدة لكن بأرقام تسلسلية: {title}_{id}.jpg -> {title}_{id}_1.jpg
            if not files and info:
                base_name = ydl.prepare_filename(info)
                base_no_ext = os.path.splitext(base_name)[0]

                # البحث عن ملفات مرقمة مثل *_1.jpg, *_2.jpg
                for i in range(1, 21):  # حد أقصى 20 صورة
                    for ext in ['jpg', 'jpeg', 'png', 'webp', 'mp4']:
                        potential = f'{base_no_ext}_{i}.{ext}'
                        if os.path.exists(potential):
                            file_type = 'video' if ext == 'mp4' else 'photo'
                            safe_file_name = re.sub(r'[^a-zA-Z0-9._-]', '_', os.path.basename(potential))
                            upload_to_supabase(potential, safe_file_name)
                            files.append({'path': potential, 'type': file_type})
                            break

            if not files:
                print(f"{platform}: لم يتم العثور على ملفات قابلة للتنزيل")
                return [], None

            safe_title = re.sub(r'[\\/*?:"<>|]', "_", info.get('title', platform))
            return files, safe_title
            
    except Exception as e:
        print(f"{platform} Download Error: {e}")
        return [], None

# أمر الإحصائيات للمطور
@bot.message_handler(commands=['stats'])
def show_stats(msg):
    if str(msg.from_user.id) != str(ADMIN_ID):
        return
        
    config = get_config()
    total_users = len(get_all_users())
    yt_count = config.get("youtube_count", 0)
    insta_count = config.get("insta_count", 0)
    tiktok_count = config.get("tiktok_count", 0)
    
    stats_text = (
        "📊 *إحصائيات البوت الكاملة*\n\n"
        f"👥 *عدد المستخدمين:* `{total_users}`\n"
        "━━━━━━━━━━━━━━━\n"
        "📥 *عمليات التحميل:*\n"
        f"📺 *يوتيوب:* `{yt_count}`\n"
        f"📸 *انستقرام:* `{insta_count}`\n"
        f"🎵 *تيك توك:* `{tiktok_count}`\n"
        "━━━━━━━━━━━━━━━\n"
        f"📈 *الإجمالي:* `{yt_count + insta_count + tiktok_count}`"
    )
    bot.reply_to(msg, stats_text, parse_mode="Markdown")

# التعامل مع أمر /start
@bot.message_handler(commands=['start', 'help'])
def start(msg):
    # إضافة المستخدم للقاعدة (مع الاسم والمعرف) والتحقق من كونه جديداً
    is_new_user = add_user(msg.from_user)
    
    # إرسال إشعار للأدمن عند وصول مستخدم جديد
    if is_new_user:
        total_users = len(get_all_users())
        user_info = f"� *مستخدم جديد انضم للبوت!*\n\n"
        user_info += f"👤 *الاسم:* {msg.from_user.first_name or 'غير معروف'}\n"
        user_info += f"🔗 *المعرف:* @{msg.from_user.username if msg.from_user.username else 'بدون معرف'}\n"
        user_info += f"🆔 *الأيدي:* `{msg.from_user.id}`\n\n"
        user_info += f"👥 *إجمالي المستخدمين الآن:* `{total_users}`"
        
        try:
            bot.send_message(ADMIN_ID, user_info, parse_mode="Markdown")
        except:
            pass  # في حالة حدوث مشكلة في الإرسال، لا نوقف البوت
    
    # التحقق من الاشتراك الإجباري
    if not check_sub(msg.chat.id):
        config = get_config()
        markup = telebot.types.InlineKeyboardMarkup()
        btn = telebot.types.InlineKeyboardButton("📢 اشترك في القناة", url=f"https://t.me/{config['channel_id'].replace('@','')}")
        markup.add(btn)
        
        sub_text = (
            "⚠️ *عذراً عزيزي، يجب عليك الاشتراك أولاً!*\n\n"
            "للاستفادة من خدمات البوت المجانية، يرجى الانضمام إلى قناتنا الرسمية ثم أرسل /start مرة أخرى.\n\n"
            f"📍 القناة: *{config['channel_id']}*"
        )
        bot.send_message(msg.chat.id, sub_text, reply_markup=markup, parse_mode="Markdown")
        return
    else:
        # إذا كان المستخدم قد اشترك للتو ولم يتم إبلاغ المطور من قبل
        if msg.chat.id not in user_subscription_notified:
            config = get_config()
            if config.get("is_force_sub"):
                try:
                    sub_info = (
                        "🔔 *مستخدم جديد دخل عبر القناة!*\n\n"
                        f"👤 *الاسم:* {msg.from_user.first_name}\n"
                        f"🔗 *المعرف:* @{msg.from_user.username if msg.from_user.username else 'لا يوجد'}\n"
                        f"🆔 *الأيدي:* `{msg.from_user.id}`\n"
                        "✅ تم التحقق من اشتراكه في قناة الاشتراك الإجباري."
                    )
                    bot.send_message(ADMIN_ID, sub_info, parse_mode="Markdown")
                    user_subscription_notified.add(msg.chat.id)
                except:
                    pass

    welcome_text = (
        f"👋 *أهلاً بك يا* {msg.from_user.first_name} *في بوت التحميل الذكي!*\n\n"
        "🚀 *أنا بوت متخصص في تحميل الفيديوهات والصوتيات من:* \n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "📺 *YouTube* | 📸 *Instagram* | 🎵 *TikTok*\n"
        "🎧 *Spotify* | 👥 *Facebook* | 🌐 *Google*\n"
        "🐦 *Twitter* | 📁 *Google Drive* | 🎶 *Deezer*\n"
        "🧵 *Threads* | 👻 *Snapchat* | 📻 *SoundCloud*\n"
        "📌 *Pinterest* | 🎬 *Likee* | 🎥 *Kwai*\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "🔍 *البحث عن الصور:*\n"
        "ارسل أي صورة وسأقوم بالبحث عن نتائج مشابهة لها فوراً.\n\n"
        "💡 *كيفية الاستخدام:*\n"
        "فقط أرسل رابط الفيديو أو المنشور الذي تود تحميله، وسأقوم بالباقي!"
    )
    
    # جلب إعدادات القناة للزر
    config = get_config()
    channel_url = f"https://t.me/{config['channel_id'].replace('@','')}"

    # إعداد لوحة الأزرار (أزرار تحت الرسالة مباشرة)
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("📢 تابع قناتنا", url=channel_url))
    
    # إذا كان المستخدم هو الأدمن، نرسل رسالة الترحيب مع زر القناة، ونظهر كيبورد التحكم أيضاً
    if msg.chat.id == ADMIN_ID:
        admin_keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        admin_keyboard.add("📊 إحصائيات", "📢 إذاعة")
        admin_keyboard.add("📢 اشتراك إجباري", "🔧 إعدادات القناة")
        admin_keyboard.add("📝 جلب ملف users.json", "📂 جلب ملف config.json")
        admin_keyboard.add("🧹 تنظيف المجلدات المؤقتة", "🚫 حظر مستخدم")
        welcome_text += "\n\n🛠️ *مرحباً أيها المطور، يمكنك التحكم بالبوت أدناه:* "
        
        # إرسال الرسالة مع زر القناة (Inline) وكيبورد الأدمن (Reply) في نفس الوقت
        bot.send_message(msg.chat.id, welcome_text, reply_markup=markup, parse_mode="Markdown")
        bot.send_message(msg.chat.id, "تم تفعيل لوحة التحكم 🛠️", reply_markup=admin_keyboard)
    else:
        bot.send_message(msg.chat.id, welcome_text, reply_markup=markup, parse_mode="Markdown")


# لوحة تحكم الأدمن
@bot.message_handler(func=lambda msg: msg.chat.id == ADMIN_ID and msg.text in [
    "📊 إحصائيات", "📢 إذاعة", "📢 اشتراك إجباري", "🔧 إعدادات القناة",
    "📝 جلب ملف users.json", "📂 جلب ملف config.json", "🧹 تنظيف المجلدات المؤقتة", "🚫 حظر مستخدم"
])
def admin_panel(msg):
    config = get_config()
    if msg.text == "📊 إحصائيات":
        users = get_all_users()
        bot.reply_to(msg, f"👥 عدد مستخدمي البوت الحالي: {len(users)}")
    
    elif msg.text == "📢 إذاعة":
        bot.reply_to(msg, "📝 أرسل الرسالة التي تريد إذاعتها (نص فقط):")
        bot.register_next_step_handler(msg, send_broadcast)

    elif msg.text == "📢 اشتراك إجباري":
        config["is_force_sub"] = not config["is_force_sub"]
        update_config(config)
        status = "✅ مفعل" if config["is_force_sub"] else "❌ معطل"
        bot.reply_to(msg, f"تم تغيير حالة الاشتراك الإجباري إلى: {status}")

    elif msg.text == "🔧 إعدادات القناة":
        bot.reply_to(msg, f"القناة الحالية: {config['channel_id']}\nأرسل معرف القناة الجديد مع @:")
        bot.register_next_step_handler(msg, update_channel)

    elif msg.text == "📝 جلب ملف users.json":
        # جلب البيانات من Supabase وحفظها في ملف مؤقت
        users = get_all_users()
        with open("users_backup.json", "w", encoding="utf-8") as f:
            json.dump(users, f, ensure_ascii=False, indent=4)
        with open("users_backup.json", "rb") as f:
            bot.send_document(msg.chat.id, f, caption="📂 ملف مستخدمي البوت (نسخة احتياطية)")
        os.remove("users_backup.json")

    elif msg.text == "📂 جلب ملف config.json":
        # جلب الإعدادات من Supabase
        config_data = get_config()
        with open("config_backup.json", "w", encoding="utf-8") as f:
            json.dump(config_data, f, ensure_ascii=False, indent=4)
        with open("config_backup.json", "rb") as f:
            bot.send_document(msg.chat.id, f, caption="⚙️ ملف إعدادات البوت")
        os.remove("config_backup.json")

    elif msg.text == "🧹 تنظيف المجلدات المؤقتة":
        count = 0
        for file in os.listdir(OUTPUT):
            file_path = os.path.join(OUTPUT, file)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    count += 1
            except:
                pass
        bot.reply_to(msg, f"✅ تم تنظيف المجلد بنجاح. تم حذف {count} ملف.")

    elif msg.text == "🚫 حظر مستخدم":
        bot.reply_to(msg, "🆔 أرسل أيدي المستخدم الذي تريد حظره:")
        bot.register_next_step_handler(msg, block_user_step)

def block_user_step(msg):
    try:
        user_id_to_block = int(msg.text)
        config = get_config()
        if "blocked_users" not in config:
            config["blocked_users"] = []
        
        if user_id_to_block not in config["blocked_users"]:
            config["blocked_users"].append(user_id_to_block)
            update_config(config)
            bot.reply_to(msg, f"✅ تم حظر المستخدم `{user_id_to_block}` بنجاح.", parse_mode="Markdown")
        else:
            bot.reply_to(msg, "⚠️ هذا المستخدم محظور بالفعل.")
    except ValueError:
        bot.reply_to(msg, "❌ خطأ: يرجى إرسال أيدي (ID) صحيح (أرقام فقط).")

def update_channel(msg):
    if not msg.text.startswith("@"):
        bot.reply_to(msg, "⚠️ خطأ: يجب أن يبدأ المعرف بـ @")
        return
    config = get_config()
    config["channel_id"] = msg.text
    update_config(config)
    bot.reply_to(msg, f"✅ تم تحديث معرف القناة إلى: {msg.text}")

def send_broadcast(msg):
    if msg.text == "إلغاء":
        bot.reply_to(msg, "🚫 تم إلغاء الإذاعة.")
        return
        
    users = get_users_list()
    count = 0
    bot.send_message(msg.chat.id, f"⌛ جاري بدء الإذاعة لـ {len(users)} مستخدم...")
    
    for user in users:
        try:
            bot.send_message(user, msg.text)
            count += 1
        except:
            pass # ربما قام المستخدم بحظر البوت
            
    bot.send_message(msg.chat.id, f"✅ تم الانتهاء! وصلت الرسالة لـ {count} مستخدم.")


# التعامل مع روابط يوتيوب
@bot.message_handler(func=lambda message: "youtube.com" in message.text or "youtu.be" in message.text)
def handle_youtube_url(msg):
    # التحقق من الاشتراك الإجباري
    if not check_sub(msg.chat.id):
        config = get_config()
        markup = telebot.types.InlineKeyboardMarkup()
        btn = telebot.types.InlineKeyboardButton("اشترك في القناة", url=f"https://t.me/{config['channel_id'].replace('@','')}")
        markup.add(btn)
        bot.send_message(msg.chat.id, f"⚠️ يجب عليك الاشتراك في القناة أولاً لتتمكن من التحميل:\n{config['channel_id']}", reply_markup=markup)
        return

    url = msg.text.strip()
    chat_id = msg.chat.id
    
    # زيادة إحصائيات يوتيوب
    # Note: we increment it later when download is confirmed
    # increment_stat("youtube_count")
    
    # حفظ الرابط مؤقتاً للمستخدم
    user_data[chat_id] = url
    
    status_msg = bot.reply_to(msg, "🔍 جاري جلب معلومات الفيديو والجودات المتاحة...")
    
    yt_info = get_yt_formats(url)
    if not yt_info:
        bot.edit_message_text("❌ فشل جلب معلومات الفيديو. يرجى التأكد من الرابط.", chat_id, status_msg.message_id)
        return

    # إنشاء كيبورد إنلاين (Inline Keyboard) لاختيار النوع والجودة
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    
    # أزرار الفيديو مع الجودات
    for f in yt_info['formats']:
        size = f'{f["filesize"]//(1024*1024)}MB' if f["filesize"] > 0 else "N/A"
        btn_text = f"🎬 {f['resolution']} ({f['ext']}) - {size}"
        markup.add(telebot.types.InlineKeyboardButton(btn_text, callback_data=f"yt_v_{f['format_id']}"))
        
    # زر الصوت
    markup.add(telebot.types.InlineKeyboardButton("🎵 تحميل كصوت (MP3)", callback_data="dl_audio"))
    
    caption = f"🎬 *{yt_info['title']}*\n\nيرجى اختيار الجودة المطلوبة للتحميل:"
    
    if yt_info['thumbnail']:
        bot.delete_message(chat_id, status_msg.message_id)
        bot.send_photo(chat_id, yt_info['thumbnail'], caption=caption, reply_markup=markup, parse_mode="Markdown")
    else:
        bot.edit_message_text(caption, chat_id, status_msg.message_id, reply_markup=markup, parse_mode="Markdown")


# التعامل مع روابط تيك توك وانستقرام وساوند كلاود
@bot.message_handler(func=lambda message: any(x in message.text for x in ["tiktok.com", "instagram.com", "soundcloud.com"]))
def handle_social_url(msg):
    print(f"[DEBUG] TikTok/Insta/SoundCloud handler triggered. msg.text: {msg.text}")
    if not check_sub(msg.chat.id):
        config = get_config()
        markup = telebot.types.InlineKeyboardMarkup()
        btn = telebot.types.InlineKeyboardButton("اشترك في القناة", url=f"https://t.me/{config['channel_id'].replace('@','')}")
        markup.add(btn)
        bot.send_message(msg.chat.id, f"⚠️ يجب الاشتراك أولاً:\n{config['channel_id']}", reply_markup=markup)
        return

    url = msg.text.strip()
    chat_id = msg.chat.id

    print(f"[DEBUG] handle_social_url called with url: {url}")

    # حل الروابط المختصرة (مثل vt.tiktok.com) للحصول على الرابط الحقيقي
    if "vt.tiktok.com" in url or "vm.tiktok.com" in url:
        try:
            print(f"[DEBUG] Resolving TikTok short link...")
            # استخدام GET مع stream=True للحصول على الروابط بدون تحميل الصفحة كاملة
            r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10, allow_redirects=True, stream=True)
            r.close()  # إغلاق الاتصال فوراً بعد الحصول على الهيدرات
            resolved_url = r.url
            print(f"[DEBUG] Resolved to: {resolved_url}")
            url = resolved_url
        except Exception as e:
            print(f"[DEBUG] Failed to resolve short link: {e}")

    if "instagram.com" in url:
        platform = "انستقرام"
        increment_stat("insta_count")
    elif "tiktok.com" in url:
        platform = "تيك توك"
        increment_stat("tiktok_count")
    elif "soundcloud.com" in url:
        platform = "ساوند كلاود"
    else:
        platform = "منصة غير معروفة"
    
    # إظهار حالة الإرسال للمستخدم
    if platform == "ساوند كلاود":
        bot.send_chat_action(chat_id, 'upload_audio')
    elif platform == "تيك توك" and "/photo/" in url:
        bot.send_chat_action(chat_id, 'upload_photo')
    else:
        bot.send_chat_action(chat_id, 'upload_video')
    
    status_msg = bot.reply_to(msg, f"⏳ جاري تحميل محتوى {platform}، يرجى الانتظار...")
    
    try:
        # إذا كان الرابط من ساوند كلاود، نستخدم تحميل الصوت
        if platform == "ساوند كلاود":
            file_path = download_mp3(url)
            if file_path and os.path.exists(file_path):
                with open(file_path, "rb") as f:
                    bot.send_audio(chat_id, f, caption="✅ تم تحميل الصوت من ساوند كلاود بنجاح", timeout=300)
                
                # حذف الملف من الستورج بعد الإرسال
                file_name_only = os.path.basename(file_path)
                safe_file_name = re.sub(r'[^a-zA-Z0-9._-]', '_', file_name_only)
                delete_from_supabase(safe_file_name)
                
                os.remove(file_path)
                bot.delete_message(chat_id, status_msg.message_id)
                return
            else:
                bot.edit_message_text(f"❌ فشل تحميل الصوت من {platform}.", chat_id, status_msg.message_id)
                return

        files, safe_title = download_social(url, platform)

        if not files:
            error_text = f"❌ فشل تحميل محتوى {platform}.\n"
            error_text += "قد يكون الحساب خاصاً، الرابط غير صحيح، أو هناك قيود على المنشور."
            bot.edit_message_text(error_text, chat_id, status_msg.message_id)
            return

        # إرسال الملفات
        photos = [f for f in files if f['type'] == 'photo']
        videos = [f for f in files if f['type'] == 'video']

        # إرسال الصور (إذا كانت أكثر من واحدة، إرسالها كألبوم)
        if photos:
            if len(photos) == 1:
                with open(photos[0]['path'], "rb") as f:
                    bot.send_photo(chat_id, f, caption=f"✅ صورة من {platform}: {safe_title}", timeout=60)
                
                # حذف من الستورج بعد الإرسال
                file_name_only = os.path.basename(photos[0]['path'])
                safe_file_name = re.sub(r'[^a-zA-Z0-9._-]', '_', file_name_only)
                delete_from_supabase(safe_file_name)
                
                os.remove(photos[0]['path'])
            else:
                # إرسال مجموعة من الصور
                media_group = []
                # نحتفظ بملفات مفتوحة لإغلاقها لاحقاً
                opened_files = []
                try:
                    for idx, photo in enumerate(photos[:10]):  # تحديد 10 صور كحد أقصى
                        f = open(photo['path'], 'rb')
                        opened_files.append(f)
                        if idx == 0:
                            media_group.append(telebot.types.InputMediaPhoto(f, caption=f"✅ {platform}: {safe_title}"))
                        else:
                            media_group.append(telebot.types.InputMediaPhoto(f))
                    
                    if media_group:
                        bot.send_media_group(chat_id, media_group, timeout=120)
                finally:
                    # إغلاق الملفات يدوياً بعد الإرسال
                    for f in opened_files:
                        f.close()
                
                # حذف الملفات من الستورج ومن الجهاز
                for photo in photos:
                    file_name_only = os.path.basename(photo['path'])
                    safe_file_name = re.sub(r'[^a-zA-Z0-9._-]', '_', file_name_only)
                    delete_from_supabase(safe_file_name)
                    
                    if os.path.exists(photo['path']):
                        os.remove(photo['path'])

        # إرسال الفيديوهات
        if videos:
            for video in videos:
                with open(video['path'], "rb") as f:
                    bot.send_video(chat_id, f, caption=f"✅ فيديو من {platform}: {safe_title}", timeout=300)
                
                # حذف من الستورج بعد الإرسال
                file_name_only = os.path.basename(video['path'])
                safe_file_name = re.sub(r'[^a-zA-Z0-9._-]', '_', file_name_only)
                delete_from_supabase(safe_file_name)
                
                os.remove(video['path'])

        bot.delete_message(chat_id, status_msg.message_id)
            
    except Exception as e:
        error_msg = str(e)
        if "Unsupported URL" in error_msg:
            bot.edit_message_text(f"❌ هذا النوع من الروابط غير مدعوم.\nالرجاء المحاولة برابط فيديو أو Reel بدلاً من الصور.", chat_id, status_msg.message_id)
        else:
            bot.edit_message_text(f"❌ حدث خطأ:\n{error_msg[:100]}", chat_id, status_msg.message_id)
        # حذف أي ملفات مؤقتة
        try:
            for file in os.listdir(OUTPUT):
                file_path = os.path.join(OUTPUT, file)
                if os.path.isfile(file_path) and (file.endswith(('.mp4', '.jpg', '.png', '.webp'))):
                    os.remove(file_path)
        except:
            pass


# التعامل مع ضغطات الأزرار (Callback Query)
@bot.callback_query_handler(func=lambda call: call.data.startswith('yt_') or call.data.startswith('dl_'))
def callback_download(call):
    chat_id = call.message.chat.id
    
    # التعامل مع طلبات التحميل من نتائج البحث
    if call.data.startswith("dl_search_"):
        video_id = call.data.replace("dl_search_", "")
        url = f"https://www.youtube.com/watch?v={video_id}"
        user_data[chat_id] = url
        
        # استدعاء دالة اختيار الجودات لهذا الرابط
        bot.answer_callback_query(call.id, "✅ تم اختيار الفيديو، اختر الجودة الآن")
        
        # نحتاج لإنشاء رسالة جديدة لاختيار الجودة
        # (بما أننا في كولباك، يمكننا استدعاء handle_youtube_url يدوياً أو محاكاة العمل)
        # لتسهيل الأمر، سنقوم بتعديل الرسالة نفسها لتظهر الجودات
        yt_info = get_yt_formats(url)
        if not yt_info:
            bot.send_message(chat_id, "❌ فشل جلب معلومات الفيديو.")
            return

        markup = telebot.types.InlineKeyboardMarkup(row_width=2)
        for f in yt_info['formats']:
            size = (f'{f["filesize"]//(1024*1024)}MB') if f["filesize"] > 0 else "N/A"
            btn_text = f"🎬 {f['resolution']} ({f['ext']}) - {size}"
            markup.add(telebot.types.InlineKeyboardButton(btn_text, callback_data=f"yt_v_{f['format_id']}"))
        markup.add(telebot.types.InlineKeyboardButton("🎵 تحميل كصوت (MP3)", callback_data="dl_audio"))
        
        caption = f"🎬 *{yt_info['title']}*\n\nيرجى اختيار الجودة المطلوبة للتحميل:"
        try:
            bot.send_photo(chat_id, yt_info['thumbnail'], caption=caption, reply_markup=markup, parse_mode="Markdown")
        except Exception as e:
            print(f"Failed to send thumbnail, sending text only: {e}")
            bot.send_message(chat_id, caption, reply_markup=markup, parse_mode="Markdown")
        return

    url = user_data.get(chat_id)
    
    if not url:
        bot.answer_callback_query(call.id, "❌ انتهت صلاحية الطلب، أرسل الرابط مرة أخرى.")
        return

    # إخبار تيليجرام بأنه تم استلام الضغطة
    bot.answer_callback_query(call.id)
    
    # معالجة طلبات الفيديو بجودة محددة أو فيديو عام
    if call.data.startswith("yt_v_") or call.data == "dl_video":
        format_id = call.data.replace("yt_v_", "") if call.data.startswith("yt_v_") else None
        
        # إظهار حالة "يرسل مقطع فيديو" (upload_video) للمستخدم
        bot.send_chat_action(chat_id, 'upload_video')
        
        # استخدام رسالة جديدة لإظهار حالة التحميل بدلاً من تعديل الصورة (إلا إذا كانت رسالة نصية)
        if hasattr(call.message, 'photo') and call.message.photo:
             status_msg = bot.send_message(chat_id, "⏳ جاري تحميل الفيديو، يرجى الانتظار...")
        else:
             bot.edit_message_text("⏳ جاري تحميل الفيديو، يرجى الانتظار...", chat_id, call.message.message_id)
             status_msg = call.message

        try:
            file_path, safe_title = download_vd(url, format_id)
            if not file_path:
                 bot.send_message(chat_id, "❌ فشل تحميل الفيديو.")
                 return

            file_size = os.path.getsize(file_path)

            if file_size > MAX_SIZE:
                bot.send_message(chat_id, f"❌ عفواً، حجم الفيديو كبير جداً ({file_size//(1024*1024)}MB).\nالحد الأقصى هو 50MB.")
                if os.path.exists(file_path): os.remove(file_path)
                return

            with open(file_path, "rb") as f:
                bot.send_video(
                    chat_id, 
                    f, 
                    caption=f"✅ تم تحميل: {safe_title}", 
                    supports_streaming=True,
                    timeout=300
                )
            
            # حذف الملف محلياً وحذفه من الستورج بعد الإرسال
            file_name_only = os.path.basename(file_path)
            # بما أننا نظفنا الاسم عند الرفع، نحتاج لاستخدام نفس المنطق هنا
            safe_file_name = re.sub(r'[^a-zA-Z0-9._-]', '_', file_name_only)
            delete_from_supabase(safe_file_name)
            
            # زيادة إحصائيات يوتيوب عند نجاح الإرسال
            increment_stat("youtube_count")
            
            if os.path.exists(file_path): os.remove(file_path)
            
        except Exception as e:
            bot.send_message(chat_id, f"❌ حدث خطأ أثناء التحميل:\n{str(e)}")
            if 'file_path' in locals() and os.path.exists(file_path): os.remove(file_path)

    elif call.data == "dl_audio":
        # إظهار حالة "يرسل ملفاً صوتياً" (upload_audio) للمستخدم
        bot.send_chat_action(chat_id, 'upload_audio')
        
        if hasattr(call.message, 'photo') and call.message.photo:
             status_msg = bot.send_message(chat_id, "⏳ جاري تحويل الرابط إلى صوت، يرجى الانتظار...")
        else:
             bot.edit_message_text("⏳ جاري تحويل الرابط إلى صوت، يرجى الانتظار...", chat_id, call.message.message_id)
             status_msg = call.message

        try:
            result = download_mp3(url)
            if isinstance(result, tuple):
                file_path, title = result
            else:
                file_path = result
                title = "Audio"

            if file_path and os.path.exists(file_path):
                with open(file_path, "rb") as f:
                    bot.send_audio(chat_id, f, caption=f"✅ {title}", timeout=300)
                
                # حذف الملف من الستورج بعد الإرسال
                file_name_only = os.path.basename(file_path)
                safe_file_name = re.sub(r'[^a-zA-Z0-9._-]', '_', file_name_only)
                delete_from_supabase(safe_file_name)
                
                # زيادة إحصائيات يوتيوب عند نجاح الإرسال (للصوت)
                increment_stat("youtube_count")
                
                os.remove(file_path)
            else:
                bot.send_message(chat_id, "❌ فشل في استخراج الصوت من هذا الرابط.")
        except Exception as e:
            bot.send_message(chat_id, f"❌ حدث خطأ أثناء التحويل:\n{str(e)}")
            if 'file_path' in locals() and os.path.exists(file_path): os.remove(file_path)
    
    # مسح الرابط من الذاكرة
    if chat_id in user_data:
        del user_data[chat_id]


# دالة تنسيق عدد المشاهدات
def format_views(n):
    if not n: return "0"
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)

# دالة البحث في يوتيوب (باستخدام تقنية مستوحاة من youtube-downloader-api)
def search_youtube(query):
    try:
        ydl_opts = YTDL_COMMON_PARAMS.copy()
        ydl_opts.update({
            'extract_flat': True,
            'default_search': 'ytsearch10',
            'nocheckcertificate': True,
            # استخدام عدة عملاء لضمان جلب النتائج بدون حظر
            'extractor_args': {'youtube': {'player_client': ['web', 'android', 'ios', 'tv']}},
        })
        
        if os.path.exists(COOKIES_FILE):
            ydl_opts['cookiefile'] = COOKIES_FILE
            
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # استخدام تقنية ytsearch لجلب النتائج
            info = ydl.extract_info(f"ytsearch10:{query}", download=False)
            results = []
            if 'entries' in info:
                for entry in info['entries']:
                    if not entry: continue
                    # نفلتر النتائج لنأخذ الفيديوهات فقط ونستبعد القنوات أو القوائم
                    if entry.get('ie_key') == 'Youtube' or '/watch?v=' in entry.get('url', ''):
                        results.append({
                            'title': entry.get('title'),
                            'url': entry.get('url') or f"https://www.youtube.com/watch?v={entry.get('id')}",
                            'id': entry.get('id'),
                            'duration': entry.get('duration'),
                            'uploader': entry.get('uploader', 'Unknown'),
                            'view_count': entry.get('view_count', 0),
                            'thumbnail': entry.get('thumbnail') or f"https://i.ytimg.com/vi/{entry.get('id')}/hqdefault.jpg"
                        })
            return results
    except Exception as e:
        print(f"YouTube Search Error: {e}")
        return []

# استيراد مكتبة requests للبحث عن الصور
import requests

# التعامل مع الصور المرسلة للبحث عن صور مشابهة
@bot.message_handler(content_types=['photo'])
def handle_image_search(msg):
    # التحقق من الاشتراك الإجباري
    if not check_sub(msg.chat.id):
        config = get_config()
        markup = telebot.types.InlineKeyboardMarkup()
        btn = telebot.types.InlineKeyboardButton("📢 اشترك في القناة", url=f"https://t.me/{config['channel_id'].replace('@','')}")
        markup.add(btn)
        bot.reply_to(msg, "⚠️ عذراً عزيزي، يجب عليك الاشتراك أولاً لاستخدام ميزة البحث عن الصور!", reply_markup=markup)
        return

    chat_id = msg.chat.id
    status_msg = bot.reply_to(msg, "🔍 جاري تحليل الصورة والبحث عن صور مشابهة عبر Google Images...")

    try:
        # الحصول على أيدي الصورة بأعلى دقة
        file_id = msg.photo[-1].file_id
        file_info = bot.get_file(file_id)
        # تحميل الصورة
        downloaded_file = bot.download_file(file_info.file_path)
        
        # حفظ الصورة مؤقتاً
        temp_image_path = os.path.join(OUTPUT, f"search_{chat_id}.jpg")
        with open(temp_image_path, 'wb') as new_file:
            new_file.write(downloaded_file)

        # استخدام Google Lens / Reverse Image Search
        # ملاحظة: سنقوم بتوجيه المستخدم لرابط النتائج المباشرة لتسهيل الأمر ولأن API جوجل مدفوع
        # لكن يمكننا محاكاة جلب بعض الروابط إذا لزم الأمر
        
        # رفع الصورة لـ Supabase للحصول على رابط عام (مطلوب لمحركات البحث)
        safe_file_name = f"search_{chat_id}_{int(os.path.getmtime(temp_image_path))}.jpg"
        public_url_res = upload_to_supabase(temp_image_path, safe_file_name)
        
        if not public_url_res:
            bot.edit_message_text("❌ فشل معالجة الصورة للبحث.", chat_id, status_msg.message_id)
            return

        public_url = public_url_res # تم تعديل دالة get_public_url لترجع الرابط مباشرة في النسخة السابقة من bot.py

        # روابط محركات البحث عن الصور
        google_search_url = f"https://www.google.com/searchbyimage?image_url={public_url}"
        yandex_search_url = f"https://yandex.com/images/search?rpt=imageview&url={public_url}"
        bing_search_url = f"https://www.bing.com/images/searchbyimage?cbir=sbi&imgurl={public_url}"

        markup = telebot.types.InlineKeyboardMarkup()
        markup.row(telebot.types.InlineKeyboardButton("🌍 Google Lens", url=google_search_url))
        markup.row(telebot.types.InlineKeyboardButton("🖼 Yandex Images", url=yandex_search_url))
        markup.row(telebot.types.InlineKeyboardButton("🔍 Bing Visual Search", url=bing_search_url))

        caption = "✅ تم العثور على نتائج!\n\nيمكنك استعراض الصور المشابهة عبر المحركات التالية:"
        bot.edit_message_text(caption, chat_id, status_msg.message_id, reply_markup=markup)

        # حذف الملف مؤقتاً بعد فترة أو تركه ليقوم المطور بتنظيفه
        os.remove(temp_image_path)
        
    except Exception as e:
        print(f"Image Search Error: {e}")
        bot.edit_message_text("❌ حدث خطأ أثناء محاولة البحث عن الصورة.", chat_id, status_msg.message_id)

# التعامل مع أي رسالة أخرى
@bot.message_handler(func=lambda message: True)
def handle_other_messages(msg):
    # التحقق من الحظر
    config = get_config()
    if msg.from_user.id in config.get("blocked_users", []):
        bot.reply_to(msg, "🚫 عذراً، لقد تم حظرك من استخدام هذا البوت بواسطة المطور.")
        return

    # إذا بدأت الرسالة بـ /dl_ وتعتبر أمراً، لا نعالجها كبحث (على الرغم من وجود هاندلر خاص بها)
    if msg.text and msg.text.startswith('/dl_'):
        return

    # إذا كانت الرسالة عبارة عن نص بحث (وليس رابطاً تم التعامل معه مسبقاً)
    query = msg.text.strip()
    
    # التحقق من أن النص ليس رابطاً (لأننا تعاملنا مع الروابط في دوال أخرى)
    if any(x in query for x in ["youtube.com", "youtu.be", "instagram.com", "tiktok.com"]):
        return # تم التعامل معه بالفعل

    import html
    status_msg = bot.reply_to(msg, f"🔎 جاري البحث عن <b>{html.escape(query)}</b> في يوتيوب...", parse_mode="HTML")
    
    results = search_youtube(query)
    
    if not results:
        bot.edit_message_text(f"❌ لم يتم العثور على نتائج للبحث: {html.escape(query)}", msg.chat.id, status_msg.message_id, parse_mode="HTML")
        return

    response_text = f"🔍 *نتائج البحث لـ:* \"{html.escape(query)}\"\n\n"
    markup = telebot.types.InlineKeyboardMarkup(row_width=5)
    dl_buttons = []
    
    for i, res in enumerate(results[:5], 1): # عرض أول 5 نتائج
        duration = f"{int(res['duration']//60)}:{int(res['duration']%60):02d}" if res['duration'] else "0:00"
        views = format_views(res['view_count'])
        
        safe_title = html.escape(res['title'])
        safe_uploader = html.escape(res['uploader'])
        
        response_text += f"{i}️⃣ <b>{safe_title}</b>\n"
        response_text += f"👤 {safe_uploader} | 🕒 {duration} | 👁 {views}\n\n"
        
        # إضافة زر برقم المقطع للتحميل السهل
        dl_buttons.append(telebot.types.InlineKeyboardButton(f"{i}", callback_data=f"dl_search_{res['id']}"))
    
    # إضافة أزرار الأرقام في صف واحد
    markup.add(*dl_buttons)
    
    # زر التالي
    safe_query_callback = query[:20].replace(":", "_").replace("|", "_")
    markup.add(telebot.types.InlineKeyboardButton("« التالي", callback_data=f"search_next_{safe_query_callback}"))
    
    # توجيه الرسالة للأدمن
    try:
        user_info = f"📩 *بحث جديد من مستخدم!*\n\n"
        user_info += f"👤 *الاسم:* {msg.from_user.first_name}\n"
        user_info += f"🆔 *الأيدي:* `{msg.from_user.id}`\n"
        user_info += f"📝 *البحث:* {query}"
        bot.send_message(ADMIN_ID, user_info, parse_mode="Markdown")
    except:
        pass

    bot.edit_message_text(response_text, msg.chat.id, status_msg.message_id, reply_markup=markup, parse_mode="HTML", disable_web_page_preview=True)


# طباعة رسالة في الكونسول
print("The bot is running..")

# تشغيل البوت باستمرار مع معالجة الأخطاء لتجنب Conflict 409
import time
while True:
    try:
        bot.polling(none_stop=True, timeout=60, long_polling_timeout=60)
    except Exception as e:
        print(f"Error in polling: {e}")
        time.sleep(15)  # انتظار 15 ثانية قبل إعادة المحاولة لتجنب الـ Conflict
