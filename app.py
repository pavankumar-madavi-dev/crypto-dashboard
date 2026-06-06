from flask import Flask, render_template_string, jsonify, request
import os

app = Flask(__name__)
SECRET_TOKEN = "ProPlus_SI_Secure_2026"
live_market_data = []

HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pro_Plus System Intelligence | Institutional Analytics</title>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-main: #0B0E11;
            --bg-card: #161A1E;
            --border-color: #2B3139;
            --text-main: #EAECEF;
            --text-muted: #848E9C;
            --neon-green: #02C076;
            --neon-red: #F6465D;
            --neon-yellow: #F0B90B;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: "Inter", sans-serif; }
        body { background-color: var(--bg-main); color: var(--text-main); display: flex; flex-direction: column; min-height: 100vh; }
        .container { padding: 15px; flex-grow: 1; display: flex; flex-direction: column; }

        .ticker-wrap { width: 100%; background: #000; border-bottom: 1px solid var(--border-color); overflow: hidden; padding: 6px 0; font-family: "JetBrains Mono", monospace; font-size: 12px; }
        .ticker-move { display: flex; width: max-content; animation: ticker 25s linear infinite; }
        .ticker-item { padding: 0 20px; display: flex; gap: 8px; align-items: center; border-right: 1px solid #1F2226; }
        @keyframes ticker { 0% { transform: translate3d(0,0,0); } 100% { transform: translate3d(-33.33%,0,0); } }

        header { display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid var(--border-color); padding-bottom: 15px; margin-top: 15px; margin-bottom: 15px; }
        .brand-title { font-size: 20px; font-weight: 700; color: var(--neon-yellow); }
        .admin-badge { font-family: "JetBrains Mono", monospace; font-size: 11px; color: var(--text-muted); text-transform: uppercase; margin-top: 4px; }
        .admin-name { color: #fff; font-weight: bold; }
        .live-badge { background: rgba(2,192,118,0.1); border: 1px solid var(--neon-green); color: var(--neon-green); padding: 6px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; }
        .offline-badge { background: rgba(246,70,93,0.1); border: 1px solid var(--neon-red); color: var(--neon-red); padding: 6px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; }

        .news-box { background: rgba(240,185,11,0.04); border: 1px dashed rgba(240,185,11,0.25); border-radius: 6px; padding: 10px 15px; margin-bottom: 20px; overflow: hidden; display: flex; align-items: center; gap: 10px; }
        .news-label { background: var(--neon-yellow); color: #000; font-size: 11px; font-weight: 700; padding: 2px 6px; border-radius: 3px; white-space: nowrap; }
        .news-scroll { overflow: hidden; position: relative; width: 100%; height: 18px; }
        .news-track { position: absolute; width: 100%; animation: newsCycle 12s steps(3) infinite; }
        .news-item { height: 18px; line-height: 18px; font-size: 12px; color: #EAECEF; font-weight: 500; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }
        @keyframes newsCycle { 0%,30%{top:0} 33%,63%{top:-18px} 66%,96%{top:-36px} 100%{top:0} }

        .section-title { font-size: 1.1rem; margin-bottom: 12px; display: flex; align-items: center; gap: 6px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(310px, 1fr)); gap: 16px; margin-bottom: 25px; }
        .card { background-color: var(--bg-card); border: 1px solid var(--border-color); border-radius: 10px; padding: 16px; position: relative; overflow: hidden; }
        .card-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; }
        .symbol { font-size: 1.2rem; font-weight: 700; color: #fff; display: flex; align-items: center; gap: 6px; }
        .badge { font-size: 10px; font-weight: 700; padding: 4px 8px; border-radius: 4px; text-transform: uppercase; }
        .bg-side { background: rgba(240,185,11,0.12); color: var(--neon-yellow); border: 1px solid rgba(240,185,11,0.2); }
        .bg-vol { background: rgba(246,70,93,0.12); color: var(--neon-red); border: 1px solid rgba(246,70,93,0.2); }
        .metrics { display: flex; flex-direction: column; gap: 8px; font-size: 13px; }
        .row { display: flex; justify-content: space-between; align-items: center; background: rgba(255,255,255,0.01); padding: 6px 8px; border-radius: 6px; }
        .lbl { color: var(--text-muted); font-size: 12px; }
        .val { font-family: "JetBrains Mono", monospace; font-weight: 600; color: #fff; }
        .dev { border-top: 1px dashed var(--border-color); padding-top: 8px; margin-top: 4px; }
        .premium-locked { filter: blur(5px); pointer-events: none; user-select: none; }
        .lock-overlay { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(22,26,30,0.94); display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 20px; text-align: center; }
        .btn-premium { background: linear-gradient(135deg, var(--neon-yellow), #C99B00); color: #000; padding: 8px 16px; border: none; border-radius: 6px; font-weight: 700; font-size: 12px; text-decoration: none; margin-top: 10px; }

        /* CHART SECTION */
        .chart-section { margin-bottom: 25px; }
        .chart-controls { display: flex; gap: 8px; margin-bottom: 12px; flex-wrap: wrap; }
        .coin-btn { background: var(--bg-card); border: 1px solid var(--border-color); color: var(--text-muted); padding: 6px 14px; border-radius: 20px; font-size: 12px; cursor: pointer; font-weight: 600; transition: all 0.2s; }
        .coin-btn.active { background: var(--neon-yellow); color: #000; border-color: var(--neon-yellow); }
        .chart-frame { border: 1px solid var(--border-color); border-radius: 10px; overflow: hidden; }

        footer { border-top: 1px solid var(--border-color); padding: 15px 0; text-align: center; font-size: 11px; color: var(--text-muted); background: #000; }
        .footer-owner { color: var(--text-main); font-weight: 600; }
    </style>
</head>
<body>

<div class="ticker-wrap">
    <div class="ticker-move" id="live-ticker">
        <div class="ticker-item">⚡ Loading Live Ticker...</div>
    </div>
</div>

<div class="container">
    <header>
        <div class="brand-zone">
            <div class="brand-title">🚀 Pro_Plus System Intelligence</div>
            <div class="admin-badge">Global Architecture: <span class="admin-name">Pavankumar Madavi</span></div>
        </div>
        <div class="offline-badge" id="live-status">● SI ENGINE OFFLINE</div>
    </header>

    <div class="news-box">
        <div class="news-label">🚨 Institutional Feed</div>
        <div class="news-scroll">
            <div class="news-track" id="news-container">
                <div class="news-item">Waiting for Secure Feed...</div>
            </div>
        </div>
    </div>

    <h3 class="section-title" style="color: var(--neon-green);">📊 Free Institutional Signals</h3>
    <div class="grid" id="free-grid"></div>

    <h3 class="section-title" style="color: var(--neon-yellow);">🔒 Premium Alpha Circle (Advanced Analytics)</h3>
    <div class="grid" id="premium-grid"></div>

    <!-- LIVE CHART SECTION -->
    <div class="chart-section">
        <h3 class="section-title" style="color: var(--neon-yellow);">📈 Live TradingView Chart</h3>
        <div class="chart-controls" id="coin-buttons"></div>
        <div class="chart-frame">
            <iframe id="tv-chart"
                src="https://s.tradingview.com/widgetembed/?symbol=BINANCE:BTCUSDT&interval=1H&theme=dark&style=1&locale=en&hide_side_toolbar=0&allow_symbol_change=0"
                width="100%" height="450" frameborder="0">
            </iframe>
        </div>
    </div>

</div>

<footer>
    <div>© 2026 <span class="footer-owner">Pro_Plus System Intelligence</span> | Built by <span class="footer-owner">Pavankumar Madavi</span></div>
</footer>

<script>
    const COINS_LIST = [
        {symbol:"BTC", tv:"BINANCE:BTCUSDT"},
        {symbol:"ETH", tv:"BINANCE:ETHUSDT"},
        {symbol:"BNB", tv:"BINANCE:BNBUSDT"},
        {symbol:"SOL", tv:"BINANCE:SOLUSDT"},
        {symbol:"XRP", tv:"BINANCE:XRPUSDT"},
        {symbol:"DOGE", tv:"BINANCE:DOGEUSDT"},
        {symbol:"ADA", tv:"BINANCE:ADAUSDT"},
        {symbol:"MATIC", tv:"BINANCE:MATICUSDT"},
        {symbol:"DOT", tv:"BINANCE:DOTUSDT"},
        {symbol:"LINK", tv:"BINANCE:LINKUSDT"}
    ];

    // Coin buttons बनाओ
    const btnContainer = document.getElementById("coin-buttons");
    COINS_LIST.forEach((c, i) => {
        const btn = document.createElement("button");
        btn.className = "coin-btn" + (i === 0 ? " active" : "");
        btn.textContent = c.symbol;
        btn.onclick = () => {
            document.querySelectorAll(".coin-btn").forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            document.getElementById("tv-chart").src =
                `https://s.tradingview.com/widgetembed/?symbol=${c.tv}&interval=1H&theme=dark&style=1&locale=en&hide_side_toolbar=0`;
        };
        btnContainer.appendChild(btn);
    });

    async function refreshDashboard() {
        try {
            const r = await fetch("/api/prices");
            const data = await r.json();
            if (data.length === 0 || data[0].waiting) return;

            const freeGrid = document.getElementById("free-grid");
            const premiumGrid = document.getElementById("premium-grid");
            const tickerObj = document.getElementById("live-ticker");
            const newsObj = document.getElementById("news-container");

            freeGrid.innerHTML = ""; premiumGrid.innerHTML = "";

            let tickerHtml = "";
            data.forEach(coin => {
                let sColor = coin.signal.includes("BUY") ? "#02C076" : coin.signal.includes("SHORT") ? "#F6465D" : "#F0B90B";
                tickerHtml += `<div class="ticker-item"><span>${coin.logo} ${coin.symbol}:</span> <b style="color:${sColor}">${coin.current_price}</b></div>`;
            });
            tickerObj.innerHTML = tickerHtml + tickerHtml + tickerHtml;

            if (data[0].live_news) {
                newsObj.innerHTML = data[0].live_news.map(n => `<div class="news-item">${n}</div>`).join("");
            }

            data.forEach((coin, index) => {
                const modeClass = coin.mode.includes("SIDEWAYS") ? "bg-side" : "bg-vol";
                const trendColor = coin.macro_trend.includes("BEARISH") ? "#F6465D" : "#02C076";
                let sigColor = "#F0B90B";
                if (coin.signal.includes("BUY") || coin.signal.includes("LONG")) sigColor = "#02C076";
                if (coin.signal.includes("SHORT") || coin.signal.includes("SELL")) sigColor = "#F6465D";

                const cardHtml = `
                <div class="card">
                    <div class="card-top">
                        <span class="symbol">${coin.logo} ${coin.symbol}/USDT</span>
                        <span class="badge ${modeClass}">${coin.mode}</span>
                    </div>
                    <div class="metrics">
                        <div class="row"><span class="lbl">Market Price:</span><span class="val" style="color:${sigColor}">${coin.current_price}</span></div>
                        <div class="row"><span class="lbl">Macro Trend (HTF):</span><span class="val" style="color:${trendColor}">${coin.macro_trend}</span></div>
                        <div class="row"><span class="lbl">Volume Ratio:</span><span class="val">${coin.vol_ratio}</span></div>
                        <div class="row dev"><span class="lbl">Intelligence Signal:</span><span class="val" style="color:${sigColor}">${coin.signal}</span></div>
                        <div class="row"><span class="lbl">Dynamic StopLoss:</span><span class="val" style="color:#F6465D">${coin.dynamic_stop_loss}</span></div>
                        <div class="row"><span class="lbl">Target Range:</span><span class="val" style="color:#02C076">${coin.target_range}</span></div>
                        <div class="row dev"><span class="lbl">Institutional Supply:</span><span class="val">${coin.supply_zone}</span></div>
                        <div class="row"><span class="lbl">Institutional Demand:</span><span class="val">${coin.demand_zone}</span></div>
                    </div>
                </div>`;

                if (index < 2) {
                    freeGrid.innerHTML += cardHtml;
                } else {
                    premiumGrid.innerHTML += `
                    <div class="card" style="min-height:310px;">
                        <div class="premium-locked">${cardHtml}</div>
                        <div class="lock-overlay">
                            <h4 style="color:#F0B90B;font-size:13px;font-weight:700;">🔒 ALPHA MEMBER ACCESS ONLY</h4>
                            <p style="font-size:11px;color:var(--text-muted);margin:5px 0 10px 0;">Unlock Institutional SMC Order-Blocks & Trailing ATR</p>
                            <a href="https://t.me/GlobalTraderPavan" target="_blank" class="btn-premium">Join Premium Circle</a>
                        </div>
                    </div>`;
                }
            });

            const statusObj = document.getElementById("live-status");
            statusObj.className = "live-badge";
            statusObj.innerHTML = `● SI SYSTEM GLOBAL LIVE (${new Date().toLocaleTimeString()})`;
        } catch(e) {
            document.getElementById("live-status").className = "offline-badge";
            document.getElementById("live-status").innerHTML = "● LIVE SYNC ERROR";
        }
    }

    setInterval(refreshDashboard, 4000);
    refreshDashboard();
</script>
</body>
</html>
'''

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/api/prices", methods=["GET"])
def get_prices():
    if not live_market_data:
        return jsonify([{"waiting": True}])
    return jsonify(live_market_data)

@app.route("/api/update_prices", methods=["POST"])
def update_prices():
    global live_market_data
    token = request.headers.get("X-SI-Token")
    if token != SECRET_TOKEN:
        return jsonify({"status": "unauthorized"}), 401
    live_market_data = request.json
    return jsonify({"status": "success"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)