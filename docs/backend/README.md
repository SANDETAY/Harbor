# Backend

Harbor’s backend is **optional** and lives primarily under:

→ **[../supabase/](../supabase/)** (SQL, edge functions, `config.local.js`)  
→ **[../auth/](../auth/)** (how to wire Apple / Google / email; calendar OAuth separate)  
→ **[../handbook/05-backend-and-cloud.md](../handbook/05-backend-and-cloud.md)** (runbook)  
→ **[../bookmarks/](../bookmarks/)** (dashboard links)

## Why `docs/supabase` stays at that path

The app loads cloud config from:

```text
./docs/supabase/config.local.js
```

That path is **runtime**. Do not rename the folder without updating `index.html`, `cap-prepare`, and native copies.
