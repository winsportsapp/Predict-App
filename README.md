# Sports Prediction

A points-based sports prediction game built with Django. Users predict the
winner of a match before its deadline; the admin enters the result and each
prediction scores +10 (correct) or -5 (incorrect).

## Local development

```
python -m venv .venv
.venv/bin/pip install -r requirements.txt      # Windows: .venv\Scripts\pip
python manage.py migrate
python manage.py runserver
```

Local development uses SQLite (`db.sqlite3`) and needs no configuration. To
override anything locally, copy `.env.example` to `.env`.

## Production runtime

| | |
|---|---|
| OS | Linux |
| Python | 3.13 (see `.python-version`) |
| WSGI server | Gunicorn 23 |
| Gunicorn entrypoint | `config.wsgi:application` |

Set `DATABASE_URL` (PostgreSQL) and the other variables listed in
`.env.example`. Deploy-time steps: install `requirements.txt`, run
`python manage.py collectstatic --noinput`, run `python manage.py migrate`,
then start `gunicorn config.wsgi:application`.

Password-reset emails are sent through Resend. Set `RESEND_API_KEY` and
`DEFAULT_FROM_EMAIL` (a sender on a domain verified in Resend) in production;
without a key, emails are printed to the console.

## Scheduled Tasks

Match synchronization runs automatically for all 5 sports (Football, Cricket, Tennis, Badminton, Hockey) via the FlashLive Sports API on RapidAPI. Fixtures, odds, and results use the Primary key (`RAPIDAPI_KEY`) with automatic bidirectional failover to the Secondary key (`RAPIDAPI_STATS_KEY`).

### Option A: Background Scheduler Daemon (Recommended for Local Dev & Background Worker)
Run the built-in scheduler daemon in a terminal or double-click `scripts\start_scheduler_daemon.bat`:
```bash
python manage.py run_scheduler
```
This automatically executes:
- **06:30 IST**: Morning Results
- **06:35 IST**: Morning Fixtures & Odds
- **20:30 IST**: Evening Results
- **20:35 IST**: Evening Fixtures & Odds

### Option B: Windows Task Scheduler (Windows Local)
To register the 4 daily tasks directly in Windows Task Scheduler (configured with laptop battery resilience, sleep/wake catch-up, and timestamped logging in `logs/auto_sync.log`):
```powershell
powershell -ExecutionPolicy Bypass -File scripts/setup_windows_scheduler.ps1
```

### Option C: Cron (Linux / VPS / Railway Scheduled Tasks)
#### Server Timezone: UTC (Default on Railway, AWS, DigitalOcean, Heroku)
```cron
# 1. Results Fetch (06:30 IST & 20:30 IST / 01:00 UTC & 15:00 UTC):
0 1,15 * * * cd /path/to/project && /path/to/venv/bin/python manage.py sync_external_matches --results

# 2. Fixtures & Odds (06:35 IST & 20:35 IST / 01:05 UTC & 15:05 UTC):
5 1,15 * * * cd /path/to/project && /path/to/venv/bin/python manage.py sync_external_matches --fixtures --new-day-only
```

#### Server Timezone: IST (`Asia/Kolkata`)
```cron
# 1. Results Fetch (06:30 IST & 20:30 IST):
30 6,20 * * * cd /path/to/project && /path/to/venv/bin/python manage.py sync_external_matches --results

# 2. Fixtures & Odds (06:35 IST & 20:35 IST):
35 6,20 * * * cd /path/to/project && /path/to/venv/bin/python manage.py sync_external_matches --fixtures --new-day-only
```




