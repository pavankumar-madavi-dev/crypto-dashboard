import requests
import time
from colorama import Fore, Style, init

init(autoreset=True)

def get_price_binance(symbol="BTCUSDT"):
    try:
        url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
        r = requests.get(url, timeout=5).json()
        return {
            "price": float(r["lastPrice"]),
            "change": float(r["priceChangePercent"]),
            "high": float(r["highPrice"]),
            "low": float(r["lowPrice"]),
            "volume": float(r["volume"])
        }
    except:
        return None

def get_rsi_signal(symbol="BTCUSDT"):
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1h&limit=15"
        data = requests.get(url, timeout=5).json()
        closes = [float(c[4]) for c in data]
        
        gains, losses = [], []
        for i in range(1, len(closes)):
            diff = closes[i] - closes[i-1]
            gains.append(max(diff, 0))
            losses.append(max(-diff, 0))
        
        avg_gain = sum(gains[-14:]) / 14
        avg_loss = sum(losses[-14:]) / 14
        
        if avg_loss == 0:
            rsi = 100
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
        
        if rsi < 30:
            signal = f"{Fore.GREEN}BUY (Oversold)"
        elif rsi > 70:
            signal = f"{Fore.RED}SELL (Overbought)"
        else:
            signal = f"{Fore.YELLOW}HOLD"
        
        return round(rsi, 2), signal
    except:
        return None, "N/A"

def display_dashboard():
    coins = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT"]
    
    while True:
        print("\033[H\033[J")
        print(Fore.CYAN + "=" * 50)
        print(Fore.CYAN + "   CRYPTO TRADING DASHBOARD")
        print(Fore.CYAN + "   by pavankumar-madavi-dev")
        print(Fore.CYAN + "=" * 50)
        
        for coin in coins:
            data = get_price_binance(coin)
            rsi, signal = get_rsi_signal(coin)
            
            if data:
                change_color = Fore.GREEN if data["change"] >= 0 else Fore.RED
                arrow = "UP" if data["change"] >= 0 else "DOWN"
                
                print(f"\n{Fore.WHITE}>> {coin}")
                print(f"   Price  : {Fore.YELLOW}${data['price']:,.2f}")
                print(f"   Change : {change_color}{arrow} {data['change']:.2f}%")
                print(f"   High   : ${data['high']:,.2f}")
                print(f"   Low    : ${data['low']:,.2f}")
                print(f"   RSI    : {rsi} >> {signal}")
            else:
                print(f"\n{coin}: Data unavailable")
        
        print(f"\n{Fore.CYAN}{'='*50}")
        print(f"{Fore.WHITE}Updated every 60 sec | Ctrl+C to exit")
        print(Fore.CYAN + "=" * 50)
        
        time.sleep(60)

if __name__ == "__main__":
    print(Fore.CYAN + "Starting Crypto Dashboard...")
    display_dashboard()
