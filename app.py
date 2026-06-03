from flask import Flask, render_template_string, jsonify
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
body{background:#0a0a0a;color:#fff;font-family:Arial;padding:10px;margin:0;}
h1{color:#00ff88;text-align:center;font-size:24px;margin:15px 0 5px;}
p{text-align:center;color:#888;margin:0 0 10px;}
.card{background:#1a1a2e;border-radius:10px;padding:15px;margin:10px 0;border:1px solid #333;transition:all 0.3s;}
.coin{font-size:18px;font-weight:bold;color:#00ff88;}
.price{font-size:26px;color:#fff;margin:5px 0;font-weight:bold;}
.up{color:#00ff88;}
.down{color:#ff4444;}
.buy{background:#00ff8822;padding:8px;border-radius:5px;margin-top:5px;}
.sell{background:#ff444422;padding:8px;border-radius:5px;margin-top:5px;}
.hold{background:#ffaa0022;padding:8px;border-radius:5px;margin-top:5px;}
.timer{text-align:center;color:#555;font-size:12px;margin-top:15px;}
.live{color:#00ff88;font-size:12px;text-align:center;}
.flash{animation:flash 0.5s;}
@keyframes flash{0%{background:#00ff8833;}100%{background:#1a1a2e;}}
</style>
</head>
<body>
<h1>🚀 Crypto Dashboard</h1>
<p>by pavankumar-madavi-dev</p>
<p class="live">🟢 LIVE — Auto updates every 15 sec</p>
<div id="dashboard"></div>
<div class="timer" id="timer">Next update in: 15s</div>

<script>
function updateDashboard() {
  fetch('/api/prices')
    .then(r => r.json())
    .then(coins => {
      let html = '';
      coins.forEach(coin => {
        html += `
        <div class="card flash">
          <div class="coin">📌 ${coin.name}</div>
          <div class="price">💰 $${coin.price}</div>
          <div class="${coin.change > 0 ? 'up' : 'down'}">
            ${coin.change > 0 ? '▲' : '▼'} ${coin.change}%
          </div>
          <div>📈 High: $${coin.high} | 📉 Low: $${coin.low}</div>
        </div>`;
      });
      document.getElementById('dashboard').innerHTML = html;
    });
}

let countdown = 15;
setInterval(() => {
  countdown--;
  document.getElementById('timer').innerText = 'Next update in: ' + countdown + 's';
  if(countdown <= 0) {
    countdown = 15;
    updateDashboard();
  }
}, 1000);

updateDashboard();
</script>
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
    except:
        return []

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/api/prices")
def prices():
    return jsonify(get_crypto_data())

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
