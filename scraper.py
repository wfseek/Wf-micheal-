import requests
import json
import time
import sys
from urllib.parse import urljoin

# Disable SSL warnings (for free proxies with bad certs)
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# SportyBet endpoints from your discovery
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

# Mobile headers to mimic real browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 12; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Origin': 'https://www.sportybet.com',
    'Referer': 'https://www.sportybet.com/tz/m/sport/football',
    'X-Requested-With': 'XMLHttpRequest',
    'Connection': 'keep-alive',
}

def get_free_proxies():
    """Get fresh free proxies from multiple sources"""
    sources = [
        'https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/http.txt',
        'https://raw.githubusercontent.com/komutan234/Proxy-List-Free/main/proxies/http.txt',
        'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt',
    ]
    
    proxies = []
    for url in sources:
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                proxies.extend([p.strip() for p in r.text.split('\n') if ':' in p.strip()])
        except:
            continue
    
    # Remove duplicates and test a sample
    unique_proxies = list(set(proxies))
    print(f"Loaded {len(unique_proxies)} unique proxies from {len(sources)} sources")
    return unique_proxies

def test_proxy(proxy):
    """Quick test if proxy works"""
    try:
        proxy_dict = {
            'http': f'http://{proxy}',
            'https': f'http://{proxy}'
        }
        
        # Test with a lightweight endpoint
        test_url = f'{BASE_URL}/common/config/broadcast'
        
        response = requests.get(
            test_url,
            headers=HEADERS,
            proxies=proxy_dict,
            timeout=15,
            verify=False  # Bypass SSL cert issues
        )
        
        if response.status_code == 200:
            return proxy_dict
        return None
    except Exception as e:
        return None

def scrape_endpoint(name, endpoint, proxy_dict=None):
    """Scrape specific endpoint"""
    url = urljoin(BASE_URL, endpoint)
    
    try:
        if proxy_dict:
            response = requests.get(
                url,
                headers=HEADERS,
                proxies=proxy_dict,
                timeout=30,
                verify=False
            )
        else:
            # Try direct (will likely fail with 403 but try anyway)
            response = requests.get(
                url,
                headers=HEADERS,
                timeout=10,
                verify=False
            )
        
        if response.status_code == 200:
            try:
                return response.json()
            except:
                return {'text': response.text[:500]}
        else:
            return {'error': f'Status {response.status_code}', 'url': url}
            
    except Exception as e:
        return {'error': str(e), 'url': url}

def main():
    print("=" * 60)
    print("SportyBet Scraper - Fixed Version")
    print("=" * 60)
    
    # Get proxies
    proxies = get_free_proxies()
    
    # Find working proxy
    working_proxy = None
    if proxies:
        # Test random 20 proxies
        test_sample = proxies[:20]  # Test first 20 (faster)
        
        for i, proxy in enumerate(test_sample):
            print(f"[{i+1}/20] Testing proxy: {proxy[:20]}...")
            result = test_proxy(proxy)
            if result:
                working_proxy = result
                print(f"✅ Working proxy found!")
                break
    
    # Scrape all endpoints
    results = {}
    
    for name, endpoint in ENDPOINTS.items():
        print(f"\n🔍 Scraping: {name}")
        
        # Try with proxy first, then direct
        data = scrape_endpoint(name, endpoint, working_proxy)
        
        if 'error' in data and working_proxy:
            # Try another proxy if first failed
            for backup in proxies[20:25]:  # Try 5 backups
                backup_dict = {'http': f'http://{backup}', 'https': f'http://{backup}'}
                data = scrape_endpoint(name, endpoint, backup_dict)
                if 'error' not in data:
                    break
        
        results[name] = {
            'endpoint': endpoint,
            'data': data,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        status = '✅' if 'error' not in data else '❌'
        print(f"{status} Result: {data.get('error', 'Success')[:50]}")
        
        # Small delay to be nice
        time.sleep(1)
    
    # Save results
    with open('odds.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    # Summary
    success_count = sum(1 for r in results.values() if 'error' not in r['data'])
    print(f"\n{'=' * 60}")
    print(f"SUMMARY: {success_count}/{len(ENDPOINTS)} endpoints succeeded")
    print(f"Saved to odds.json")
    print(f"{'=' * 60}")
    
    # Print successful endpoints
    if success_count > 0:
        print("\n✅ Working endpoints:")
        for name, result in results.items():
            if 'error' not in result['data']:
                print(f"  - {name}: {result['endpoint']}")

if __name__ == '__main__':
    main()
                             
