# 📊 Morning Market Brief — Email Edition

Automated daily email at **8:55 AM IST (Mon–Fri)** to `raunakbhiwal64@gmail.com` and `madhujotmadan@gmail.com` with:
- 🟢/🔴 Gift Nifty (latest value as of ~8:45 AM)
- 🇺🇸 Dow Jones previous close
- 📰 Top Economic Times market headline

Powered by **GitHub Actions + Gmail SMTP** (free, no third-party services).

---

## 1. Create a Gmail App Password (one-time)

> You must use an **App Password**, not your regular Gmail password.
> App Passwords require 2-Step Verification to be enabled on the sending account.

1. Go to → **https://myaccount.google.com/apppasswords**
2. Sign in if prompted
3. App name: `market-brief` → click **Create**
4. Copy the 16-character password shown (e.g. `abcd efgh ijkl mnop`)

---

## 2. Add GitHub Secrets

Go to your repo → **Settings → Secrets and variables → Actions → New repository secret**

| Secret name | Value |
|---|---|
| `GMAIL_USER` | The Gmail address you created the App Password for, e.g. `youremail@gmail.com` |
| `GMAIL_APP_PASSWORD` | The 16-char App Password from step 1 (spaces optional) |

---

## 3. Test Manually

1. Go to the **Actions** tab in this repo
2. Click **"Morning Market Brief"** in the left sidebar
3. Click **"Run workflow"** → **"Run workflow"**
4. Check both inboxes — email arrives within ~30 seconds

---

## 4. Local Testing

```bash
pip install -r requirements.txt
export GMAIL_USER=youremail@gmail.com
export GMAIL_APP_PASSWORD="abcd efgh ijkl mnop"
python main.py
```

On Windows (PowerShell):
```powershell
$env:GMAIL_USER = "youremail@gmail.com"
$env:GMAIL_APP_PASSWORD = "abcd efgh ijkl mnop"
python main.py
```

---

## Schedule

Runs automatically at **3:25 AM UTC = 8:55 AM IST**, Monday–Friday.

To change the time, edit the cron in `.github/workflows/daily.yml`:
```yaml
- cron: '25 3 * * 1-5'   # min hour day month weekday
```
