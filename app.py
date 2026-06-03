from flask import Flask, render_template_string, jsonify
import requests
import os
import hmac
import hashlib
import time

app = Flask(__name__)

API_KEY = os.environ.get("BINANCE_API_KEY", "")
SECRET = os.environ.get("BINANCE_SECRET", "")

prices = {
    "BTCUSDT": {"name":"BTC","price":"0","change":"0","high":"0","low":"0","volume":"0","funding":"0"},
    "ETHUSDT": {"name":"ETH","price":"0","change":"0","high":"0","low":"0","volume":"0","funding":"0"},
    "BNBUSDT": {"name":"BNB","price":"0","change":"0","high":"0","low":"0","volume":"0","funding":"0"},
    "SOLUSDT": {"name":"SOL","price":"0","change":"0","high":"0","low":"0","volume":"0","funding":"0"},
    "XRPUSDT": {"name":"XRP","price":"0","change":"0","high":"0","low":"0","volume":"0","funding":"0"},
}

def fetch_binance():
    try:
        headers = {"X-MBX-APIKEY": API_KEY}
        symbols = ["BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","XRPUSDT"]
        for symbol in symbols:
            # Futures Mark Price
            url = f"https://fapi.binance.com/fapi/v1/ticker/24hr?symbol={symbol}"
            r = requests.get(url, headers=headers, timeout=5).json()
            prices[symbol]["price"] = f"{float(r['lastPrice']):,.2f}"
            prices[symbol]["change"] = f"{float(r['priceChangePercent']):.2f}"
            prices[symbol]["high"] = f"{float(r['highPrice']):,.2f}"
            prices[symbol]["low"] = f"{float(r['lowPrice']):,.2f}"
            prices[symbol]["volume"] = f"{float(r['volume']):,.0f}"

            # Funding Rate
            url2 = f"https://fapi.binance.com/fapi/v1/fundingRate?symbol={symbol}&limit=1"
            r2 = requests.get(url2, timeout=5).json()
            if r2:
                prices[symbol]["funding"] = f"{float(r2[0]['fundingRate'])*100:.4f}%"
    except Exception as e:
        print("Binance error:", e)
        fetch_coingecko()

def fetch_coingecko():
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
    except Exception as e:
        print("CoinGecko error:", e)

def get_signal(change, price_str):
    change = float(change)
    if change < -3:
        return "STRONG BUY 🟢🟢", "buy"
    elif change < -1:
        return "BUY 🟢", "buy"
    elif change > 3:
        return "STRONG SELL 🔴🔴", "sell"
    elif change > 1:
        return "SELL 🔴", "sell"
    else:
        return "HOLD 🟡", "hold"

import threading
def update_loop():
    while True:
        fetch_binance()
        time.sleep(10)

t = threading.Thread(target=update_loop, daemon=True)
t.start()

HTML = '''
<!DOCTYPE html>
<html>
<head>
<title>Crypto Trading Dashboard</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
*{box-sizing:border-box;}
body{background:#0a0a0a;color:#fff;font-family:Arial;padding:10px;margin:0;}
h1{color:#00ff88;text-align:center;font-size:20px;margin:10px 0 3px;}
.sub{text-align:center;color:#888;font-size:12px;margin:0 0 5px;}
.live{color:#00ff88;font-size:12px;text-align:center;margin-bottom:10px;}
.card{background:#1a1a2e;border-radius:12px;padding:12px;margin:8px 0;border:1px solid #333;}
.coin{font-size:14px;font-weight:bold;color:#00ff88;}
.price{font-size:28px;color:#fff;margin:4px 0;font-weight:bold;}
.up{color:#00ff88;font-size:14px;}
.down{color:#ff4444;font-size:14px;}
.info{font-size:12px;color:#888;margin:3px 0;}
.buy{background:#00ff8822;padding:6px 10px;border-radius:5px;margin-top:6px;font-size:13px;}
.sell{background:#ff444422;padding:6px 10px;border-radius:5px;margin-top:6px;font-size:13px;}
.hold{background:#ffaa0022;padding:6px 10px;border-radius:5px;margin-top:6px;font-size:13px;}
.footer{text-align:center;color:#444;font-size:11px;margin-top:10px;}
</style>
</head>
<body>
<h1>🚀 Crypto Trading Dashboard</h1>
<p class="sub">by pavankumar-madavi-dev</p>
<p class="live">🟢 LIVE — Binance Futures Data</p>
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
        const sc = p.signal_class;
        html += `
        <div class="card">
          <div class="coin">📌 ${p.name}/USDT</div>
          <div class="price">$${p.price}</div>
          <div class="${up?'up':'down'}">${up?'▲':'▼'} ${p.change}%</div>
          <div class="info">📈 H: $${p.high} | 📉 L: $${p.low}</div>
          <div class="info">💰 Funding: ${p.funding}</div>
          <div class="${sc}">📊 Signal: ${p.signal}</div>
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
        signal, sc = get_signal(v["change"], v["price"])
        result[k] = {**v, "signal": signal, "signal_class": sc}
    return jsonify(result)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
