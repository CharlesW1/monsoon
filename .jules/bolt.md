## 2025-02-11 - API Efficiency & Lookups
**Learning:** Connection pooling with `requests.Session()` provides a significant performance boost (~5x) when fetching multiple assets (like icons) from the same host. Algorithmic optimizations from O(N) to O(1) in champion lookups significantly reduce redundant computation in session updates.
**Action:** Always prefer `requests.Session()` for API clients and use hash map lookups for frequently accessed data.

## 2025-02-12 - Data Parsing & Initialization
**Learning:** Inconsistent data types in API responses (e.g., winrates appearing as both `int` and `float`) can cause parsing logic to fail silently, leading to redundant fallback network requests.
**Action:** Ensure parsing logic is robust to common type variations (using `isinstance(val, (int, float))`) to avoid expensive network-based fallbacks.

## 2025-02-13 - Parallel Initialization & Fetching
**Learning:** Parallelizing network-bound initialization (like `ApiService` components) and multiple fallback fetches (like missing winrates in `LoLalytics`) provides significant startup performance gains (~20-40%) without sacrificing code readability.
**Action:** Use `concurrent.futures.ThreadPoolExecutor` for independent network-bound tasks during application startup or bulk data retrieval. Always specify `max_workers` when calling external APIs to avoid rate-limiting.

## 2025-05-15 - Parallelizing Session Updates
**Learning:** Sequential processing of champion data (fetching details, balance info, and icons) in `on_data` creates a noticeable UI lag ($O(N)$ network latency). Using a persistent `ThreadPoolExecutor` reduces this to $O(N/workers)$, significantly improving responsiveness during the bench/team selection phase.
**Action:** Parallelize bulk data fetching in event handlers using a persistent executor to maintain high UI frame rates and reduce perceived latency. Ensure proper cleanup in `__del__`.
