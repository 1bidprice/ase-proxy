# MINBEIS Automation Engine v1

Πρώτη λειτουργική βάση για αυτοματοποίηση MINBEIS.

## Τι κάνει

- Διαβάζει watch universe από YAML.
- Τραβάει delayed/daily market data μέσω public adapter.
- Διαβάζει news RSS feeds.
- Τρέχει conservative MINBEIS scoring.
- Τρέχει Buy Engine με κανόνα ασφαλείας:
  - αν λείπει price/valuation/invalidation/risk cap → NO BUY / 0%.
- Γράφει αποτελέσματα σε Google Sheet όταν υπάρχουν credentials.
- Παράγει broker export CSV μόνο για ανθρώπινη έγκριση.

## Τι ΔΕΝ κάνει

- Δεν πατάει εντολές σε broker.
- Δεν κάνει intraday scalping.
- Δεν χρησιμοποιεί leverage.
- Δεν παράγει BUY όταν λείπουν δεδομένα.
- Δεν υποκαθιστά επενδυτικό σύμβουλο.

## Γρήγορη εγκατάσταση

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python run_minbeis.py --dry-run
```

## Google Sheets writeback

Για writeback χρειάζεται service account JSON από Google Cloud και να δοθεί access στο Sheet.

`.env`:

```bash
SPREADSHEET_ID=1LnWr8AY9uYMsw93VArfiRfbu75Aod5Z1hAv9mOYHOYo
GOOGLE_APPLICATION_CREDENTIALS=/secure/path/service-account.json
MINBEIS_WRITEBACK=true
```

## Ασφάλεια

```text
missing data → SOURCE INCOMPLETE
missing valuation → NO BUY
missing invalidation → NO BUY
missing risk cap → NO BUY
API error → ERROR / NO BUY
```
