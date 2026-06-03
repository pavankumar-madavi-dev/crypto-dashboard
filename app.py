from flask import Flask, render_template_string, jsonify
import requests
import os
import threading
import json

try:
    import websocket
    WS_AVAILABLE = True
except:
    WS_AVAILABLE = False

app = Flask(__name__)

prices = {
    "BTCUSDT": {"name":"BTC","price":"0","change":"0","source":"loading"},
    "ETHUSDT": {"name":"ETH","price":"0","change":"0","source":"loading"},
    "BNBUSDT": {"name":"BNB","price":"0","change":"0","source":"loading"},
    "SOLUSDT": {"name":"SOL","price":"0","change":"0","source":"loading"},
    "XRPUSDT": {"name":"XRP","price":"0","change":"0","source":"loading"},
}

def fetch_coingecko():
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            "vs_currency": "usd",
            "ids": "bitcoin,ethereum,binancecoin,solana,ripple",
        }
        r = requests.get(url, params=params, timeout=10).json()
        mapping = {
            "bitcoin":"BTCUSDT","ethereum":"ETHUSDT",
            "binancecoin":"BNBUSDT","solana":"SOLUSDT","ripple":"XRPUSDT"
        }
        for c in r:
            key = mapping.get(c["id"])
            if key:
                prices[key]["price"] = f"{c['current_price']:,.2f}"
                prices[key]["change"] = f"{c['price_change_percentage_24h']:.2f}"
                prices[key]["source"] = "coingecko"
    except Exception as e:
        print("CoinGecko error:", e)

def coingecko_loop():
    while True:
        fetch_coingecko()
        import time
        time.sleep(15)

def on_message(ws, message):
    data = json.loads(message)
    if "data" in data:
        d = data["data"]
        symbol = d.get("s")
        if symbol in prices:
            prices[symbol]["price"] = f"{float(d['c']):,.2f}"
            prices[symbol]["change"] = f"{float(d['P']):.2f}"
            prices[symbol]["source"] = "binance"

def on_close(ws, a, b):
    import time
    time.sleep(5)
    start_ws()

def start_ws():
    try:
        streams = "btcusdt@ticker/ethusdt@ticker/bnbusdt@ticker/solusdt@ticker/xrpusdt@ticker"
        url = f"wss://stream.binance.com:9443/stream?streams={streams}"
        ws = websocket.WebSocketApp(url, on_message=on_message, on_close=on_close)
        ws.run_forever()
    except:
        pass

fetch_coingecko()

t1 = threading.Thread(target=coingecko_loop, daemon=True)
t1.start()

if WS_AVAILABLE:
    t2 = threading.Thread(target=start_ws, daemon=True)
    t2.start()

HTML = '''
<!DOCTYPE html>
<html>
<head>
<title>Crypto Dashboard</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
*{box-sizing:border-box;}
body{background:#0a0a0a;color:#fff;font-family:Arial;padding:10px;margin:0;}
h1{color:#00ff88;text-align:center;font-size:22px;margin:15px 0 3px;}
.sub{text-align:center;color:#888;font-size:13px;margin:0 0 5px;}
.live{color:#00ff88;font-size:13px;text-align:center;margin-bottom:12px;}
.card{background:#1a1a2e;border-radius:12px;padding:15px;margin:8px 0;border:1px solid #333;}
.coin{font-size:15px;font-weight:bold;color:#00ff88;}
.price{font-size:30px;color:#fff;margin:5px 0;font-weight:bold;}
.up{color:#00ff88;font-size:15px;}
.down{color:#ff4444;font-size:15px;}
.src{font-size:10px;color:#555;margin-top:3px;}
.footer{text-align:center;color:#444;font-size:11px;margin-top:15px;}
</style>
</head>
<body>
<h1>🚀 Crypto Dashboard</h1>
<p class="sub">by pavankumar-madavi-dev</p>
<p class="live">🟢 LIVE Real-time Prices</p>
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
          <div class="coin">📌 ${p.name}</div>
          <div class="price">$${p.price}</div>
          <div class="${up?'up':'down'}">${up?'▲':'▼'} ${p.change}%</div>
          <div class="src">source: ${p.source}</div>
        </div>`;
      });
      document.getElementById('dashboard').innerHTML = html;
      document.getElementById('footer').innerText =
        'Updated: ' + new Date().toLocaleTimeString();
    });
}
update();
setInterval(update, 1000);
</script>
</body>
</html>
'''

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/api/prices")
def api_prices():
    return jsonify(prices)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
