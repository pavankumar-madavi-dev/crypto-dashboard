import requests

def get_live_crypto_news():
    try:
        url = "https://cryptopanic.com/api/v1/posts/?auth_token=pub_free&kind=news&limit=3"
        res = requests.get(url, timeout=5).json()
        return [item['title'] for item in res['results'][:3]]
    except:
        return [
            "Market Update: Institutional accumulation detected",
            "Whale Alert: Large transfers spotted on ETH network",
            "Smart money positioning in SOL and BNB"
        ]