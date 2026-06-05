import ccxt
import pandas as pd
import numpy as np
import json
import time
import os
import logging
import requests
from datetime import datetime, timedelta
from collections import deque

# ═══════════════════════════════════════════════════════════
# LOGGER SETUP
# ═══════════════════════════════════════════════════════════
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════
TG_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TG_CHAT  = os.environ.get("TELEGRAM_CHAT_ID", "@GlobalTraderPavan")

SYMBOLS = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT", "DOGE/USDT"]

SCAN_INTERVAL = 300  # 5 minutes
DATA_FILE = "market_data.json"

# ═══════════════════════════════════════════════════════════
# EXCHANGE SETUP
# ═══════════════════════════════════════════════════════════
try:
    exchange = ccxt.binance({
        "enableRateLimit": True,
        "options": {"defaultType": "future"}
    })
    logger.info("✅ Binance Exchange Connected")
except Exception as e:
    logger.error(f"❌ Exchange Error: {e}")
    exchange = None

# ═══════════════════════════════════════════════════════════
# TELEGRAM MESSENGER
# ═══════════════════════════════════════════════════════════
def send_telegram(msg, retry=2):
    """Send message to Telegram with retry logic"""
    if not TG_TOKEN or not TG_CHAT:
        return False
    
    for attempt in range(retry):
        try:
            url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
            requests.post(
                url,
                data={"chat_id": TG_CHAT, "text": msg, "parse_mode": "HTML"},
                timeout=10
            )
            logger.info(f"✅ Telegram sent: {msg[:50]}...")
            return True
        except Exception as e:
            logger.warning(f"⚠️ Telegram retry {attempt+1}/{retry}: {e}")
            time.sleep(2)
    
    return False

# ═══════════════════════════════════════════════════════════
# TECHNICAL INDICATORS
# ═══════════════════════════════════════════════════════════
def calculate_indicators(df):
    """Calculate all technical indicators"""
    try:
        # ATR (14-period)
        df["H-L"]  = df["high"] - df["low"]
        df["H-PC"] = abs(df["high"] - df["close"].shift(1))
        df["L-PC"] = abs(df["low"]  - df["close"].shift(1))
        df["TR"]   = df[["H-L","H-PC","L-PC"]].max(axis=1)
        df["ATR"]  = df["TR"].rolling(14).mean()

        # EMA (20/50)
        df["EMA20"] = df["close"].ewm(span=20).mean()
        df["EMA50"] = df["close"].ewm(span=50).mean()

        # RSI (14)
        delta = df["close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df["RSI"] = 100 - (100 / (1 + rs))

        # MACD
        ema12 = df["close"].ewm(span=12).mean()
        ema26 = df["close"].ewm(span=26).mean()
        df["MACD"] = ema12 - ema26
        df["MACD_Signal"] = df["MACD"].ewm(span=9).mean()
        df["MACD_Hist"] = df["MACD"] - df["MACD_Signal"]

        # Bollinger Bands
        df["BB_Mid"] = df["close"].rolling(20).mean()
        df["BB_Std"] = df["close"].rolling(20).std()
        df["BB_Upper"] = df["BB_Mid"] + (df["BB_Std"] * 2)
        df["BB_Lower"] = df["BB_Mid"] - (df["BB_Std"] * 2)

        return df
    except Exception as e:
        logger.error(f"Indicator error: {e}")
        return df

# ═══════════════════════════════════════════════════════════
# MULTI-TIMEFRAME TREND DETECTION
# ═══════════════════════════════════════════════════════════
def detect_macro_trend(df_1h, df_4h, df_1d):
    """
    Detect macro trend using multi-timeframe EMA cross
    Returns: "BULLISH" / "BEARISH" / "NEUTRAL"
    """
    try:
        # 1D trend (strongest)
        if len(df_1d) > 50:
            daily_ema20 = df_1d["EMA20"].iloc[-1]
            daily_ema50 = df_1d["EMA50"].iloc[-1]
            
            if daily_ema20 > daily_ema50:
                return "BULLISH"
            elif daily_ema20 < daily_ema50:
                return "BEARISH"
        
        return "NEUTRAL"
    except Exception as e:
        logger.warning(f"Macro trend error: {e}")
        return "NEUTRAL"

# ═══════════════════════════════════════════════════════════
# INSTITUTIONAL ORDER BLOCK DETECTION
# ═══════════════════════════════════════════════════════════
def detect_order_blocks(df):
    """
    Detect true Institutional Supply/Demand zones
    Based on: High volume + Price rejection
    """
    try:
        if len(df) < 24:
            return None, None

        last_24 = df.iloc[-24:]
        avg_vol = last_24["volume"].mean()

        # Supply Zone (Resistance with high volume)
        high_vol_bars = last_24[last_24["volume"] > avg_vol * 1.5]
        if len(high_vol_bars) > 0:
            supply = high_vol_bars["high"].max()
        else:
            supply = last_24["high"].max()

        # Demand Zone (Support with high volume)
        if len(high_vol_bars) > 0:
            demand = high_vol_bars["low"].min()
        else:
            demand = last_24["low"].min()

        return supply, demand
    except Exception as e:
        logger.warning(f"Order block error: {e}")
        return None, None

# ═══════════════════════════════════════════════════════════
# MARKET STRUCTURE BREAK (MSB) DETECTION
# ═══════════════════════════════════════════════════════════
def detect_msb(df):
    """
    Detect Market Structure Break
    True break only if volume confirms
    """
    try:
        if len(df) < 5:
            return None

        recent = df.iloc[-5:]
        current_price = df["close"].iloc[-1]
        avg_vol = df["volume"].iloc[-10:].mean()
        current_vol = df["volume"].iloc[-1]

        # Higher High + Higher Low = Bullish MSB
        if current_price > recent["high"].iloc[-2] and current_vol > avg_vol * 1.3:
            return "BULLISH_MSB"
        
        # Lower High + Lower Low = Bearish MSB
        if current_price < recent["low"].iloc[-2] and current_vol > avg_vol * 1.3:
            return "BEARISH_MSB"

        return None
    except Exception as e:
        logger.warning(f"MSB error: {e}")
        return None

# ═══════════════════════════════════════════════════════════
# RIGHT-TIME ENTRY LOGIC
# ═══════════════════════════════════════════════════════════
def check_right_time_entry(price, demand, supply, vol_ratio, macro_trend):
    """
    Entry only when:
    1. Price is deep in Demand Zone (discount)
    2. OR Price at Supply Zone (premium)
    3. AND Volume Ratio > 1.5x
    """
    entry_price = None
    entry_type = None

    zone_range = supply - demand

    # Deep Discount Entry
    if price <= demand * 1.01 and vol_ratio > 1.5 and macro_trend != "BEARISH":
        entry_price = price
        entry_type = "DISCOUNT_BUY"

    # Premium Entry (only in BULLISH)
    elif price >= supply * 0.99 and vol_ratio > 1.5 and macro_trend == "BULLISH":
        entry_price = price
        entry_type = "PREMIUM_SELL"

    # Normal zone entry
    elif zone_range > 0:
        zone_middle = (supply + demand) / 2
        if price <= zone_middle * 0.98 and vol_ratio > 1.3 and macro_trend == "BULLISH":
            entry_price = price
            entry_type = "NORMAL_BUY"

    return entry_price, entry_type

# ═══════════════════════════════════════════════════════════
# DYNAMIC EXIT STRATEGY (3-LEVEL TARGETS + TRAILING SL)
# ═══════════════════════════════════════════════════════════
def calculate_targets_and_sl(entry_price, entry_type, atr, demand, supply):
    """
    3-Level Target System + Dynamic Trailing SL
    T1: Conservative scalp (0.5% * zone_range)
    T2: Momentum target (1% * zone_range)
    T3: Macro trend run (2% * zone_range)
    """
    zone_range = supply - demand if supply > demand else entry_price * 0.05

    if entry_type == "DISCOUNT_BUY":
        # Targets above entry
        t1 = entry_price + (zone_range * 0.5)
        t2 = entry_price + (zone_range * 1.0)
        t3 = entry_price + (zone_range * 2.0)
        
        # Dynamic trailing SL
        sl = entry_price - (2 * atr)
        be_sl = entry_price  # Break-even after T1

    elif entry_type == "PREMIUM_SELL":
        # Targets below entry
        t1 = entry_price - (zone_range * 0.5)
        t2 = entry_price - (zone_range * 1.0)
        t3 = entry_price - (zone_range * 2.0)
        
        # Dynamic trailing SL
        sl = entry_price + (2 * atr)
        be_sl = entry_price

    else:
        # Normal entry
        t1 = entry_price + (zone_range * 0.5)
        t2 = entry_price + (zone_range * 1.0)
        t3 = entry_price + (zone_range * 2.0)
        sl = entry_price - (2 * atr)
        be_sl = entry_price

    return {
        "T1": t1, "T2": t2, "T3": t3,
        "SL": sl, "BE_SL": be_sl
    }

# ═══════════════════════════════════════════════════════════
# FETCH MULTI-TIMEFRAME DATA
# ═══════════════════════════════════════════════════════════
def fetch_multi_timeframe(symbol):
    """Fetch 1h, 4h, 1d OHLCV data"""
    try:
        df_1h = pd.DataFrame(
            exchange.fetch_ohlcv(symbol, timeframe="1h", limit=100),
            columns=["timestamp","open","high","low","close","volume"]
        )
        df_1h["timestamp"] = pd.to_datetime(df_1h["timestamp"], unit="ms")
        df_1h = calculate_indicators(df_1h)

        df_4h = pd.DataFrame(
            exchange.fetch_ohlcv(symbol, timeframe="4h", limit=50),
            columns=["timestamp","open","high","low","close","volume"]
        )
        df_4h["timestamp"] = pd.to_datetime(df_4h["timestamp"], unit="ms")
        df_4h = calculate_indicators(df_4h)

        df_1d = pd.DataFrame(
            exchange.fetch_ohlcv(symbol, timeframe="1d", limit=30),
            columns=["timestamp","open","high","low","close","volume"]
        )
        df_1d["timestamp"] = pd.to_datetime(df_1d["timestamp"], unit="ms")
        df_1d = calculate_indicators(df_1d)

        return df_1h, df_4h, df_1d

    except Exception as e:
        logger.error(f"Multi-TF fetch error {symbol}: {e}")
        return None, None, None

# ═══════════════════════════════════════════════════════════
# COMPREHENSIVE ANALYSIS ENGINE
# ═══════════════════════════════════════════════════════════
def analyze_pro_plus(symbol):
    """Pro_Plus Elite Analysis"""
    try:
        # Fetch data
        df_1h, df_4h, df_1d = fetch_multi_timeframe(symbol)
        if df_1h is None or len(df_1h) < 20:
            logger.warning(f"⚠️ Insufficient data: {symbol}")
            return None

        # Current values
        current_price = df_1h["close"].iloc[-1]
        prev_price = df_1h["close"].iloc[-2]
        price_change = ((current_price - prev_price) / prev_price) * 100

        # Indicators
        atr = df_1h["ATR"].iloc[-1] if pd.notna(df_1h["ATR"].iloc[-1]) else current_price * 0.01
        rsi = df_1h["RSI"].iloc[-1] if pd.notna(df_1h["RSI"].iloc[-1]) else 50

        # Volume analysis
        avg_vol_5h = df_1h["volume"].iloc[-6:-1].mean()
        current_vol = df_1h["volume"].iloc[-1]
        vol_ratio = current_vol / avg_vol_5h if avg_vol_5h > 0 else 0

        # Order blocks (Smart Money)
        supply, demand = detect_order_blocks(df_1h)
        if supply is None or demand is None:
            supply = df_1h["high"].iloc[-24:].max()
            demand = df_1h["low"].iloc[-24:].min()

        # Market Structure
        msb = detect_msb(df_1h)

        # Macro Trend
        macro_trend = detect_macro_trend(df_1h, df_4h, df_1d)

        # Volatility State
        volatility_state = "HIGH" if atr > current_price * 0.01 else "LOW"

        # Entry Logic
        entry_price, entry_type = check_right_time_entry(
            current_price, demand, supply, vol_ratio, macro_trend
        )

        # Targets & SL
        if entry_price:
            targets = calculate_targets_and_sl(entry_price, entry_type, atr, demand, supply)
        else:
            targets = None

        # Generate Signal
        if entry_type == "DISCOUNT_BUY":
            signal = f"🟢 INSTITUTIONAL BUY {entry_type}"
            action = "BUY"
            emoji = "🟢🟢"
        elif entry_type == "PREMIUM_SELL":
            signal = f"🔴 INSTITUTIONAL SELL {entry_type}"
            action = "SELL"
            emoji = "🔴🔴"
        elif entry_type == "NORMAL_BUY":
            signal = f"🟢 SMART BUY {entry_type}"
            action = "BUY"
            emoji = "🟢"
        else:
            signal = "🟡 HOLD / MONITOR"
            action = "HOLD"
            emoji = "🟡"

        result = {
            "symbol": symbol,
            "price": round(current_price, 4),
            "change": round(price_change, 2),
            "vol_ratio": round(vol_ratio, 2),
            "atr": round(atr, 4),
            "rsi": round(rsi, 2),
            "supply": round(supply, 4),
            "demand": round(demand, 4),
            "macro_trend": macro_trend,
            "volatility_state": volatility_state,
            "msb": msb,
            "entry_type": entry_type,
            "entry_price": round(entry_price, 4) if entry_price else None,
            "targets": targets,
            "signal": signal,
            "action": action,
            "emoji": emoji,
            "timestamp": datetime.now().isoformat(),
        }

        return result

    except Exception as e:
        logger.error(f"Analysis error {symbol}: {e}")
        return None

# ═══════════════════════════════════════════════════════════
# SAVE DATA TO JSON
# ═══════════════════════════════════════════════════════════
def save_market_data(data_list):
    """Save all analysis data to JSON for Flask to read"""
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "data": data_list
            }, f, indent=2)
        logger.info(f"✅ Market data saved to {DATA_FILE}")
    except Exception as e:
        logger.error(f"Save error: {e}")

# ═══════════════════════════════════════════════════════════
# TELEGRAM NOTIFICATION
# ═══════════════════════════════════════════════════════════
def build_telegram_msg(r):
    """Build premium Telegram message"""
    return f"""🚀 <b>Pro_Plus SI Signal</b>

📌 <b>{r['symbol']}</b>
💰 Price: <b>${r['price']:,.4f}</b>
📊 Change: <b>{r['change']:.2f}%</b>

⚙️ <b>Macro Trend:</b> {r['macro_trend']}
📈 <b>Volatility:</b> {r['volatility_state']}
🔍 <b>Market Structure:</b> {r['msb'] if r['msb'] else 'Normal'}

🏔️ <b>Supply Zone:</b> ${r['supply']:,.4f}
🏕️ <b>Demand Zone:</b> ${r['demand']:,.4f}

{r['emoji']} <b>Signal:</b> {r['signal']}

{f"📍 <b>Entry:</b> ${r['entry_price']:,.4f}" if r['entry_price'] else ""}
{f"🎯 <b>T1:</b> ${r['targets']['T1']:,.4f} | <b>T2:</b> ${r['targets']['T2']:,.4f} | <b>T3:</b> ${r['targets']['T3']:,.4f}" if r['targets'] else ""}
{f"🛑 <b>SL:</b> ${r['targets']['SL']:,.4f}" if r['targets'] else ""}

📦 <b>Vol Ratio:</b> {r['vol_ratio']:.2f}x
📉 <b>ATR:</b> {r['atr']:.4f}
📊 <b>RSI:</b> {r['rsi']:.2f}

🌐 <a href="https://t.me/GlobalTraderPavan">Join Pro_Plus Channel</a>
⚠️ <b>Trade at your own risk!</b>"""

# ═══════════════════════════════════════════════════════════
# MAIN LOOP
# ═══════════════════════════════════════════════════════════
last_signals = {}
scan_count = 0

def main():
    global scan_count
    
    logger.info("="*60)
    logger.info("🚀 Pro_Plus SI Trading System Started!")
    logger.info("="*60)
    
    send_telegram("🚀 <b>Pro_Plus SI System Online!</b>\n⚡ Elite Algorithmic Trading\n📡 Monitoring: BTC ETH SOL XRP DOGE")

    while True:
        try:
            scan_count += 1
            logger.info(f"\n📊 Scan #{scan_count} - {datetime.now().strftime('%H:%M:%S')}")
            
            results = []
            for symbol in SYMBOLS:
                try:
                    r = analyze_pro_plus(symbol)
                    if r:
                        results.append(r)
                        logger.info(f"✅ {symbol}: {r['signal']}")
                        
                        # Send signal on change
                        prev = last_signals.get(symbol, "")
                        if r['signal'] != prev and r['entry_type']:
                            last_signals[symbol] = r['signal']
                            msg = build_telegram_msg(r)
                            send_telegram(msg)
                            logger.info(f"📢 Telegram sent: {symbol}")
                except Exception as e:
                    logger.error(f"Symbol error {symbol}: {e}")
                    continue

            # Save data
            if results:
                save_market_data(results)

            logger.info(f"⏳ Next scan in {SCAN_INTERVAL}s ({datetime.now() + timedelta(seconds=SCAN_INTERVAL)})")
            time.sleep(SCAN_INTERVAL)

        except KeyboardInterrupt:
            logger.info("\n🛑 System stopped by user")
            break
        except Exception as e:
            logger.error(f"Main loop error: {e}")
            time.sleep(30)

if __name__ == "__main__":
    main()
