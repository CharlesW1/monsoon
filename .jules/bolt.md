## 2026-02-14 - DataDragon O(1) Lookup & Connection Pooling
**Learning:** Even small linear searches in frequently called methods can become significant bottlenecks when combined with I/O and lack of connection pooling. The DataDragon icon lookup was O(N) even for cached results, leading to a 0.5ms overhead per call.
**Action:** Always check if a loop can be replaced by a hash map lookup for frequently queried static data, and ensure `requests.Session()` is used for any class making multiple network calls.
