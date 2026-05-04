# 📊 WhatsApp Morning Market Brief

Automated daily WhatsApp message at **8:55 AM IST (Mon–Fri)** with:
- 🟢/🔴 Gift Nifty (latest value as of ~8:45 AM)
- 🇺🇸 Dow Jones previous close
- 📰 Top Economic Times market headline

Powered by GitHub Actions + [CallMeBot](https://www.callmebot.com/) (free, no credit card).

---

## 1. One-Time CallMeBot Setup

1. Save **+34 644 65 29 86** as a contact (name it anything, e.g. "CallMeBot")
2. Send this exact message to that number on WhatsApp:
   ```
   I allow callmebot to send me messages
   ```
3. You'll receive a reply with your **API key** (a short number like `1234567`)

---

## 2. Add GitHub Secrets

Go to your repo → **Settings → Secrets and variables → Actions → New repository secret**

| Secret name | Value |
|---|---|
| `CALLMEBOT_PHONE` | Your phone with country code, no `+` — e.g. `919876543210` |
| `CALLMEBOT_APIKEY` | The API key received from CallMeBot in step 1 |

---

## 3. Test Manually (Recommended Before Waiting Till 8:55 AM)

1. Go to the **Actions** tab in this repo
2. Click **"Morning Market Brief"** in the left sidebar
3. Click **"Run workflow"** → **"Run workflow"**
4. Watch the logs — you should receive the WhatsApp message within ~30 seconds

---

## 4. Local Testing

```bash
pip install -r requirements.txt
export CALLMEBOT_PHONE=919876543210
export CALLMEBOT_APIKEY=1234567
python main.py
```

On Windows (PowerShell):
```powershell
$env:CALLMEBOT_PHONE = "919876543210"
$env:CALLMEBOT_APIKEY = "1234567"
python main.py
```

---

## Schedule

Runs automatically at **3:25 AM UTC = 8:55 AM IST**, Monday–Friday.

To change the time, edit the cron in `.github/workflows/daily.yml`:
```yaml
- cron: '25 3 * * 1-5'   # min hour day month weekday
```
