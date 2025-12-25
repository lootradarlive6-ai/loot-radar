import requests
from bs4 import BeautifulSoup
import os
import time
import random
from urllib.parse import urlparse

# --- 1. CONFIGURATION ---
try:
    TELEGRAM_TOKEN = os.environ['7993945188:AAHhH2cijvnXzFVOKUpnvBOGGEkD9H106Uw']
    TELEGRAM_CHAT_ID = os.environ['-1003680677026']
except KeyError:
    # Use empty strings if running locally without secrets
    TELEGRAM_TOKEN = ""
    TELEGRAM_CHAT_ID = ""

TRACKING_LIST = [
    {
        "name": "Apple iPhone 13",
        "url": "https://www.amazon.in/dp/B09G9HD6PD", 
        "target": 42000,
        "mrp": 59900
    },
    {
        "name": "Sony XM4 Headphones",
        "url": "https://www.amazon.in/dp/B0863TXGM3", 
        "target": 18000, 
        "mrp": 29990
    }
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}

def get_price_amazon(soup):
    try:
        price = soup.find(class_="a-price-whole")
        if price:
            return int(price.get_text().replace(',', '').replace('.', ''))
    except:
        pass
    return None

def get_price_flipkart(soup):
    try:
        price = soup.find("div", class_="_30jeq3")
        if not price:
            price = soup.find("div", class_="Nx9bqj")
        if price:
            return int(price.get_text().replace('₹', '').replace(',', '').replace('.', ''))
    except:
        pass
    return None

def send_telegram_alert(name, price, url, drop_percent, is_glitch=False):
    if is_glitch:
        title = "🔥💀 GLITCH DETECTED! (99% RISK)"
        advice = "RUN! BUY NOW!"
    else:
        title = "🚨 PRICE DROP ALERT"
        advice = "Price is below your target."

    message = (
        f"{title}\n\n"
        f"📦 *{name}*\n"
        f"💰 Price: ₹{price}\n"
        f"📉 Drop: *{drop_percent}% OFF*\n"
        f"💡 {advice}\n\n"
        f"👉 [Buy Now]({url})"
    )
    
    api_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    
    try:
        requests.post(api_url, json=payload)
        print(f"✅ Alert Sent for {name}!")
    except Exception as e:
        print(f"❌ Telegram Error: {e}")

def run_scanner():
    print(f"🔎 Starting Scan... ({len(TRACKING_LIST)} items)")
    
    for item in TRACKING_LIST:
        url = item['url']
        name = item['name']
        target = item['target']
        mrp = item['mrp']
        
        try:
            domain = urlparse(url).netloc
            time.sleep(random.randint(2, 5))
            
            page = requests.get(url, headers=HEADERS)
            soup = BeautifulSoup(page.content, 'html.parser')
            
            current_price = None
            if "amazon" in domain:
                current_price = get_price_amazon(soup)
            elif "flipkart" in domain:
                current_price = get_price_flipkart(soup)
            
            if current_price:
                drop_percent = int(((mrp - current_price) / mrp) * 100)
                # THIS WAS THE BROKEN LINE - FIXED NOW:
                print(f"   📦 {name}: ₹{current_price} ({drop_percent}% off)")

                if drop_percent >= 55:
                    send_telegram_alert(name, current_price, url, drop_percent, is_glitch=True)
                elif current_price <= target:
                    send_telegram_alert(name, current_price, url, drop_percent, is_glitch=False)
            else:
                print(f"   ⚠️ Could not read price for {name}")
                
        except Exception as e:
            print(f"   ❌ Error on {name}: {e}")

if __name__ == "__main__":
    run_scanner()
  
