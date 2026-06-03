from flask import Flask, render_template_string
import requests

app = Flask(__name__)

HTML = '''
<!DOCTYPE html>
<html>
<head>
<title>Crypto Dashboard</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{background:#0a0a0a;color:#fff;font-family:Arial;padding:10px;}
h1{color:#00ff88;text-align:center;}
.card{background:#1a1a2e;border-radius:10px;padding:15px;margin:10px 0;}
.coin{font-size:18px;font-weight:bold;color:#00ff88;}
.price{font-size:24px;color:#fff;}
.up{color:#00ff88;} .down{color:#ff4444;}
.signal-buy{background:#00ff8833;padding:5px;border-radius:5px;}
.signal-sell{background:#ff444433;padding:5px;border-radius:5px;}
.signal-hold{background:#ffaa0033;padding:5px;border-radius:5px;}
</style>
</head>
<body>
<h1>🚀 Crypto Dashboard</h1>
<p style="text-align:center;color:#888;">by pavankumar-madavi-dev</p>
{% for coin in coins %}
<div class="card">
  <div class="coin">{{ coin.name }}</div>
  <div class="price">${{ coin.price }}</div>
  <div class="{{ 'up' if coin.change > 0 else 'down' }}">
    {{ '▲' if coin.change > 0 else '▼' }} {{ coin.change }}%
  </div>
  <div class="signal-{{ coin.signal_class }}">
    Signal: {{ coin.signal }} | RSI: {{ coin.rsi }}
  </div>
</div>
{% endfor %}
</body>
</html>
'''

def get_data(symbol):
    try:
        url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
        r = requests.get(url, timeout=5).json()
        price = float(r["lastPrice"])
        change = float(r["priceChangePercent"])

        url2 = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1h&limit=15"
        data = requests.get(url2, timeout=5).json()
        closes = [float(c[4]) for c in data]
        gains, losses = [], []
        for i in range(1, len(closes)):
            diff = closes[i] - closes[i-1]
            gains.append(max(diff, 0))
            losses.append(max(-diff, 0))
        avg_gain = sum(gains[-14:]) / 14
        avg_loss = sum(losses[-14:]) / 14
        rsi = 100 if avg_loss == 0 else 100 - (100 / (1 + avg_gain/avg_loss))
        rsi = round(rsi, 1)

        if rsi < 30:
            signal, sc = "BUY 🟢", "buy"
        elif rsi > 70:
            signal, sc = "SELL 🔴", "sell"
        else:
            signal, sc = "HOLD 🟡", "hold"

        return {"name": symbol, "price": f"{price:,.2f}", "change": round(change, 2), "rsi": rsi, "signal": signal, "signal_class": sc}
    except:
        return {"name": symbol, "price": "N/A", "change": 0, "rsi": 0, "signal": "N/A", "signal_class": "hold"}

@app.route("/")
def index():
    coins = [get_data(s) for s in ["BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","XRPUSDT"]]
    return render_template_string(HTML, coins=coins)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
