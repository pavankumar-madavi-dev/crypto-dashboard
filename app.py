from flask import Flask, render_template_string
import requests
import os

app = Flask(__name__)

HTML = '''
<!DOCTYPE html>
<html>
<head>
<title>Crypto Dashboard</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{background:#0a0a0a;color:#fff;font-family:Arial;padding:10px;}
h1{color:#00ff88;text-align:center;font-size:24px;}
p{text-align:center;color:#888;}
.card{background:#1a1a2e;border-radius:10px;padding:15px;margin:10px 0;border:1px solid #333;}
.coin{font-size:18px;font-weight:bold;color:#00ff88;}
.price{font-size:22px;color:#fff;margin:5px 0;}
.up{color:#00ff88;}
.down{color:#ff4444;}
.footer{text-align:center;color:#555;margin-top:20px;font-size:12px;}
</style>
</head>
<body>
<h1>🚀 Crypto Dashboard</h1>
<p>by pavankumar-madavi-dev</p>
{% for coin in coins %}
<div class="card">
  <div class="coin">📌 {{ coin.name }}</div>
  <div class="price">💰 ${{ coin.price }}</div>
  <div class="{{ 'up' if coin.change > 0 else 'down' }}">
    {{ '▲' if coin.change > 0 else '▼' }} {{ coin.change }}%
  </div>
  <div>📈 High: ${{ coin.high }} | 📉 Low: ${{ coin.low }}</div>
</div>
{% endfor %}
<div class="footer">Powered by CoinGecko API</div>
</body>
</html>
'''

def get_crypto_data():
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            "vs_currency": "usd",
            "ids": "bitcoin,ethereum,binancecoin,solana,ripple",
            "order": "market_cap_desc"
        }
        r = requests.get(url, params=params, timeout=10).json()
        coins = []
        for c in r:
            coins.append({
                "name": c["symbol"].upper(),
                "price": f"{c['current_price']:,.2f}",
                "change": round(c["price_change_percentage_24h"], 2),
                "high": f"{c['high_24h']:,.2f}",
                "low": f"{c['low_24h']:,.2f}"
            })
        return coins
    except Exception as e:
        return []

@app.route("/")
def index():
    coins = get_crypto_data()
    return render_template_string(HTML, coins=coins)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
