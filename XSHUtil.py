import requests
import threading
import time

API_URL = "https://api.coinmarketcap.com/v1/ticker/shield-xsh/?convert=JPY"
API_URL2 = "https://api.coinmarketcap.com/v1/ticker/shield-xsh/?convert=BTC"

price_jpy_per_xsh = 0
price_btc_per_xsh = 0


def update_price_jpy_per_xsh():
    global price_jpy_per_xsh
    while True:
        headers = {"content-type": "application/json"}
        data = requests.get(API_URL, headers=headers).json()
        price_jpy_per_xsh = float(data[0]['price_jpy'])
        time.sleep(60)


def update_price_btc_per_xsh():
    global price_btc_per_xsh
    while True:
        headers = {"content-type": "application/json"}
        data = requests.get(API_URL2, headers=headers).json()
        price_btc_per_xsh = float(data[0]['price_btc'])
        time.sleep(60)


threadUpdatePriceJPY = threading.Thread(target=update_price_jpy_per_xsh)
threadUpdatePriceBTC = threading.Thread(target=update_price_btc_per_xsh)
threadUpdatePriceJPY.start()
threadUpdatePriceBTC.start()


def get_price_jpy_per_xsh() -> float:
    return price_jpy_per_xsh


def get_price_btc_per_xsh() -> float:
    return price_btc_per_xsh