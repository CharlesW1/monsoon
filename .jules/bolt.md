## 2026-02-13 - [API Connection Pooling and O(1) Lookups]
**Learning:** League of Legends API interactions (DataDragon, LoLalytics, etc.) often involve multiple small requests (e.g., icons, winrates). Using `requests.Session()` significantly reduces latency by reusing TCP connections. Additionally, linear scans (O(n)) of champion data are inefficient for frequent updates during champion select.
**Action:** Always implement session pooling for API clients and use dictionary-based mappings for frequent data lookups.

## 2026-02-13 - [CI Release Workflow Failure]
**Learning:** Release workflows that perform version bumping and tagging should be restricted to the `main` branch to avoid conflicts and unnecessary runs on feature branches. Additionally, `fetch-depth: 0` is often required for git-based version checks or tagging steps to ensure the local repository has all remote tags.
**Action:** Restrict release-triggering workflows to `main` and use `fetch-depth: 0` when tag history is required.
