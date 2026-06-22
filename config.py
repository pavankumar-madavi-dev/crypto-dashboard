# ==========================================
# GlobalTraderPavan — Master Config
# Owner: Pavankumar Madavi
# niDar Marketing And Services
# Sadak Arjuni, Gondia, Maharashtra
# ==========================================

import os

# --- TRADING ON/OFF ---
TRADING_ACTIVE = True

# --- MINIMUM CONFIDENCE ---
CONFIDENCE_MINIMUM = 70

# --- COINS ---
COINS = [
    "BTCUSDT",
    "ETHUSDT",
    "BNBUSDT",
    "SOLUSDT"
]

# --- API KEYS ---
BINANCE_API_KEY  = os.getenv("BINANCE_API_KEY")
BINANCE_SECRET   = os.getenv("BINANCE_SECRET_KEY")
TELEGRAM_TOKEN   = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# --- RISK SETTINGS ---
MAX_RISK_PERCENT = 2
MIN_FUND_USDT    = 50
MAX_FUND_USDT    = 500

# --- TIMING ---
CHECK_INTERVAL    = 300
CONFIRMATION_TIME = 480

# --- RSI LEVELS ---
RSI_OVERSOLD   = 30
RSI_OVERBOUGHT = 70
VOLUME_SPIKE   = 150