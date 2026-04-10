import requests
import json
import time
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = 'https://www.sportybet.com/tz'
ENDPOINTS = {
    'events_by_order': '/factsCenter/wapConfigurableEventsByOrder',
    'live_events': '/factsCenter/wapConfigurableIndexLiveEvents',
    'highlight_events': '/factsCenter/wapConfigurableMixHighlightEvents',
    'quick_market_a': '/factsCenter/quickMarketList?block=A&sport=sr:sport:1',
    'quick_market_b': '/factsCenter/quickMarketList?block=B&sport=sr:sport:1',
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 12; SM-G991B) AppleWebKit/537.36',
    'Accept': 'application/json',
    'X-Forwarded-For': '127.0.0.1',
    'X-Real-IP': '127.0.0.1',
    'Referer': 'https://www.sportybet.com/tz/m/sport/football',
}

def try_endpoint(endpoint):
    """Fast attempt with 3 techniques only"""
    url = f'{BASE_URL}{endpoint}'
    
    # Technique 1: Direct with IP spoofing (5s timeout)
    try:
        r = requests.get(url, headers=HEADERS, timeout=5, verify=False)
        if r.status_code == 200:
            return r.json(), 'direct_ip_spoof'
    except:
        pass
    
    # Technique 2: Trailing slash
    try:
        r = requests.get(f'{url}/', headers=HEADERS, timeout=5, verify=False)
        if r.status_code == 200:
            return r.json(), 'trailing_slash'
    except:
        pass
    
    # Technique 3: POST override
    try:
        h = {**HEADERS, 'X-HTTP-Method-Override': 'GET'}
        r = requests.post(url, headers=h, timeout=5, verify=False)
        if r.status_code == 200:
            return r.json(), 'post_override'
    except:
        pass
    
    return {'error': 'Failed'}, None

def main():
    results = {}
    
    for name, endpoint in ENDPOINTS.items():
        print(f"Testing {name}...")
        data, tech = try_endpoint(endpoint)
        results[name] = {'data': data, 'technique': tech}
        print(f"  {'✅' if tech else '❌'} {tech or 'Failed'}")
        time.sleep(0.5)  # Small delay only
    
    with open('odds.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    success = sum(1 for r in results.values() if r['technique'])
    print(f"\nDone: {success}/{len(ENDPOINTS)} succeeded")

if __name__ == '__main__':
    main()
        
