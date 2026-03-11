## 2025-02-11 - API Efficiency & Lookups
**Learning:** Connection pooling with `requests.Session()` provides a significant performance boost (~5x) when fetching multiple assets (like icons) from the same host. Algorithmic optimizations from O(N) to O(1) in champion lookups significantly reduce redundant computation in session updates.
**Action:** Always prefer `requests.Session()` for API clients and use hash map lookups for frequently accessed data.

## 2025-02-12 - Data Parsing & Initialization
**Learning:** Inconsistent data types in API responses (e.g., winrates appearing as both `int` and `float`) can cause parsing logic to fail silently, leading to redundant fallback network requests.
**Action:** Ensure parsing logic is robust to common type variations (using `isinstance(val, (int, float))`) to avoid expensive network-based fallbacks.

## 2025-02-13 - Parallel Initialization & Fetching
**Learning:** Parallelizing network-bound initialization (like `ApiService` components) and multiple fallback fetches (like missing winrates in `LoLalytics`) provides significant startup performance gains (~20-40%) without sacrificing code readability.
**Action:** Use `concurrent.futures.ThreadPoolExecutor` for independent network-bound tasks during application startup or bulk data retrieval. Always specify `max_workers` when calling external APIs to avoid rate-limiting.

## 2025-02-14 - Parallelizing API Components
**Learning:** Parallelizing network-bound tasks within a single API class initialization (like `LolWiki` fetching its module while initializing its `LoLalytics` dependency) can yield significant startup improvements (~38%). This is especially effective when the dependency itself is also doing network-bound work.
**Action:** Identify and parallelize independent network-bound initialization steps within API wrapper classes.
