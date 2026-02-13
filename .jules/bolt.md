## 2026-02-13 - [API Connection Pooling and O(1) Lookups]
**Learning:** League of Legends API interactions (DataDragon, LoLalytics, etc.) often involve multiple small requests (e.g., icons, winrates). Using `requests.Session()` significantly reduces latency by reusing TCP connections. Additionally, linear scans (O(n)) of champion data are inefficient for frequent updates during champion select.
**Action:** Always implement session pooling for API clients and use dictionary-based mappings for frequent data lookups.
