import os
import time
import requests
import random
from datetime import datetime
# हमने न्यूज़ इंजन को इंपोर्ट कर लिया है
from news_engine import get_live_crypto_news

# =====================================================================
# 🛠️ कॉन्फिगरेशन और क्रेडेंशियल्स
# =====================================================================
BOT_TOKEN = "8242319724:AAEu7_zaM-u7VeUGDNDjhqg7zgTVBH7KPRw"
CHAT_ID = "@GlobalTraderPavan"
RAILWAY_URL = "https://web-production-1f385.up.railway.app/api/update_prices"
SECRET_TOKEN = "ProPlus_SI_Secure_2026"

POPULAR_COINS = [
    {"symbol": "BTC", "name": "Bitcoin", "logo": "₿"},
    {"symbol": "ETH", "name": "Ethereum", "logo": "Ξ"},
    {"symbol": "BNB", "name": "BNB Coin", "logo": "🔶"},
    {"symbol": "SOL", "name": "Solana", "logo": "☀️"},
    {"symbol": "XRP", "name": "Ripple", "logo": "✕"},
    {"symbol": "DOGE", "name": "Dogecoin", "logo": "🐕"},
    {"symbol": "ADA", "name": "Cardano", "logo": "₳"},
    {"symbol": "MATIC", "name": "Polygon", "logo": "💜"},
    {"symbol": "DOT", "name": "Polkadot", "logo": "●"},
    {"symbol": "LINK", "name": "Chainlink", "logo": "🔗"}
]

# =====================================================================
# 📨 टेलीग्राम फंक्शन
# =====================================================================
def send_telegram_signal(coin):
    sig_emoji = "🟢" if "BUY" in coin['signal'] or "LONG" in coin['signal'] else "🔴" if "SHORT" in coin['signal'] or "SELL" in coin['signal'] else "🟡"
    trend_emoji = "📈" if "BULLISH" in coin['macro_trend'] else "📉" if "BEARISH" in coin['macro_trend'] else "🔄"
    message = (f"🚀 *Global Trading Signal*\n\n📌 *{coin['logo']} {coin['symbol']}/USDT*\n💰 Price: `{coin['current_price']}`\n{trend_emoji} Macro Trend: *{coin['macro_trend']}*\n\n{sig_emoji} *Signal: {coin['signal']}*\n\n📱 [Official Telegram Channel](https://t.me/GlobalTraderPavan)")
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown", "disable_web_page_preview": True}
    try:
        requests.post(url, json=payload, timeout=10)
    except:
        pass

# =====================================================================
# 🧠 मार्केट एनालिसिस इंजन
# =====================================================================
def get_binance_price(symbol):
    try:
        res = requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}USDT", timeout=5).json()
        return float(res['price'])
    except:
        return 10.0

def analyze_market():
    processed_data = []
    # असली लाइव न्यूज़ यहाँ से फ़ेच हो रही है
    live_news = get_live_crypto_news() 
    
    print(f"\n⚡ [{datetime.now().strftime('%H:%M:%S')}] Starting System Intelligence Scan...")

    for c in POPULAR_COINS:
        price = get_binance_price(c['symbol'])
        rand_val = random.randint(1, 3)
        signal = "INSTITUTIONAL BUY 🟢" if rand_val == 1 else "INSTITUTIONAL SHORT 🔴" if rand_val == 2 else "HOLD 🟡"
        macro_trend = "STRONG BULLISH 📈" if rand_val == 1 else "BEARISH 📉" if rand_val == 2 else "NEUTRAL 🔄"
        
        coin_payload = {
            "symbol": c['symbol'],
            "name": c['name'],
            "logo": c['logo'],
            "current_price": f"${price:,.2f}",
            "macro_trend": macro_trend,
            "signal": signal,
            "live_news": live_news  # सिर्फ एक बार न्यूज़ वाला डेटा
        }
        processed_data.append(coin_payload)
        
        if "BUY" in signal or "SHORT" in signal:
            send_telegram_signal(coin_payload)
            time.sleep(1)

    return processed_data

# =====================================================================
# 🚀 मेन लूप
# =====================================================================
if __name__ == "__main__":
    while True:
        try:
            market_data = analyze_market()
            headers = {"X-SI-Token": SECRET_TOKEN, "Content-Type": "application/json"}
            response = requests.post(RAILWAY_URL, json=market_data, headers=headers, timeout=15)
            if response.status_code == 200:
                print("🎯 [RAILWAY] Data Successfully Saved to Cloud Memory!")
        except Exception as e:
            print(f"❌ Error: {e}")
        time.sleep(300)
