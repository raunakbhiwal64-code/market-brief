import os
import urllib.parse
import requests
import yfinance as yf
from bs4 import BeautifulSoup


def fmt_price(price, change_pct):
    arrow = "▲" if change_pct >= 0 else "▼"
    sign = "+" if change_pct >= 0 else ""
    return f"{price:,.0f} ({arrow}{abs(change_pct):.2f}%)"


def get_gift_nifty():
    try:
        ticker = yf.Ticker("^NSEI")
        # Get intraday 1-min data for latest price
        intraday = ticker.history(period="1d", interval="1m")
        if intraday.empty:
            raise ValueError("Empty intraday data")
        latest_price = intraday["Close"].iloc[-1]

        # Get previous close from 2-day daily data
        daily = ticker.history(period="2d", interval="1d")
        if len(daily) < 2:
            raise ValueError("Not enough daily data for prev close")
        prev_close = daily["Close"].iloc[-2]

        change_pct = ((latest_price - prev_close) / prev_close) * 100
        print(f"[Gift Nifty] price={latest_price:.2f}, prev_close={prev_close:.2f}, chg={change_pct:.2f}%")
        return fmt_price(latest_price, change_pct), change_pct
    except Exception as e:
        print(f"[Gift Nifty] ERROR: {e}")
        return "N/A (fetch error)", 0


def get_dow_jones():
    try:
        ticker = yf.Ticker("^DJI")
        daily = ticker.history(period="5d", interval="1d")
        if len(daily) < 2:
            raise ValueError("Not enough data")
        # Use last two completed sessions
        latest_close = daily["Close"].iloc[-1]
        prev_close = daily["Close"].iloc[-2]
        change_pct = ((latest_close - prev_close) / prev_close) * 100
        print(f"[Dow Jones] close={latest_close:.2f}, prev_close={prev_close:.2f}, chg={change_pct:.2f}%")
        return fmt_price(latest_close, change_pct)
    except Exception as e:
        print(f"[Dow Jones] ERROR: {e}")
        return "N/A (fetch error)"


def get_et_headline():
    try:
        url = "https://economictimes.indiatimes.com/markets/stocks/news"
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        keywords = ["open", "gap", "nifty", "sensex", "market"]

        # Try story containers first
        for cls in ["eachStory", "story-box", "articleList"]:
            stories = soup.find_all(class_=cls)
            for story in stories:
                tag = story.find(["h3", "h2", "a"])
                if tag and tag.get_text(strip=True):
                    text = tag.get_text(strip=True)
                    if any(kw in text.lower() for kw in keywords):
                        headline = text[:120] + ("..." if len(text) > 120 else "")
                        print(f"[ET Headline] Found in .{cls}: {headline}")
                        return headline

        # Fallback: scan all h2/h3 tags
        for tag in soup.find_all(["h2", "h3"]):
            text = tag.get_text(strip=True)
            if text and any(kw in text.lower() for kw in keywords):
                headline = text[:120] + ("..." if len(text) > 120 else "")
                print(f"[ET Headline] Fallback h-tag: {headline}")
                return headline

        # Last resort: first h2 or h3
        tag = soup.find(["h2", "h3"])
        if tag:
            text = tag.get_text(strip=True)
            headline = text[:120] + ("..." if len(text) > 120 else "")
            print(f"[ET Headline] Last-resort: {headline}")
            return headline

        return "N/A (no headline found)"
    except Exception as e:
        print(f"[ET Headline] ERROR: {e}")
        return "N/A (fetch error)"


def build_message(gift_nifty_str, gift_change_pct, dow_str, headline):
    dot = "🟢" if gift_change_pct >= 0 else "🔴"
    message = (
        f"📊 *Morning Market Brief*\n"
        f"━━━━━━━━━━━━━━━\n"
        f"{dot} *Gift Nifty* (8:45 AM): {gift_nifty_str}\n"
        f"🇺🇸 *Dow Jones* (prev close): {dow_str}\n"
        f"━━━━━━━━━━━━━━━\n"
        f"📰 *ET:* {headline}"
    )
    return message


def send_whatsapp(message):
    phone = os.environ.get("CALLMEBOT_PHONE", "")
    apikey = os.environ.get("CALLMEBOT_APIKEY", "")
    if not phone or not apikey:
        print("[WhatsApp] ERROR: CALLMEBOT_PHONE or CALLMEBOT_APIKEY not set")
        return
    url = (
        f"https://api.callmebot.com/whatsapp.php"
        f"?phone={phone}&text={urllib.parse.quote(message)}&apikey={apikey}"
    )
    try:
        resp = requests.get(url, timeout=10)
        print(f"[WhatsApp] Sent — HTTP {resp.status_code}")
    except Exception as e:
        print(f"[WhatsApp] ERROR sending: {e}")


def main():
    print("=== Market Brief Starting ===")
    gift_nifty_str, gift_change_pct = get_gift_nifty()
    dow_str = get_dow_jones()
    headline = get_et_headline()

    message = build_message(gift_nifty_str, gift_change_pct, dow_str, headline)
    print("\n--- Message Preview ---")
    print(message)
    print("-----------------------\n")

    send_whatsapp(message)
    print("=== Done ===")


if __name__ == "__main__":
    main()