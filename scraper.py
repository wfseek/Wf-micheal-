import requests
import json
import time
import urllib3
import random
import sys

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Your discovered SportyBet endpoints
BASE_URL = 'https://www.sportybet.com/tz'
ENDPOINTS = {
    'events_by_order': '/factsCenter/wapConfigurableEventsByOrder',
    'live_events': '/factsCenter/wapConfigurableIndexLiveEvents',
    'highlight_events': '/factsCenter/wapConfigurableMixHighlightEvents',
    'quick_market_a': '/factsCenter/quickMarketList?block=A&sport=sr:sport:1',
    'quick_market_b': '/factsCenter/quickMarketList?block=B&sport=sr:sport:1',
    'recommend_events': '/factsCenter/recommendScrollEvents/v2',
    'custom_events': '/factsCenter/configurableCustomEvents',
    'stale_odds': '/factsCenter/stale-odds/resume-policy',
    'story_sets': '/factsCenter/story/v1/story-sets?page=0&pageSize=15',
    'broadcast_config': '/common/config/broadcast',
    'common_config': '/common/config/query',
    'promotion_query': '/promotion/v1/sp/query',
    'featured_booking': '/orders/bookingCode/featured?pageNum=1&pageSize=10',
    'featured_users': '/patron/socialpage/featured-users',
    'games_lobby': '/games/lobby/v1/games/getByRanking',
    'anTest_campaign': '/anTest/client/campaign',
}

# Free proxy sources
PROXY_SOURCES = [
    'https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/http.txt',
    'https://raw.githubusercontent.com/komutan234/Proxy-List-Free/main/proxies/http.txt',
    'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt',
]

def get_free_proxies():
    """Get fresh free proxies from multiple sources"""
    proxies = []
    for url in PROXY_SOURCES:
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                proxies.extend([p.strip() for p in r.text.split('\n') if ':' in p.strip()])
        except:
            continue
    return list(set(proxies))

def get_bypass_headers():
    """All bypass header variations"""
    base = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 12; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Origin': 'https://www.sportybet.com',
        'Referer': 'https://www.sportybet.com/tz/m/sport/football',
        'X-Requested-With': 'XMLHttpRequest',
        'Connection': 'keep-alive',
    }
    
    variations = [
        base,
        {**base, 'X-Forwarded-For': '127.0.0.1', 'X-Real-IP': '127.0.0.1', 'X-Originating-IP': '127.0.0.1'},
        {**base, 'X-Forwarded-For': '192.168.1.1', 'X-Real-IP': '192.168.1.1'},
        {**base, 'X-Forwarded-For': '10.0.0.1', 'X-Real-IP': '10.0.0.1'},
        {**base, 'X-Forwarded-For': '172.16.0.1', 'X-Real-IP': '172.16.0.1'},
        {**base, 'X-HTTP-Method-Override': 'GET', 'X-Original-Method': 'GET'},
        {**base, 'X-Forwarded-Host': 'www.sportybet.com', 'X-Forwarded-Proto': 'https'},
        {**base, 'CF-Connecting-IP': '127.0.0.1'},
        {**base, 'X-Client-IP': '127.0.0.1', 'X-Remote-IP': '127.0.0.1'},
    ]
    return variations

def get_url_variations(endpoint):
    """All URL path variations"""
    return [
        f'{BASE_URL}{endpoint}',
        f'{BASE_URL}{endpoint}/',
        f'{BASE_URL}{endpoint}..;/',
        f'{BASE_URL}/./{endpoint.lstrip("/")}',
        f'{BASE_URL}/%2e/{endpoint.lstrip("/")}',
        f'{BASE_URL}%2f{endpoint.lstrip("/")}',
        f'{BASE_URL}//{endpoint.lstrip("/")}',
        f'{BASE_URL}{endpoint.replace("/", "//")}',
        f'{BASE_URL}{endpoint}?cache_bust={random.randint(1000,9999)}',
    ]

def try_request(url, headers, proxy=None, method='GET', data=None):
    """Try a single request with given parameters"""
    try:
        proxies = {'http': f'http://{proxy}', 'https': f'http://{proxy}'} if proxy else None
        
        if method == 'GET':
            response = requests.get(
                url, headers=headers, proxies=proxies, 
                timeout=15, verify=False, allow_redirects=True
            )
        elif method == 'POST':
            response = requests.post(
                url, headers=headers, data=data, proxies=proxies,
                timeout=15, verify=False, allow_redirects=True
            )
        elif method == 'PUT':
            response = requests.put(
                url, headers=headers, proxies=proxies,
                timeout=15, verify=False, allow_redirects=True
            )
        
        if response.status_code == 200:
            try:
                return response.json()
            except:
                return {'text': response.text[:1000]}
        return {'error': f'Status {response.status_code}'}
        
    except Exception as e:
        return {'error': str(e)[:100]}

def try_all_techniques(endpoint):
    """Try all bypass techniques for an endpoint"""
    print(f"\n{'='*60}")
    print(f"Testing: {endpoint}")
    print(f"{'='*60}")
    
    # Get variations
    urls = get_url_variations(endpoint)
    headers_list = get_bypass_headers()
    proxies = get_free_proxies()
    
    print(f"URLs to try: {len(urls)}")
    print(f"Header variations: {len(headers_list)}")
    print(f"Proxies available: {len(proxies)}")
    
    # Technique 1: Direct requests with different headers
    print("\n[1] Trying direct requests with header variations...")
    for i, headers in enumerate(headers_list):
        for url in urls[:3]:  # First 3 URL variations
            print(f"  Direct attempt {i+1}...")
            result = try_request(url, headers)
            if 'error' not in result:
                print(f"  ✅ SUCCESS - Direct with headers variation {i+1}")
                return result, f"direct_headers_{i+1}"
    
    # Technique 2: With free proxies
    print("\n[2] Trying with free proxies...")
    for i, proxy in enumerate(proxies[:15]):
        print(f"  Proxy {i+1}/15: {proxy[:20]}...")
        for headers in headers_list[:3]:
            for url in urls[:2]:
                result = try_request(url, headers, proxy)
                if 'error' not in result:
                    print(f"  ✅ SUCCESS - Proxy {proxy[:20]}")
                    return result, f"proxy_{i+1}"
    
    # Technique 3: POST with method override
    print("\n[3] Trying POST with method override...")
    for headers in headers_list:
        headers = {**headers, 'X-HTTP-Method-Override': 'GET'}
        for url in urls[:2]:
            result = try_request(url, headers, method='POST')
            if 'error' not in result:
                print(f"  ✅ SUCCESS - POST override")
                return result, "post_override"
    
    # Technique 4: PUT request
    print("\n[4] Trying PUT requests...")
    for headers in headers_list[:2]:
        for url in urls[:2]:
            result = try_request(url, headers, method='PUT')
            if 'error' not in result:
                print(f"  ✅ SUCCESS - PUT")
                return result, "put_method"
    
    # Technique 5: Case manipulation
    print("\n[5] Trying case manipulation...")
    case_urls = [
        f'{BASE_URL}{endpoint}'.replace('factsCenter', 'FactsCenter'),
        f'{BASE_URL}{endpoint}'.replace('factsCenter', 'FACTSCENTER').lower(),
        f'{BASE_URL}{endpoint}'.replace('wapConfigurable', 'WAPCONFIGURABLE').lower(),
    ]
    for url in case_urls:
        for headers in headers_list[:2]:
            result = try_request(url, headers)
            if 'error' not in result:
                print(f"  ✅ SUCCESS - Case manipulation")
                return result, "case_manipulation"
    
    return {'error': 'All techniques failed'}, None

def main():
    print("=" * 70)
    print("SPORTYBET SCRAPER - ALL BYPASS TECHNIQUES COMBINED")
    print("=" * 70)
    
    results = {}
    successful_techniques = {}
    
    for name, endpoint in ENDPOINTS.items():
        data, technique = try_all_techniques(endpoint)
        
        results[name] = {
            'endpoint': endpoint,
            'data': data,
            'technique': technique,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        if technique:
            successful_techniques[name] = technique
        
        time.sleep(1)  # Be nice
    
    # Save results
    with open('odds.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    
    success_count = len(successful_techniques)
    print(f"Successful: {success_count}/{len(ENDPOINTS)}")
    
    if successful_techniques:
        print("\n✅ Working endpoints and techniques:")
        for name, tech in successful_techniques.items():
            print(f"  - {name}: {tech}")
    
    print(f"\nSaved to odds.json")
    print(f"{'='*70}")

if __name__ == '__main__':
    main()
        
