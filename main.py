import ccxt
import requests
import os

# دریافت متغیرهای امن از GitHub Secrets
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# اتصال به صرافی
exchange = ccxt.kucoin()

# لیست 50 کوین برتر از نظر مارکت کپ
TOP_50_COINS = [
    "BTC/USDT", "ETH/USDT", "BNB/USDT", "XRP/USDT", "SOL/USDT",
    "ADA/USDT", "DOGE/USDT", "AVAX/USDT", "DOT/USDT", "AIXBT/USDT",
    "TRX/USDT", "LTC/USDT", "SHIB/USDT", "UNI/USDT", "LINK/USDT",
    "ATOM/USDT", "XLM/USDT", "BCH/USDT", "ICP/USDT", "FIL/USDT",
    "LDO/USDT", "APT/USDT", "ARB/USDT", "QNT/USDT", "NEAR/USDT",
    "VET/USDT", "HBAR/USDT", "MKR/USDT", "SAND/USDT", "EGLD/USDT",
    "AXS/USDT", "TWT/USDT", "RPL/USDT", "AAVE/USDT", "THETA/USDT",
    "XEC/USDT", "EOS/USDT", "KCS/USDT", "ZIL/USDT", "GRT/USDT",
    "CHZ/USDT", "STX/USDT", "ENJ/USDT", "CAKE/USDT", "FXS/USDT",
    "KAVA/USDT", "GMT/USDT", "BONK/USDT", "SNX/USDT", "ROSE/USDT"
]

# ذخیره‌ی سقف قیمتی هر کوین
highest_prices = {}

def send_telegram_message(message):
    """ ارسال پیام به تلگرام """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ خطا: مقادیر TOKEN و CHAT ID تنظیم نشده‌اند!")
        return
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            print(f"⚠️ خطا در ارسال پیام تلگرام: {response.text}")
    except Exception as e:
        print(f"❌ خطا در ارسال پیام تلگرام: {e}")

def fetch_price(symbol):
    """ دریافت قیمت آخرین معامله یک جفت‌ارز """
    try:
        ticker = exchange.fetch_ticker(symbol)
        return ticker["last"]
    except Exception as e:
        print(f"❌ خطا در دریافت قیمت {symbol}: {e}")
        return None

def update_highest_prices():
    """ بررسی و به‌روزرسانی سقف قیمتی برای هر کوین """
    for symbol in TOP_50_COINS:
        price = fetch_price(symbol)
        if price is None:
            continue
        
        if symbol not in highest_prices or price > highest_prices[symbol]:
            highest_prices[symbol] = price  # ثبت سقف جدید

def check_price_drops():
    """ بررسی افت ۱۰٪ از سقف برای هر کوین """
    dropped_coins = []
    for symbol, highest in highest_prices.items():
        price = fetch_price(symbol)
        if price is None:
            continue

        drop_threshold = highest * 0.99  # ۱۰٪ پایین‌تر از سقف
        if price <= drop_threshold:
            dropped_coins.append(symbol)
    
    # ارسال هشدار اگر حداقل یک کوین ۱۰٪ افت کند
    if dropped_coins:
        message = f"⚠️ هشدار: برخی از کوین‌ها حداقل 1% ریزش داشته‌اند!\n\n"
        message += "📉 کوین‌های ریزشی:\n" + "\n".join(dropped_coins)
        send_telegram_message(message)

def main():
    """ اجرای یک‌بار بررسی قیمت‌ها """
    print("🔍 در حال بررسی قیمت‌ها...")
    update_highest_prices()
    check_price_drops()
    print("✅ بررسی انجام شد.")

if __name__ == "__main__":
    main()
