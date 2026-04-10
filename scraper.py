import requests
import cloudscraper
import random
import json
import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# SportyBet API Endpoints (from your discovery)
SPORTYBET_ENDPOINTS = {
    'events_by_order': 'https://www.sportybet.com/tz/factsCenter/wapConfigurableEventsByOrder',
    'live_events': 'https://www.sportybet.com/tz/factsCenter/wapConfigurableIndexLiveEvents',
    'highlight_events': 'https://www.sportybet.com/tz/factsCenter/wapConfigurableMixHighlightEvents',
    'quick_market_a': 'https://www.sportybet.com/tz/factsCenter/quickMarketList?block=A&sport=sr:sport:1',
    'quick_market_b': 'https://www.sportybet.com/tz/factsCenter/quickMarketList?block=B&sport=sr:sport:1',
    'recommend_events': 'https://www.sportybet.com/tz/factsCenter/recommendScrollEvents/v2',
    'custom_events': 'https://www.sportybet.com/tz/factsCenter/configurableCustomEvents',
    'stale_odds': 'https://www.sportybet.com/tz/factsCenter/stale-odds/resume-policy',
    'story_sets': 'https://www.sportybet.com/tz/factsCenter/story/v1/story-sets?page=0&pageSize=15',
    'broadcast_config': 'https://www.sportybet.com/tz/common/config/broadcast',
    'common_config': 'https://www.sportybet.com/tz/common/config/query',
    'promotion_query': 'https://www.sportybet.com/tz/promotion/v1/sp/query',
    'featured_booking': 'https://www.sportybet.com/tz/orders/bookingCode/featured?pageNum=1&pageSize=10',
    'featured_users': 'https://www.sportybet.com/tz/patron/socialpage/featured-users',
    'games_lobby': 'https://www.sportybet.com/tz/games/lobby/v1/games/getByRanking',
    'anTest_campaign': 'https://www.sportybet.com/tz/anTest/client/campaign',
}

# Mobile headers to mimic app
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 12; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Origin': 'https://www.sportybet.com',
    'Referer': 'https://www.sportybet.com/tz/m/sport/football',
    'X-Requested-With': 'XMLHttpRequest',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
}

def get_free_proxies():
    """Load free proxies from file"""
    try:
        with open('proxies.txt', 'r') as f:
            proxies = [p.strip() for p in f.readlines() if p.strip() and ':' in p]
        return list(set(proxies))  # Remove duplicates
    except:
        return []

def test_proxy(proxy, scraper):
    """Test if proxy works with SportyBet"""
    try:
        proxy_dict = {
            'http': f'http://{proxy}',
            'https': f'http://{proxy}'
        }
        
        # Test with lightweight endpoint
        test_url = SPORTYBET_ENDPOINTS['broadcast_config']
        response = scraper.get(
            test_url,
            headers=HEADERS,
            proxies=proxy_dict,
            timeout=15
        )
        
        if response.status_code == 200:
            return proxy_dict
        return None
    except:
        return None

def scrape_with_proxy(endpoint_name, endpoint_url, scraper, proxy_dict):
    """Scrape specific endpoint using proxy"""
    try:
        response = scraper.get(
            endpoint_url,
            headers=HEADERS,
            proxies=proxy_dict,
            timeout=30
        )
        
        if response.status_code == 200:
            try:
                return response.json()
            except:
                return {'text': response.text[:1000]}
        else:
            return {'error': f'Status {response.status_code}'}
            
    except Exception as e:
        return {'error': str(e)}

def scrape_with_selenium():
    """Fallback: Use headless browser if proxies fail"""
    print("Trying Selenium fallback...")
    
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument(f'--user-agent={HEADERS["User-Agent"]}')
    
    try:
        service = Service('/usr/bin/chromedriver')
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        driver.get('https://www.sportybet.com/tz/m/sport/football')
        time.sleep(10)
        
        # Extract via JavaScript
        data = driver.execute_script("""
            const matches = [];
            document.querySelectorAll('.event-item, [data-testid="event"]').forEach(el => {
                try {
                    const teams = el.querySelectorAll('.team-name, [class*="team"]');
                    const odds = el.querySelectorAll('.odd, button');
                    if (teams.length >= 2 && odds.length >= 3) {
                        matches.push({
                            match: teams[0].innerText + ' vs ' + teams[1].innerText,
                            home: odds[0].innerText,
                            draw: odds[1].innerText,
                            away: odds[2].innerText
                        });
                    }
                } catch(e) {}
            });
            return matches;
        """)
        
        driver.quit()
        return {'selenium_matches': data}
        
    except Exception as e:
        try:
            driver.save_screenshot('error.png')
            driver.quit()
        except:
            pass
        return {'error': str(e)}

def main():
    print("=" * 50)
    print("SportyBet Scraper with Free Proxies")
    print("=" * 50)
    
    # Create cloudscraper instance
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'android',
            'mobile': True
        },
        delay=5
    )
    
    # Load proxies
    proxies = get_free_proxies()
    print(f"Loaded {len(proxies)} free proxies")
    
    # Find working proxy
    working_proxy = None
    if proxies:
        test_sample = random.sample(proxies, min(10, len(proxies)))
        for proxy in test_sample:
            print(f"Testing proxy: {proxy}")
            result = test_proxy(proxy, scraper)
            if result:
                working_proxy = result
                print(f"✅ Working proxy found: {proxy}")
                break
            time.sleep(1)
    
    # Scrape all endpoints
    all_data = {}
    
    for name, url in SPORTYBET_ENDPOINTS.items():
        print(f"\nScraping: {name}")
        
        if working_proxy:
            data = scrape_with_proxy(name, url, scraper, working_proxy)
        else:
            # Try direct (will likely fail with 403)
            try:
                response = scraper.get(url, headers=HEADERS, timeout=10)
                data = response.json() if response.status_code == 200 else {'error': response.status_code}
            except Exception as e:
                data = {'error': str(e)}
        
        all_data[name] = {
            'url': url,
            'data': data,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        print(f"Result: {'✅ Success' if 'error' not in data else '❌ ' + str(data['error'])}")
        time.sleep(2)  # Be nice to server
    
    # Save results
    with open('odds.json', 'w') as f:
        json.dump(all_data, f, indent=2)
    
    print(f"\n{'=' * 50}")
    print(f"Saved results for {len(all_data)} endpoints")
    print("Check odds.json for data")
    
    # If all failed, try Selenium
    if all('error' in v['data'] for v in all_data.values()):
        print("\nAll API endpoints failed. Trying Selenium...")
        selenium_data = scrape_with_selenium()
        all_data['selenium_fallback'] = selenium_data
        
        with open('odds.json', 'w') as f:
            json.dump(all_data, f, indent=2)

if __name__ == '__main__':
    main()
                       
