# Core Rule: Absolute Truth & Full Verification (Zero Guessing)

1. **NO GUESSWORK OR TRUNCATION**:
   - Never assume, estimate, truncate, or guess counts, statuses, metrics, or file lists.
   - Never rely on a single page of API results (e.g. `pageSize=100` without a full `nextPageToken` pagination loop). Always paginate until `nextPageToken` is completely null/exhausted.
   - If loading or syncing takes time, let it load completely and process every page of data.

2. **DEEP ACCURACY ON ALL PLATFORMS & DASHBOARDS**:
   - Every number displayed to the user or saved to dashboard data files must reflect 100% real, fully scanned, verified ground truth from APIs and databases.
   - Sync all discovered real data across both `docs/` and `web/` directories and push to the live server/GitHub repository so web apps and dashboards reflect exact values.

3. **APPLIES GLOBALLY**:
   - This rule applies unconditionally to this project and all current and future projects.
