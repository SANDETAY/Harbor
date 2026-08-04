# Supabase (runtime + SQL)

**This folder path is used by the app.** Keep the name `docs/supabase`.

| File / folder | Purpose |
|---------------|---------|
| `config.local.js` | Your project URL + anon key (**gitignored**, required for cloud) |
| `config.example.js` | Template if present — copy to `config.local.js` |
| `schema.sql` | Core tables |
| `schema-c1-household.sql` | Household membership |
| `schema-c1b-display-name.sql` | Display names |
| `schema-c1c-life-share.sql` | Life share |
| `schema-d-calendar-oauth.sql` | Calendar OAuth storage |
| `FIX-*.sql` | One-time SQL fixes — run in Supabase SQL Editor |
| `functions/` | Edge functions (calendar OAuth) |

**How to operate:** [../handbook/05-backend-and-cloud.md](../handbook/05-backend-and-cloud.md)  
**Dashboards:** [../bookmarks/BOOKMARKS.md](../bookmarks/BOOKMARKS.md)
