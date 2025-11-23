## Chinese movies with Mongolian subtitles (Flask demo)

- Sign up or log in to watch
- VIP subscription counts from the payment day
- VIP-only movies are protected; free movies are accessible to all authenticated users

### Quick start

1) Create and activate a virtualenv (optional)

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2) Install dependencies

```bash
pip3 install -r requirements.txt
```

3) Run the app (auto-inits DB and serves)

```bash
python3 run.py --serve            # default port 5000
python3 run.py --serve --port 8080  # custom port
# or: PORT=8080 python3 run.py --serve
```

Optional: initialize DB and seed demo content explicitly

```bash
python3 run.py --init-db --seed-demo --serve
```

Then open `http://localhost:5000` (or your chosen port).

### Notes
- Demo includes one sample movie (`Big Buck Bunny`) marked VIP-only and one Mongolian WebVTT subtitle at `app/static/subtitles/mn_sample.vtt`.
- VIP purchase is simulated and extends by 30 days. Existing active VIPs get extended from their current end date; otherwise it starts from today (payment day).
