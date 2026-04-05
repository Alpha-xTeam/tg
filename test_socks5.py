"""
🔍 أداة لاختبار برووكسيات SOCKS5 مع YouTube
تختبر كل برووكسي وتتأكد إنه يشتغل مع YouTube
"""

import requests
import concurrent.futures
import os
import json

# قائمة البرووكسيات
PROXY_LIST = [
    "socks5://72.49.49.11:31034",
    "socks5://208.102.51.6:58208",
    "socks5://69.61.200.104:36181",
    "socks5://66.42.224.229:41679",
    "socks5://192.111.137.37:18762",
    "socks5://192.252.208.67:14287",
    "socks5://192.111.137.34:18765",
    "socks5://192.252.208.70:14282",
    "socks5://192.252.211.197:14921",
    "socks5://192.111.139.163:19404",
    "socks5://72.195.34.35:27360",
    "socks5://174.77.111.198:49547",
    "socks5://98.178.72.21:10919",
    "socks5://72.195.34.60:27391",
    "socks5://184.178.172.28:15294",
    "socks5://184.178.172.25:15291",
    "socks5://184.178.172.18:15280",
    "socks5://184.178.172.5:15303",
    "socks5://98.181.137.83:4145",
    "socks5://70.166.167.38:57728",
    "socks5://184.178.172.13:15311",
    "socks5://98.175.31.222:4145",
    "socks5://72.205.0.93:4145",
    "socks5://195.39.233.14:44567",
    "socks5://170.233.30.33:4153",
    "socks5://184.170.251.30:11288",
    "socks5://134.199.159.23:1080",
    "socks5://104.248.203.234:1080",
    "socks5://121.169.46.116:1090",
    "socks5://103.76.149.140:1080",
    "socks5://103.30.29.49:1080",
    "socks5://194.163.167.32:1080",
    "socks5://5.255.117.127:1080",
    "socks5://5.255.117.250:1080",
    "socks5://95.78.118.172:1080",
    "socks5://202.72.232.121:1080",
    "socks5://195.46.183.181:1080",
    "socks5://203.189.152.79:1080",
    "socks5://159.223.53.194:1080",
    "socks5://38.76.200.182:58367",
    "socks5://154.64.235.206:58367",
    "socks5://149.62.186.244:1080",
    "socks5://173.249.5.133:1080",
    "socks5://94.230.127.180:1080",
    "socks5://103.75.118.84:1080",
    "socks5://185.175.229.58:1080",
    "socks5://103.239.54.22:1080",
    "socks5://206.123.156.230:4168",
    "socks5://119.148.11.141:22122",
    "socks5://206.123.156.233:23733",
    "socks5://206.123.156.229:5475",
    "socks5://206.123.156.200:4695",
    "socks5://206.123.156.200:4744",
    "socks5://206.123.156.199:4197",
    "socks5://206.123.156.183:9789",
    "socks5://206.123.156.229:5994",
    "socks5://206.123.156.222:6252",
    "socks5://206.123.156.223:5886",
    "socks5://206.123.156.199:5859",
    "socks5://206.123.156.222:6329",
    "socks5://206.123.156.207:5977",
    "socks5://206.123.156.199:5708",
    "socks5://206.123.156.204:7069",
    "socks5://206.123.156.220:5951",
    "socks5://206.123.156.222:5733",
    "socks5://206.123.156.227:5224",
    "socks5://206.123.156.200:8052",
    "socks5://206.123.156.230:4178",
    "socks5://206.123.156.236:5061",
    "socks5://206.123.156.230:4245",
    "socks5://206.123.156.234:5479",
    "socks5://195.190.121.154:1080",
    "socks5://206.123.156.227:4865",
    "socks5://206.123.156.229:4130",
    "socks5://206.123.156.225:8000",
    "socks5://195.19.49.8:1080",
    "socks5://206.123.156.222:5737",
    "socks5://206.123.156.222:5758",
    "socks5://206.123.156.204:5775",
    "socks5://206.123.156.222:5734",
    "socks5://206.123.156.183:6025",
    "socks5://206.123.156.213:4764",
    "socks5://206.123.156.234:32063",
    "socks5://206.123.156.222:10468",
    "socks5://206.123.156.222:5760",
    "socks5://206.123.156.207:4715",
    "socks5://206.123.156.200:7395",
    "socks5://206.123.156.236:9002",
    "socks5://206.123.156.217:9000",
    "socks5://206.123.156.190:10367",
    "socks5://206.123.156.206:6574",
    "socks5://206.123.156.200:8994",
    "socks5://206.123.156.219:4303",
    "socks5://206.123.156.223:5481",
    "socks5://206.123.156.180:4122",
    "socks5://206.123.156.211:4434",
    "socks5://206.123.156.238:5302",
    "socks5://206.123.156.211:6011",
    "socks5://206.123.156.230:5683",
    "socks5://206.123.156.230:5282",
]

def test_proxy_with_http(proxy_url, timeout=8):
    """اختبار برووكسي مع اتصال HTTP عادي"""
    proxies = {"http": proxy_url, "https": proxy_url}
    try:
        r = requests.get("http://httpbin.org/ip", proxies=proxies, timeout=timeout)
        if r.status_code == 200:
            ip = r.json().get("origin", "Unknown")
            return {"proxy": proxy_url, "ip": ip, "status": "working"}
    except:
        pass
    return {"proxy": proxy_url, "status": "failed"}

def test_proxy_with_youtube(proxy_url, timeout=10):
    """اختبار برووكسي مع YouTube مباشرة"""
    try:
        from pytubefix import YouTube
        
        # اختصار: نجيب معلومات فيديو قصير
        proxies = {"http": proxy_url, "https": proxy_url}
        yt = YouTube("https://www.youtube.com/watch?v=jNQXAC9IVRw", 
                     client='TV', 
                     proxies=proxies)
        title = yt.title
        if title:
            return {"proxy": proxy_url, "status": "youtube_ok", "title": title[:50]}
    except Exception as e:
        error_msg = str(e)
        if "SSL" in error_msg or "EOF" in error_msg:
            return {"proxy": proxy_url, "status": "ssl_failed"}
        elif "timed out" in error_msg or "timeout" in error_msg.lower():
            return {"proxy": proxy_url, "status": "timeout"}
        elif "refused" in error_msg.lower() or "connect" in error_msg.lower():
            return {"proxy": proxy_url, "status": "connection_failed"}
        return {"proxy": proxy_url, "status": f"error: {error_msg[:50]}"}
    return {"proxy": proxy_url, "status": "failed"}

def test_proxies(mode="youtube"):
    """اختبار كل البرووكسيات
    
    Args:
        mode: "http" للاختبار السريع أو "youtube" للاختبار الحقيقي
    """
    print(f"🔍 أبداً اختبار {len(PROXY_LIST)} برووكسي...")
    print(f"📌 وضع الاختبار: {mode}\n")
    
    working = []
    tested = 0
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
        if mode == "http":
            futures = {executor.submit(test_proxy_with_http, p): p for p in PROXY_LIST}
        else:
            futures = {executor.submit(test_proxy_with_youtube, p): p for p in PROXY_LIST}
        
        for future in concurrent.futures.as_completed(futures):
            tested += 1
            result = future.result()
            
            if result["status"] in ["working", "youtube_ok"]:
                working.append(result)
                status_icon = "✅"
                extra = f"IP: {result.get('ip', 'N/A')}" if mode == "http" else f"Title: {result.get('title', 'N/A')}"
                print(f"{status_icon} [{tested}/{len(PROXY_LIST)}] {result['proxy']} | {extra}")
            elif tested % 10 == 0:
                print(f"⏳ [{tested}/{len(PROXY_LIST)}] ... جاري الاختبار ...")
    
    print(f"\n{'='*60}")
    print(f"✅ لقيت {len(working)} برووكسي شغال من {len(PROXY_LIST)}!\n")
    
    if working:
        # اعرض أفضل 5
        print("🏆 أفضل 5 برووكسيات:\n")
        for i, w in enumerate(working[:5], 1):
            print(f"  {i}. {w['proxy']}")
            if 'ip' in w:
                print(f"     IP: {w['ip']}")
            if 'title' in w:
                print(f"     ✓ YouTube: {w['title']}")
            print()
        
        # احفظ في .env
        best = working[0]
        
        # اقرأ .env الموجود
        env_file = ".env"
        env_content = {}
        if os.path.exists(env_file):
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    if "=" in line and not line.startswith("#"):
                        key, val = line.strip().split("=", 1)
                        env_content[key] = val
        
        env_content["PROXY_URL"] = best["proxy"]
        
        with open(env_file, "w", encoding="utf-8") as f:
            f.write("# برووكسي شغال (آخر تحديث: الآن)\n")
            for key, val in env_content.items():
                f.write(f"{key}={val}\n")
        
        print(f"✅ حفظت أفضل برووكسي في .env:")
        print(f"   PROXY_URL={best['proxy']}\n")
        
        # احفظ قائمة كاملة
        with open("working_socks5_proxies.json", "w") as f:
            json.dump(working, f, indent=2)
        print(f"✅ حفظت {len(working)} برووكسي في working_socks5_proxies.json")
    
    return working

if __name__ == "__main__":
    import sys
    mode = sys.argv[1] if len(sys.argv) > 1 else "youtube"
    test_proxies(mode)
