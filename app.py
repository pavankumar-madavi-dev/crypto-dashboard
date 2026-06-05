from flask import Flask, render_template_string, jsonify
import json
import os
from datetime import datetime
import threading
import time

app = Flask(__name__)

DATA_FILE = "market_data.json"

# ═══════════════════════════════════════════════════════════
# LOAD MARKET DATA
# ═══════════════════════════════════════════════════════════
def load_market_data():
    """Load data from si_trader.py"""
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Load error: {e}")
    
    return {"timestamp": datetime.now().isoformat(), "data": []}

# ═══════════════════════════════════════════════════════════
# PREMIUM HTML/CSS/JS DASHBOARD
# ═══════════════════════════════════════════════════════════
HTML = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pro_Plus • Elite SI Trading System</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%);
            color: #e0e0e0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            overflow-x: hidden;
            min-height: 100vh;
        }

        /* ── HEADER ── */
        .header {
            background: rgba(15, 23, 42, 0.95);
            backdrop-filter: blur(10px);
            padding: 20px;
            border-bottom: 2px solid rgba(88, 166, 255, 0.3);
            position: sticky;
            top: 0;
            z-index: 100;
        }

        .header-content {
            max-width: 1400px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .logo {
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 24px;
            font-weight: 900;
            background: linear-gradient(135deg, #58a6ff, #1f6feb);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .logo-icon {
            font-size: 28px;
        }

        .timer-badge {
            background: rgba(88, 166, 255, 0.15);
            border: 1px solid rgba(88, 166, 255, 0.5);
            padding: 8px 15px;
            border-radius: 20px;
            font-size: 12px;
            color: #58a6ff;
            font-weight: 600;
        }

        /* ── STATS BAR ── */
        .stats-bar {
            background: rgba(20, 28, 50, 0.6);
            padding: 15px 20px;
            border-bottom: 1px solid rgba(88, 166, 255, 0.2);
            display: flex;
            gap: 30px;
            justify-content: center;
            flex-wrap: wrap;
            font-size: 13px;
        }

        .stat-item {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .stat-label {
            color: #888;
        }

        .stat-value {
            color: #58a6ff;
            font-weight: 600;
        }

        /* ── MAIN CONTAINER ── */
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 30px 20px;
        }

        .section-title {
            font-size: 20px;
            font-weight: 700;
            color: #e0e0e0;
            margin: 30px 0 15px;
            padding-left: 15px;
            border-left: 4px solid #58a6ff;
        }

        /* ── GRID LAYOUT ── */
        .cards-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        /* ── CARD STYLES ── */
        .card {
            background: rgba(20, 28, 50, 0.5);
            border: 1px solid rgba(88, 166, 255, 0.2);
            border-radius: 12px;
            padding: 20px;
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        .card:hover {
            border-color: rgba(88, 166, 255, 0.5);
            background: rgba(20, 28, 50, 0.8);
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(88, 166, 255, 0.1);
        }

        .card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, #58a6ff, transparent);
            opacity: 0;
            transition: opacity 0.3s ease;
        }

        .card:hover::before {
            opacity: 1;
        }

        /* ── SYMBOL HEADER ── */
        .symbol-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 15px;
            border-bottom: 1px solid rgba(88, 166, 255, 0.1);
        }

        .symbol-name {
            font-size: 18px;
            font-weight: 700;
            color: #58a6ff;
        }

        .price-badge {
            font-size: 22px;
            font-weight: 900;
            color: #e0e0e0;
        }

        .change-badge {
            padding: 5px 10px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
        }

        .change-badge.positive {
            background: rgba(34, 197, 94, 0.2);
            color: #22c55e;
        }

        .change-badge.negative {
            background: rgba(239, 68, 68, 0.2);
            color: #ef4444;
        }

        /* ── INFO ROW ── */
        .info-row {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            font-size: 12px;
            border-bottom: 1px solid rgba(88, 166, 255, 0.05);
        }

        .info-label {
            color: #666;
        }

        .info-value {
            color: #58a6ff;
            font-weight: 600;
        }

        /* ── SIGNAL BADGE ── */
        .signal-section {
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid rgba(88, 166, 255, 0.1);
        }

        .signal-badge {
            display: inline-block;
            padding: 10px 15px;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 700;
            width: 100%;
            text-align: center;
            margin-bottom: 10px;
        }

        .signal-buy {
            background: rgba(34, 197, 94, 0.2);
            color: #22c55e;
            border: 1px solid rgba(34, 197, 94, 0.4);
        }

        .signal-sell {
            background: rgba(239, 68, 68, 0.2);
            color: #ef4444;
            border: 1px solid rgba(239, 68, 68, 0.4);
        }

        .signal-hold {
            background: rgba(59, 130, 246, 0.2);
            color: #3b82f6;
            border: 1px solid rgba(59, 130, 246, 0.4);
        }

        /* ── TARGETS & SL ── */
        .targets-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-top: 10px;
        }

        .target-box {
            background: rgba(88, 166, 255, 0.1);
            border: 1px solid rgba(88, 166, 255, 0.2);
            padding: 10px;
            border-radius: 6px;
            font-size: 11px;
            text-align: center;
        }

        .target-label {
            color: #888;
            font-size: 10px;
        }

        .target-value {
            color: #58a6ff;
            font-weight: 700;
            font-size: 14px;
            margin-top: 3px;
        }

        /* ── TREND GAUGE ── */
        .trend-gauge {
            display: flex;
            gap: 5px;
            margin: 10px 0;
        }

        .trend-segment {
            flex: 1;
            height: 8px;
            border-radius: 4px;
            background: rgba(88, 166, 255, 0.1);
        }

        .trend-segment.bullish {
            background: linear-gradient(90deg, #22c55e, rgba(34, 197, 94, 0.3));
        }

        .trend-segment.bearish {
            background: linear-gradient(90deg, #ef4444, rgba(239, 68, 68, 0.3));
        }

        .trend-segment.neutral {
            background: linear-gradient(90deg, #3b82f6, rgba(59, 130, 246, 0.3));
        }

        /* ── PREMIUM BADGE ── */
        .premium-lock {
            position: absolute;
            top: 15px;
            right: 15px;
            background: rgba(239, 68, 68, 0.2);
            border: 1px solid rgba(239, 68, 68, 0.5);
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 11px;
            color: #ef4444;
            font-weight: 600;
            display: none;
        }

        .card.premium .premium-lock {
            display: block;
        }

        .card.premium {
            opacity: 0.6;
            pointer-events: none;
        }

        /* ── FOOTER ── */
        .footer {
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 12px;
            border-top: 1px solid rgba(88, 166, 255, 0.1);
            margin-top: 40px;
        }

        .footer-link {
            color: #58a6ff;
            text-decoration: none;
        }

        .footer-link:hover {
            text-decoration: underline;
        }

        /* ── LOADING ── */
        .loading {
            text-align: center;
            padding: 40px;
            color: #666;
        }

        .spinner {
            border: 2px solid rgba(88, 166, 255, 0.2);
            border-top: 2px solid #58a6ff;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        /* ── RESPONSIVE ── */
        @media (max-width: 768px) {
            .cards-grid {
                grid-template-columns: 1fr;
            }
            
            .header-content {
                flex-direction: column;
                gap: 15px;
            }
            
            .stats-bar {
                gap: 15px;
            }
        }
    </style>
</head>
<body>
    <!-- HEADER -->
    <div class="header">
        <div class="header-content">
            <div class="logo">
                <span class="logo-icon">⚡</span>
                <span>Pro_Plus</span>
            </div>
            <div class="timer-badge">
                🟢 LIVE • Next Scan: <span id="timer">5m 0s</span>
            </div>
        </div>
    </div>

    <!-- STATS BAR -->
    <div class="stats-bar">
        <div class="stat-item">
            <span class="stat-label">System Status:</span>
            <span class="stat-value">🟢 ONLINE</span>
        </div>
        <div class="stat-item">
            <span class="stat-label">Last Update:</span>
            <span class="stat-value" id="last-update">--:--:--</span>
        </div>
        <div class="stat-item">
            <span class="stat-label">Symbols Tracked:</span>
            <span class="stat-value" id="symbol-count">5</span>
        </div>
        <div class="stat-item">
            <span class="stat-label">Active Signals:</span>
            <span class="stat-value" id="signal-count">0</span>
        </div>
    </div>

    <!-- CONTAINER -->
    <div class="container">
        <!-- FREE SIGNALS SECTION -->
        <div class="section-title">📊 Free Signals Preview</div>
        <div class="cards-grid" id="free-cards">
            <div class="loading">
                <div class="spinner"></div>
                <p>Loading real-time data...</p>
            </div>
        </div>

        <!-- PREMIUM SECTION -->
        <div class="section-title">🔒 Premium SI Circle (Advanced Analysis)</div>
        <div class="cards-grid" id="premium-cards">
            <div class="loading">
                <div class="spinner"></div>
                <p>Unlock premium features...</p>
            </div>
        </div>
    </div>

    <!-- FOOTER -->
    <div class="footer">
        <p>⚡ <strong>Pro_Plus</strong> • Elite System Intelligence Trading Platform</p>
        <p>🌐 Join: <a href="https://t.me/GlobalTraderPavan" class="footer-link">@GlobalTraderPavan</a> | ⚠️ Trade at your own risk</p>
        <p style="margin-top: 10px; color: #555;">Powered by Binance Futures | Multi-Timeframe AI Analysis</p>
    </div>

    <script>
        const FREE_SYMBOLS = ["BTC/USDT", "ETH/USDT"];
        const PREMIUM_SYMBOLS = ["SOL/USDT", "XRP/USDT", "DOGE/USDT"];
        let allData = {};
        let countdownTime = 300;

        // ── FETCH DATA ──
        async function fetchData() {
            try {
                const response = await fetch('/api/data');
                const data = await response.json();
                
                if (data.data && data.data.length > 0) {
                    allData = {};
                    data.data.forEach(item => {
                        allData[item.symbol] = item;
                    });
                    
                    updateUI();
                    updateLastUpdate(data.timestamp);
                    countdownTime = 300;
                }
            } catch (error) {
                console.error('Fetch error:', error);
            }
        }

        // ── BUILD CARD ──
        function buildCard(symbol, isPremium = false) {
            const data = allData[symbol];
            if (!data) return '';

            const isPositive = data.change >= 0;
            const signal = data.signal || 'HOLD';
            const signalClass = data.action === 'BUY' ? 'signal-buy' : 
                               data.action === 'SELL' ? 'signal-sell' : 'signal-hold';

            const macroColor = data.macro_trend === 'BULLISH' ? 'bullish' :
                              data.macro_trend === 'BEARISH' ? 'bearish' : 'neutral';

            let html = `
                <div class="card ${isPremium ? 'premium' : ''}">
                    <div class="premium-lock">🔒 PREMIUM</div>
                    
                    <div class="symbol-header">
                        <div class="symbol-name">📌 ${symbol}</div>
                        <div class="price-badge">$${data.price.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 4})}</div>
                    </div>

                    <div class="change-badge ${isPositive ? 'positive' : 'negative'}">
                        ${isPositive ? '▲' : '▼'} ${Math.abs(data.change).toFixed(2)}%
                    </div>

                    <div class="info-row">
                        <span class="info-label">Macro Trend:</span>
                        <span class="info-value">${data.macro_trend}</span>
                    </div>

                    <div class="trend-gauge">
                        <div class="trend-segment ${macroColor}"></div>
                        <div class="trend-segment ${macroColor}"></div>
                        <div class="trend-segment ${macroColor}"></div>
                    </div>

                    <div class="info-row">
                        <span class="info-label">Volatility:</span>
                        <span class="info-value">${data.volatility_state}</span>
                    </div>

                    <div class="info-row">
                        <span class="info-label">Supply Zone:</span>
                        <span class="info-value">$${data.supply.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 4})}</span>
                    </div>

                    <div class="info-row">
                        <span class="info-label">Demand Zone:</span>
                        <span class="info-value">$${data.demand.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 4})}</span>
                    </div>

                    <div class="info-row">
                        <span class="info-label">ATR:</span>
                        <span class="info-value">${data.atr.toFixed(4)}</span>
                    </div>

                    <div class="info-row">
                        <span class="info-label">RSI:</span>
                        <span class="info-value">${data.rsi.toFixed(2)}</span>
                    </div>

                    <div class="info-row">
                        <span class="info-label">Volume Ratio:</span>
                        <span class="info-value">${data.vol_ratio.toFixed(2)}x</span>
                    </div>

                    <div class="signal-section">
                        <div class="signal-badge ${signalClass}">
                            ${data.emoji} ${signal}
                        </div>
                        
                        ${data.targets ? `
                        <div class="targets-grid">
                            <div class="target-box">
                                <div class="target-label">T1</div>
                                <div class="target-value">$${data.targets.T1.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 4})}</div>
                            </div>
                            <div class="target-box">
                                <div class="target-label">T2</div>
                                <div class="target-value">$${data.targets.T2.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 4})}</div>
                            </div>
                            <div class="target-box">
                                <div class="target-label">T3</div>
                                <div class="target-value">$${data.targets.T3.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 4})}</div>
                            </div>
                            <div class="target-box">
                                <div class="target-label">SL</div>
                                <div class="target-value">$${data.targets.SL.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 4})}</div>
                            </div>
                        </div>
                        ` : ''}
                    </div>
                </div>
            `;

            return html;
        }

        // ── UPDATE UI ──
        function updateUI() {
            let freeHtml = '';
            let premiumHtml = '';

            FREE_SYMBOLS.forEach(symbol => {
                freeHtml += buildCard(symbol, false);
            });

            PREMIUM_SYMBOLS.forEach(symbol => {
                premiumHtml += buildCard(symbol, true);
            });

            document.getElementById('free-cards').innerHTML = freeHtml || '<p style="color: #666;">No data available</p>';
            document.getElementById('premium-cards').innerHTML = premiumHtml || '<p style="color: #666;">Upgrade to Premium</p>';

            document.getElementById('symbol-count').textContent = Object.keys(allData).length;
            
            let signalCount = Object.values(allData).filter(d => d.action !== 'HOLD').length;
            document.getElementById('signal-count').textContent = signalCount;
        }

        // ── UPDATE TIMESTAMP ──
        function updateLastUpdate(timestamp) {
            const date = new Date(timestamp);
            const time = date.toLocaleTimeString();
            document.getElementById('last-update').textContent = time;
        }

        // ── COUNTDOWN TIMER ──
        function updateTimer() {
            const mins = Math.floor(countdownTime / 60);
            const secs = countdownTime % 60;
            document.getElementById('timer').textContent = 
                `${mins}m ${secs}s`.padStart(4, '0');
            
            if (countdownTime > 0) {
                countdownTime--;
            } else {
                countdownTime = 300;
            }
        }

        // ── INIT ──
        fetchData();
        setInterval(fetchData, 5000);
        setInterval(updateTimer, 1000);
    </script>
</body>
</html>
'''

# ═══════════════════════════════════════════════════════════
# FLASK ROUTES
# ═══════════════════════════════════════════════════════════

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/api/data")
def get_data():
    data = load_market_data()
    return jsonify(data)

@app.route("/api/prices")
def get_prices():
    """Legacy endpoint for compatibility"""
    data = load_market_data()
    result = {}
    if "data" in data:
        for item in data["data"]:
            result[item["symbol"]] = item
    return jsonify(result)

# ═══════════════════════════════════════════════════════════
# RUN
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
