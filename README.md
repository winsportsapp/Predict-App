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

## Scheduled Tasks (Cron)

To stay strictly within the 500 RapidAPI requests/month limit (~14 requests/day) for FlashLive and 100 requests/day for API-Football, match synchronization runs on the following schedule:

### Server Timezone: UTC (Default on Railway, AWS, DigitalOcean, Heroku)
```cron
# 1. Results Fetch #1 at 06:30 IST (01:00 UTC):
0 1 * * * cd /path/to/project && /path/to/venv/bin/python manage.py sync_external_matches --results

# 2. Morning Fixtures & Odds at 06:35 IST (01:05 UTC):
5 1 * * * cd /path/to/project && /path/to/venv/bin/python manage.py sync_external_matches --fixtures --new-day-only

# 3. Results Fetch #2 at 20:30 IST (15:00 UTC):
0 15 * * * cd /path/to/project && /path/to/venv/bin/python manage.py sync_external_matches --results

# 4. Evening Next-Day Fixtures & Odds at 20:35 IST (15:05 UTC) [All sports, including Football]:
5 15 * * * cd /path/to/project && /path/to/venv/bin/python manage.py sync_external_matches --fixtures --days-ahead 1 --new-day-only
```

### Server Timezone: IST (`Asia/Kolkata`)
```cron
# 1. Results Fetch #1 at 06:30 IST:
30 6 * * * cd /path/to/project && /path/to/venv/bin/python manage.py sync_external_matches --results

# 2. Morning Fixtures & Odds at 06:35 IST:
35 6 * * * cd /path/to/project && /path/to/venv/bin/python manage.py sync_external_matches --fixtures --new-day-only

# 3. Results Fetch #2 at 20:30 IST:
30 20 * * * cd /path/to/project && /path/to/venv/bin/python manage.py sync_external_matches --results

# 4. Evening Next-Day Fixtures & Odds at 20:35 IST [All sports, including Football]:
35 20 * * * cd /path/to/project && /path/to/venv/bin/python manage.py sync_external_matches --fixtures --days-ahead 1 --new-day-only
```



