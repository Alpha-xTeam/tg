
import requests
proxies = {'http': 'socks4://111.161.126.107:80', 'https': 'socks4://111.161.126.107:80'}
try:
    r = requests.get('http://httpbin.org/ip', proxies=proxies, timeout=10)
    print('✅ Proxy works! IP:', r.json()['origin'])
except Exception as e:
    print('❌ Proxy failed:', e)
