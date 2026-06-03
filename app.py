from flask import Flask, render_template_string, jsonify
import requests
import os
import threading
import time

app = Flask(__name__)

API_KEY = os.environ.get("BINANCE_API_KEY", "")
SECRET = os.environ.get("BINANCE_SECRET", "")
TG_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TG_CHAT = os.environ.get("TELEGRAM_CHAT_ID", "")

prices = {
    "BTCUSDT": {"name":"BTC","price":"0","change":"0","high":"0","low":"0","funding":"0"},
    "ETHUSDT": {"name":"ETH","price":"0","change":"0","high":"0","low":"0","funding":"0"},
    "BNBUSDT": {"name":"BNB","price":"0","change":"0","high":"0","low":"0","funding":"0"},
    "SOLUSDT": {"name":"SOL","price":"0","change":"0","high":"0","low":"0","funding":"0"},
    "XRPUSDT": {"name":"XRP","price":"0","change":"0","high":"0","low":"0","funding":"0"},
}

last_signals = {}

def get_signal(change):
    c = float(change)
    if c < -3:
        return "STRONG BUY 🟢🟢", "buy", "strong"
    elif c < -1:
        return "BUY 🟢", "buy", "normal"
    elif c > 3:
        return "STRONG SELL 🔴🔴", "sell", "strong"
    elif c > 1:
        return "SELL 🔴", "sell", "normal"
    else:
        return "HOLD 🟡", "hold", "normal"

def get_sl_target(price, signal_class):
    p = float(price.replace(",",""))
    if signal_class == "buy":
        sl = p * 0.98
        t1 = p * 1.02
        t2 = p * 1.04
    elif signal_class == "sell":
        sl = p * 1.02
        t1 = p * 0.98
        t2 = p * 0.96
    else:
        sl = p * 0.99
        t1 = p * 1.01
        t2 = p * 1.02
    return f"{sl:,.2f}", f"{t1:,.2f}", f"{t2:,.2f}"

def send_telegram(msg):
    try:
        if TG_TOKEN and TG_CHAT:
            url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
            requests.post(url, data={"chat_id": TG_CHAT, "text": msg, "parse_mode": "HTML"}, timeout=5)
    except:
        pass

def fetch_data():
    try:
        headers = {"X-MBX-APIKEY": API_KEY}
        for symbol in prices.keys():
            url = f"https://fapi.binance.com/fapi/v1/ticker/24hr?symbol={symbol}"
            r = requests.get(url, headers=headers, timeout=5).json()
            prices[symbol]["price"] = f"{float(r['lastPrice']):,.2f}"
            prices[symbol]["change"] = f"{float(r['priceChangePercent']):.2f}"
            prices[symbol]["high"] = f"{float(r['highPrice']):,.2f}"
            prices[symbol]["low"] = f"{float(r['lowPrice']):,.2f}"
    except:
        try:
            url = "https://api.coingecko.com/api/v3/coins/markets"
            params = {"vs_currency":"usd","ids":"bitcoin,ethereum,binancecoin,solana,ripple"}
            r = requests.get(url, params=params, timeout=10).json()
            mapping = {"bitcoin":"BTCUSDT","ethereum":"ETHUSDT","binancecoin":"BNBUSDT","solana":"SOLUSDT","ripple":"XRPUSDT"}
            for c in r:
                key = mapping.get(c["id"])
                if key:
                    prices[key]["price"] = f"{c['current_price']:,.2f}"
                    prices[key]["change"] = f"{c['price_change_percentage_24h']:.2f}"
                    prices[key]["high"] = f"{c['high_24h']:,.2f}"
                    prices[key]["low"] = f"{c['low_24h']:,.2f}"
        except:
            pass

def check_and_send_signals():
    for symbol, data in prices.items():
        signal, sc, strength = get_signal(data["change"])
        sl, t1, t2 = get_sl_target(data["price"], sc)
        prev = last_signals.get(symbol, "")
        if signal != prev and strength == "strong":
            last_signals[symbol] = signal
            msg = f"""🚀 <b>Global Trading Signal</b>

📌 <b>{data['name']}/USDT</b>
💰 Price: <b>${data['price']}</b>
📊 Change: {data['change']}%

🎯 Signal: <b>{signal}</b>

📉 Stop Loss: <b>${sl}</b>
🎯 Target 1: <b>${t1}</b>
🎯 Target 2: <b>${t2}</b>

⚠️ Trade at your own risk!
"""
            send_telegram(msg)

def update_loop():
    while True:
        fetch_data()
        check_and_send_signals()
        time.sleep(15)

t = threading.Thread(target=update_loop, daemon=True)
t.start()

HTML = '''
<!DOCTYPE html>
<html>
<head>
<title>Global Trading Dashboard</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
*{box-sizing:border-box;}
body{background:#0a0a0a;color:#fff;font-family:Arial;padding:10px;margin:0;}
h1{color:#00ff88;text-align:center;font-size:20px;margin:10px 0 3px;}
.sub{text-align:center;color:#888;font-size:12px;margin:0 0 5px;}
.live{color:#00ff88;font-size:12px;text-align:center;margin-bottom:10px;}
.card{background:#1a1a2e;border-radius:12px;padding:12px;margin:8px 0;border:1px solid #333;}
.coin{font-size:14px;font-weight:bold;color:#00ff88;}
.price{font-size:26px;color:#fff;margin:4px 0;font-weight:bold;}
.up{color:#00ff88;font-size:14px;}
.down{color:#ff4444;font-size:14px;}
.info{font-size:12px;color:#888;margin:3px 0;}
.sl{font-size:12px;color:#ff4444;margin:2px 0;}
.target{font-size:12px;color:#00ff88;margin:2px 0;}
.buy{background:#00ff8822;padding:6px 10px;border-radius:5px;margin-top:6px;font-size:13px;font-weight:bold;}
.sell{background:#ff444422;padding:6px 10px;border-radius:5px;margin-top:6px;font-size:13px;font-weight:bold;}
.hold{background:#ffaa0022;padding:6px 10px;border-radius:5px;margin-top:6px;font-size:13px;}
.footer{text-align:center;color:#444;font-size:11px;margin-top:10px;}
</style>
</head>
<body>
<h1>🚀 Global Trading Dashboard</h1>
<p class="sub">Powered by Binance | Free Signals</p>
<p class="live">🟢 LIVE Real-time Signals</p>
<div id="dashboard"></div>
<div class="footer" id="footer"></div>
<script>
function update() {
  fetch('/api/prices')
    .then(r => r.json())
    .then(data => {
      let html = '';
      Object.values(data).forEach(p => {
        const up = parseFloat(p.change) >= 0;
        html += `
        <div class="card">
          <div class="coin">📌 ${p.name}/USDT</div>
          <div class="price">$${p.price}</div>
          <div class="${up?'up':'down'}">${up?'▲':'▼'} ${p.change}%</div>
          <div class="info">📈 H: $${p.high} | 📉 L: $${p.low}</div>
          <div class="sl">🛑 Stop Loss: $${p.sl}</div>
          <div class="target">🎯 T1: $${p.t1} | T2: $${p.t2}</div>
          <div class="${p.signal_class}">📊 ${p.signal}</div>
        </div>`;
      });
      document.getElementById('dashboard').innerHTML = html;
      document.getElementById('footer').innerText =
        'Updated: ' + new Date().toLocaleTimeString();
    });
}
update();
setInterval(update, 2000);
</script>
</body>
</html>
'''

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/api/prices")
def api_prices():
    result = {}
    for k, v in prices.items():
        signal, sc, strength = get_signal(v["change"])
        sl, t1, t2 = get_sl_target(v["price"], sc)
        result[k] = {**v, "signal": signal, "signal_class": sc, "sl": sl, "t1": t1, "t2": t2}
    return jsonify(result)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
