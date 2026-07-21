# MINBEIS Security Rules

1. Never paste broker passwords, API secrets, or service account JSON in chat.
2. Broker execution is disabled in v1.
3. Google Sheet writeback requires service account credentials stored securely.
4. If a data source fails, the system must output NO BUY.
5. If valuation, invalidation, or risk cap is missing, the system must output NO BUY.
6. Every run must write to Automation Run Log.
7. Human approval is required for any Broker Export row.
