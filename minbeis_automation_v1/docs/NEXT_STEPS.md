# Next Steps

## Step 1 — Test dry run locally
```bash
pip install -r requirements.txt
python run_minbeis.py --dry-run
```

## Step 2 — Validate ticker mappings
Check whether each Athens ticker returns data:
- ALPHA.AT
- ETE.AT
- EUROB.AT
- TPEIR.AT
- AKTR.AT

If a ticker fails, set provider-specific symbol mapping.

## Step 3 — Google Sheets writeback
Create Google Cloud service account.
Share the MINBEIS Sheet with the service account email.
Set:
```bash
GOOGLE_APPLICATION_CREDENTIALS=/secure/path/service-account.json
MINBEIS_WRITEBACK=true
```

## Step 4 — Scheduled runs
Use GitHub Actions, Render cron, or Google Cloud Scheduler.

## Step 5 — Replace public data with official feeds
Move Greek market data to Euronext/ATHEX official or licensed source before serious use.

## Step 6 — Add valuation module
No BUY PROBE/STARTER/CORE before valuation, invalidation and risk cap modules exist.
