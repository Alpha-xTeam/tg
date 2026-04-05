"""
🔍 أداة للبحث عن برووكسيات شغالة تلقائياً
يجيب برووكسيات من مصادر مجانية ويختبرها
"""

import requests
import concurrent.futures
import json
import os

# مصادر البرووكسيات المجانية
PROXY_SOURCES = [
    "https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&proxy_type=socks4&country=all&proxy_minl=0&proxy_maxl=0&sort=last_checked&direction=desc&limit=50",
    "https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&proxy_type=socks5&country=all&proxy_minl=0&proxy_maxl=0&sort=last_checked&direction=desc&limit=50",
    "https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&proxy_type=http&country=all&proxy_minl=0&proxy_maxl=0&sort=last_checked&direction=desc&limit=50",
    # مصادر إضافية
    "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks4.txt",
    "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks5.txt",
]

def test_proxy(proxy_url, timeout=8):
    """اختبار برووكسي واحد"""
    protocol = proxy_url.split("://")[0] if "://" in proxy_url else "http"
    proxies = {
        "http": proxy_url,
        "https": proxy_url,
    }
    try:
        r = requests.get("http://httpbin.org/ip", proxies=proxies, timeout=timeout)
        if r.status_code == 200:
            ip = r.json().get("origin", "Unknown")
            print(f"✅ {proxy_url} | IP: {ip}")
            return {"proxy": proxy_url, "ip": ip, "status": "working"}
    except:
        pass
    return {"proxy": proxy_url, "status": "failed"}

def get_proxies_from_sources():
    """جيب البرووكسيات من المصادر"""
    all_proxies = set()
    
    for source in PROXY_SOURCES:
        try:
            print(f"📥 جيب البرووكسيات من: {source.split('/')[-1]}")
            res = requests.get(source, timeout=10)
            
            if "proxyscrape" in source:
                data = res.json()
                raw_list = data.get("proxyList", [])
            else:
                raw_list = res.text.strip().split("\n")
            
            for line in raw_list:
                line = line.strip()
                if not line or ":" not in line:
                    continue
                # أضف البروتوكول إذا مو موجود
                if not line.startswith(("http://", "https://", "socks4://", "socks5://")):
                    parts = line.split(":")
                    if len(parts) >= 2:
                        line = f"socks4://{parts[0]}:{parts[1]}"
                all_proxies.add(line)
                
            print(f"   ✅ حصلت {len(raw_list)} برووكسي")
        except Exception as e:
            print(f"   ❌ فشل: {e}")
    
    return list(all_proxies)

def find_working_proxies(max_workers=20):
    """ابحث عن برووكسيات شغالة"""
    print("🔍 أبداً البحث عن برووكسيات شغالة...\n")
    
    all_proxies = get_proxies_from_sources()
    print(f"\n📋 إجمالي البرووكسيات: {len(all_proxies)}")
    print(f"⏳ أختبرهم الآن... (يأخذ دقيقة)\n")
    
    working = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(test_proxy, p): p for p in all_proxies}
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result["status"] == "working":
                working.append(result)
    
    print(f"\n{'='*50}")
    print(f"✅ لقيت {len(working)} برووكسي شغال!\n")
    
    for i, w in enumerate(working[:5], 1):
        print(f"{i}. {w['proxy']} (IP: {w['ip']})")
    
    if working:
        # احفظ أفضل برووكسي في ملف .env
        best = working[0]
        env_file = ".env"
        env_content = {}
        
        # اقرأ الإعدادات الموجودة
        if os.path.exists(env_file):
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    if "=" in line and not line.startswith("#"):
                        key, val = line.strip().split("=", 1)
                        env_content[key] = val
        
        env_content["PROXY_URL"] = best["proxy"]
        
        with open(env_file, "w", encoding="utf-8") as f:
            for key, val in env_content.items():
                f.write(f"{key}={val}\n")
        
        print(f"\n✅ حفظت أفضل برووكسي في .env:")
        print(f"   PROXY_URL={best['proxy']}")
        
        # احفظ قائمة كاملة
        with open("working_proxies.json", "w") as f:
            json.dump(working, f, indent=2)
        print(f"✅ حفظت {len(working)} برووكسي في working_proxies.json")
    
    return working

if __name__ == "__main__":
    find_working_proxies()
