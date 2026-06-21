cat > si_trader.py << 'PYEOF'
import os, time, requests
from datetime import datetime

BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
CHANNEL_ID = os.environ.get('TELEGRAM_CHANNEL_ID')
API_KEY = os.environ.get('BINANCE_API_KEY')

def get_price(symbol):
    try:
        r = requests.get(f'https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}', timeout=10)
        d = r.json()
        return float(d['lastPrice']), float(d['priceChangePercent'])
    except:
        return None, None

def send_signal():
    btc, btc_chg = get_price('BTCUSDT')
    eth, eth_chg = get_price('ETHUSDT')
    bnb, bnb_chg = get_price('BNBUSDT')
    sol, sol_chg = get_price('SOLUSDT')
    
    if not btc:
        print('Price fetch failed')
        return
    
    direction = 'LONG 📈' if btc_chg > 0 else 'SHORT 📉'
    entry_low = round(btc * 0.998, 0)
    entry_high = round(btc * 1.002, 0)
    target1 = round(btc * 1.02, 0)
    target2 = round(btc * 1.04, 0)
    sl = round(btc * 0.985, 0)
    
    msg = f"""📊 *SIGNAL ALERT — GlobalTraderPavan*
━━━━━━━━━━━━━━━━━━━━

🔶 *BTCUSDT — {direction}*

💰 *Live Price:* ${btc:,.0f} ({btc_chg:+.2f}%)
📍 *Entry Zone:* ${entry_low:,.0f} – ${entry_high:,.0f}
🎯 *Target 1:* ${target1:,.0f}
🎯 *Target 2:* ${target2:,.0f}
🛑 *Stop Loss:* ${sl:,.0f}

━━━━━━━━━━━━━━━━━━━━
📈 *Market Update:*
• ETH: ${eth:,.0f} ({eth_chg:+.2f}%)
• BNB: ${bnb:,.0f} ({bnb_chg:+.2f}%)
• SOL: ${sol:,.0f} ({sol_chg:+.2f}%)

━━━━━━━━━━━━━━━━━━━━
⏰ {datetime.now().strftime('%d %b %Y, %I:%M %p IST')}
⚡ Strategy: SMC Analysis
⚠️ Risk: 2% max per trade

🔗 [Binance Join करो](https://www.binance.com/activity/referral-entry/CPA?ref=CPA_009BQG4BOM)
📲 @GlobalTraderPavan
━━━━━━━━━━━━━━━━━━━━"""

    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    requests.post(url, json={
        'chat_id': CHANNEL_ID,
        'text': msg,
        'parse_mode': 'Markdown',
        'disable_web_page_preview': True
    })
    print(f'Signal sent at {datetime.now()}')

print('GlobalTraderPavan Signal Bot Started!')
while True:
    try:
        send_signal()
        time.sleep(3600)  # हर 1 घंटे में signal
    except Exception as e:
        print(f'Error: {e}')
        time.sleep(60)
PYEOF
