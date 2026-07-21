# MINBEIS Automation Engine v1

Πρώτη λειτουργική βάση αυτοματοποίησης MINBEIS.

## Τι κάνει

- Διαβάζει watch universe από YAML.
- Τραβάει delayed/daily market data μέσω public adapter.
- Διαβάζει επίσημα RSS της Euronext Athens και συμπληρωματικά news feeds.
- Υποστηρίζει ελληνικά και αγγλικά aliases ανά εκδότη.
- Υπολογίζει valuation gates ανά κλάδο.
- Υπολογίζει technical setup, entry zone, SMA20/SMA50, ATR, recent support και invalidation.
- Υπολογίζει risk sizing και μέγιστη μοντελοποιημένη ζημιά ως ποσοστό χαρτοφυλακίου.
- Παράγει `NO BUY`, `PAPER BUY` ή ελεγχόμενο `BUY PROBE`.
- Γράφει αποτελέσματα σε Google Sheet όταν υπάρχουν ασφαλή credentials.
- Παράγει Broker Export CSV μόνο για ανθρώπινη έγκριση.
- Τρέχει compile, tests, deterministic fixture, live-data smoke και artifact export μέσω GitHub Actions.

## Τι ΔΕΝ κάνει

- Δεν πατάει εντολές σε broker.
- Δεν κάνει intraday scalping.
- Δεν χρησιμοποιεί leverage.
- Δεν μετατρέπει ελλιπή δεδομένα σε αγορά.
- Δεν χρησιμοποιεί fixture data για Google Sheet writeback.

## Κανόνες ασφαλείας

```text
failed data source → NO BUY
failed valuation → NO BUY
failed price setup → NO BUY
missing invalidation → NO BUY
missing risk cap → NO BUY
event pending → NO BUY
real order → human only
```

## BUY PROBE

Πρώτη πραγματική υποψήφια θέση επιτρέπεται μόνο όταν:

```text
theme = PASS
numbers = PASS
valuation = PASS
price setup = PASS
invalidation = YES
risk cap = YES
```

Το v1 περιορίζει το `BUY PROBE` σε 0,25%–0,75% του χαρτοφυλακίου. `BUY STARTER` και `BUY CORE` απαιτούν μελλοντικό follow-up/portfolio module και δεν δίνονται αυτόματα στην πρώτη είσοδο.

## Εκτέλεση

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python run_minbeis.py --dry-run
```

Deterministic engine test:

```bash
python run_minbeis.py --dry-run --fixture
```

## Google Sheets writeback

Απαιτεί Google Cloud service account JSON και πρόσβαση στο Sheet.

```bash
SPREADSHEET_ID=1LnWr8AY9uYMsw93VArfiRfbu75Aod5Z1hAv9mOYHOYo
GOOGLE_APPLICATION_CREDENTIALS=/secure/path/service-account.json
MINBEIS_WRITEBACK=true
```

Το service-account JSON δεν αποθηκεύεται ποτέ στο repository.

## Τρέχον όριο δεδομένων

Το public/delayed adapter είναι MVP και όχι αδειοδοτημένο επαγγελματικό market feed. Η Euronext παρέχει επίσημα delayed/real-time/historical web services και machine-readable προϊόντα, τα οποία μπορούν να αντικαταστήσουν το prototype adapter όταν αποφασιστεί σχετική συνδρομή ή άδεια.
