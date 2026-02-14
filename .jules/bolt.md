## 2025-02-11 - API Efficiency & Lookups
**Learning:** Connection pooling with `requests.Session()` provides a significant performance boost (~5x) when fetching multiple assets (like icons) from the same host. Algorithmic optimizations from O(N) to O(1) in champion lookups significantly reduce redundant computation in session updates.
**Action:** Always prefer `requests.Session()` for API clients and use hash map lookups for frequently accessed data.
