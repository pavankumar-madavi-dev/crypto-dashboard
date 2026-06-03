from flask import Flask, render_template_string, jsonify
import requests
import os
import threading
import json
import websocket

app = Flask(__name__)

# Live prices store
prices = {
    "BTCUSDT": {"price": "0", "change": "0"},
    "ETHUSDT": {"price": "0", "change": "0"},
    "BNBUSDT": {"price": "0", "change": "0"},
    "SOLUSDT": {"price": "0", "change": "0"},
    "XRPUSDT": {"price": "0", "change": "0"},
}

def on_message(ws, message):
    data = json.loads(message)
    if "data" in data:
        d = data["data"]
        symbol = d["s"]
        if symbol in prices:
            prices[symbol]["price"] = f"{float(d['c']):,.2f}"
            prices[symbol]["change"] = f"{float(d['P']):.2f}"

def on_error(ws, error):
    print("Error:", error)

def on_close(ws, a, b):
    print("WebSocket closed, reconnecting...")
    start_ws()

def on_open(ws):
    print("WebSocket connected!")

def start_ws():
    streams = "btcusdt@ticker/ethusdt@ticker/bnbusdt@ticker/solusdt@ticker/xrpusdt@ticker"
    url = f"wss://stream.binance.com:9443/stream?streams={streams}"
    ws = websocket.WebSocketApp(
        url,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
        on_open=on_open
    )
    ws.run_forever()

# Start WebSocket in background
t = threading.Thread(target=start_ws, daemon=True)
t.start()

HTML = '''
<!DOCTYPE html>
<html>
<head>
<title>Crypto Dashboard</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{background:#0a0a0a;color:#fff;font-family:Arial;padding:10px;margin:0;}
h1{color:#00ff88;text-align:center;font-size:24px;margin:15px 0 5px;}
p{text-align:center;color:#888;margin:0 0 5px;}
.live{color:#00ff88;font-size:13px;text-align:center;margin-bottom:10px;}
.card{background:#1a1a2e;border-radius:10px;padding:15px;margin:10px 0;border:1px solid #333;}
.coin{font-size:16px;font-weight:bold;color:#00ff88;}
.price{font-size:28px;color:#fff;margin:5px 0;font-weight:bold;}
.up{color:#00ff88;font-size:16px;}
.down{color:#ff4444;font-size:16px;}
.updated{font-size:11px;color:#555;text-align:center;margin-top:15px;}
</style>
</head>
<body>
<h1>🚀 Crypto Dashboard</h1>
<p>by pavankumar-madavi-dev</p>
<p class="live">🟢 LIVE — Real-time Binance prices</p>
<div id="dashboard"></div>
<div class="updated" id="updated"></div>

<script>
const coins = [
  {id:"BTCUSDT", name:"BTC"},
  {id:"ETHUSDT", name:"ETH"},
  {id:"BNBUSDT", name:"BNB"},
  {id:"SOLUSDT", name:"SOL"},
  {id:"XRPUSDT", name:"XRP"}
];

function updateDashboard() {
  fetch('/api/prices')
    .then(r => r.json())
    .then(data => {
      let html = '';
      coins.forEach(coin => {
        const p = data[coin.id];
        const up = parseFloat(p.change) >= 0;
        html += `
        <div class="card">
          <div class="coin">📌 ${coin.name}</div>
          <div class="price">💰 $${p.price}</div>
          <div class="${up ? 'up' : 'down'}">
            ${up ? '▲' : '▼'} ${p.change}%
          </div>
        </div>`;
      });
      document.getElementById('dashboard').innerHTML = html;
      const now = new Date();
      document.getElementById('updated').innerText =
        'Last updated: ' + now.toLocaleTimeString();
    });
}

updateDashboard();
setInterval(updateDashboard, 1000);
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
