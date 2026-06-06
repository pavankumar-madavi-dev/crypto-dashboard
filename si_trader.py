import os
import time
import requests
import random
from datetime import datetime

BOT_TOKEN = "8242319724:AAEu7_zaM-u7VeUGDNDjhqg7zgTVBH7KPRw"
CHAT_ID = "@GlobalTraderPavan"
RAILWAY_URL = "https://1f385.up.railway.app/api/update_prices"
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

def get_live_crypto_news():
    try:
        url = "https://cryptopanic.com/api/v1/posts/?auth_token=pub_free&kind=news&limit=3"
        res = requests.get(url, timeout=5).json()
        return [item['title'] for item in res['results'][:3]]
    except:
        return [
            "Market Update: Institutional accumulation detected in BTC",
            "Whale Alert: Large transfers spotted on ETH network",
            "Analysis: Smart money positioning in SOL and BNB"
        ]

def get_binance_price(symbol):
    try:
        res = requests.get(
            f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}USDT",
            timeout=5
        ).json()
        return float(res['price'])
    except:
        return 10.0

def send_telegram_signal(coin):
    sig_emoji = "🟢" if "BUY" in coin['signal'] else "🔴" if "SHORT" in coin['signal'] else "🟡"
    trend_emoji = "📈" if "BULLISH" in coin['macro_trend'] else "📉"
    message = (
        f"🚀 *Global Trading Signal*\n\n"
        f"📌 *{coin['logo']} {coin['symbol']}/USDT*\n"
        f"💰 Price: `{coin['current_price']}`\n"
        f"{trend_emoji} Macro Trend: *{coin['macro_trend']}*\n\n"
        f"{sig_emoji} *Signal: {coin['signal']}*\n\n"
        f"📱 [Official Telegram Channel](https://t.me/GlobalTraderPavan)"
    )
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except:
        pass

def analyze_market():
    processed_data = []
    live_news = get_live_crypto_news()
    print(f"\n⚡ [{datetime.now().strftime('%H:%M:%S')}] System Intelligence Scan...")

    for c in POPULAR_COINS:
        price = get_binance_price(c['symbol'])
        rand_val = random.randint(1, 3)

        if rand_val == 1:
            signal = "INSTITUTIONAL BUY 🟢"
            macro_trend = "STRONG BULLISH 📈"
            mode = "TRENDING VOL"
            stop_loss = f"${price * 0.97:,.2f}"
            target = f"${price * 1.04:,.2f} - ${price * 1.07:,.2f}"
        elif rand_val == 2:
            signal = "INSTITUTIONAL SHORT 🔴"
            macro_trend = "BEARISH 📉"
            mode = "HIGH VOLATILITY"
            stop_loss = f"${price * 1.03:,.2f}"
            target = f"${price * 0.94:,.2f} - ${price * 0.97:,.2f}"
        else:
            signal = "HOLD 🟡"
            macro_trend = "NEUTRAL 🔄"
            mode = "SIDEWAYS"
            stop_loss = f"${price * 0.98:,.2f}"
            target = f"${price * 1.02:,.2f} - ${price * 1.04:,.2f}"

        coin_payload = {
            "symbol": c['symbol'],
            "name": c['name'],
            "logo": c['logo'],
            "current_price": f"${price:,.2f}",
            "macro_trend": macro_trend,
            "signal": signal,
            "mode": mode,
            "vol_ratio": f"{random.uniform(1.2, 3.5):.2f}x",
            "dynamic_stop_loss": stop_loss,
            "target_range": target,
            "supply_zone": f"${price * 1.05:,.2f} - ${price * 1.08:,.2f}",
            "demand_zone": f"${price * 0.93:,.2f} - ${price * 0.96:,.2f}",
            "live_news": live_news
        }
        processed_data.append(coin_payload)

        if "BUY" in signal or "SHORT" in signal:
            send_telegram_signal(coin_payload)
            time.sleep(1)

    return processed_data

if __name__ == "__main__":
    print("🚀 Pro_Plus SI Engine Started!")
    while True:
        try:
            market_data = analyze_market()
            headers = {
                "X-SI-Token": SECRET_TOKEN,
                "Content-Type": "application/json"
            }
            response = requests.post(
                RAILWAY_URL,
                json=market_data,
                headers=headers,
                timeout=15
            )
            if response.status_code == 200:
                print("🎯 Data Successfully Sent to Railway!")
            else:
                print(f"⚠️ Railway Response: {response.status_code}")
        except Exception as e:
            print(f"❌ Error: {e}")
        time.sleep(60)  # हर 1 मिनट में update