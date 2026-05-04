import os
import smtplib
import requests
import yfinance as yf
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from bs4 import BeautifulSoup


def fmt_price(price, change_pct):
    arrow = "▲" if change_pct >= 0 else "▼"
    return f"{price:,.0f} ({arrow}{abs(change_pct):.2f}%)"


def get_gift_nifty():
    try:
        ticker = yf.Ticker("^NSEI")
        intraday = ticker.history(period="1d", interval="1m")
        if intraday.empty:
            raise ValueError("Empty intraday data")
        latest_price = intraday["Close"].iloc[-1]

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

        for cls in ["eachStory", "story-box", "articleList"]:
            for story in soup.find_all(class_=cls):
                tag = story.find(["h3", "h2", "a"])
                if tag and tag.get_text(strip=True):
                    text = tag.get_text(strip=True)
                    if any(kw in text.lower() for kw in keywords):
                        headline = text[:120] + ("..." if len(text) > 120 else "")
                        print(f"[ET Headline] Found in .{cls}: {headline}")
                        return headline

        for tag in soup.find_all(["h2", "h3"]):
            text = tag.get_text(strip=True)
            if text and any(kw in text.lower() for kw in keywords):
                headline = text[:120] + ("..." if len(text) > 120 else "")
                print(f"[ET Headline] Fallback h-tag: {headline}")
                return headline

        tag = soup.find(["h2", "h3"])
        if tag:
            text = tag.get_text(strip=True)
            return text[:120] + ("..." if len(text) > 120 else "")

        return "N/A (no headline found)"
    except Exception as e:
        print(f"[ET Headline] ERROR: {e}")
        return "N/A (fetch error)"


def build_html(gift_nifty_str, gift_change_pct, dow_str, headline):
    dot   = "▲" if gift_change_pct >= 0 else "▼"
    color = "#16a34a" if gift_change_pct >= 0 else "#dc2626"
    return (
        f'<html><body style="margin:0;padding:12px 16px;font-family:Arial,sans-serif;font-size:13px;color:#111;">'
        f'<span style="font-weight:600;font-size:13px;">📊 Market Brief</span>'
        f'<span style="color:#9ca3af;font-size:11px;margin-left:6px;">8:55 AM IST</span><br><br>'
        f'<span style="color:{color};font-weight:700;">{dot} Gift Nifty</span>'
        f'&nbsp;&nbsp;<strong>{gift_nifty_str}</strong>'
        f'&emsp;'
        f'🇺🇸 <span style="font-weight:700;">Dow</span>'
        f'&nbsp;&nbsp;<strong>{dow_str}</strong><br><br>'
        f'<span style="color:#6b7280;font-size:12px;">ET — {headline}</span>'
        f'</body></html>'
    )


def build_plain(gift_nifty_str, gift_change_pct, dow_str, headline):
    dot = "▲" if gift_change_pct >= 0 else "▼"
    return (
        f"📊 Morning Market Brief\n"
        f"{'─'*32}\n"
        f"Gift Nifty (8:45 AM):   {gift_nifty_str}\n"
        f"Dow Jones (prev close): {dow_str}\n"
        f"{'─'*32}\n"
        f"ET: {headline}\n"
    )


def send_email(gift_nifty_str, gift_change_pct, dow_str, headline):
    gmail_user = os.environ.get("GMAIL_USER", "")
    gmail_password = os.environ.get("GMAIL_APP_PASSWORD", "")
    recipients = ["raunakbhiwal64@gmail.com", "madhujotmadan@gmail.com"]

    if not gmail_user or not gmail_password:
        print("[Email] ERROR: GMAIL_USER or GMAIL_APP_PASSWORD not set")
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "📊 Morning Market Brief"
    msg["From"] = f"Market Brief <{gmail_user}>"
    msg["To"] = ", ".join(recipients)

    plain = build_plain(gift_nifty_str, gift_change_pct, dow_str, headline)
    html = build_html(gift_nifty_str, gift_change_pct, dow_str, headline)
    msg.attach(MIMEText(plain, "plain"))
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.ehlo()
            server.starttls()
            server.login(gmail_user, gmail_password)
            server.sendmail(gmail_user, recipients, msg.as_string())
        print(f"[Email] Sent to {recipients}")
    except Exception as e:
        print(f"[Email] ERROR: {e}")


def main():
    print("=== Market Brief Starting ===")
    gift_nifty_str, gift_change_pct = get_gift_nifty()
    dow_str = get_dow_jones()
    headline = get_et_headline()

    print("\n--- Data ---")
    print(f"Gift Nifty : {gift_nifty_str}")
    print(f"Dow Jones  : {dow_str}")
    print(f"Headline   : {headline}")
    print("------------\n")

    send_email(gift_nifty_str, gift_change_pct, dow_str, headline)
    print("=== Done ===")


if __name__ == "__main__":
    main()
