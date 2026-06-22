# Locket — Notion setup (one time)

Locket uses **Notion as the backend** — no server. You manage notes from the
Notion app on your phone; the partner's Mac reads whichever note is marked
**Live** and shows it on the lock screen.

## 1. The database

You already have **Locket — Notes** in your workspace. Columns:

- **Note** (title) — the exact text shown on the lock screen (keep ≤100 chars).
- **Live** (checkbox) — check ONE to make it the live one.
- **Vibe** (select) — just for you to organize.
- **Last Shown** (date) — the agent stamps this when it pushes a note.
- **Added** (created time).

## 2. Make an internal integration

1. Go to notion.so/my-integrations → **New integration** (Internal).
2. Name it `Locket`, give it **Read content** + **Update content** (update is
   only needed if you want the “Last Shown” stamp; read-only is fine otherwise).
3. Copy the **Internal Integration Secret** (`secret_...` / `ntn_...`).

## 3. Share the database with it

Open **Locket — Notes** → `⋯` menu → **Connections** → add `Locket`.
Without this the token can't see the database.

## 4. Get the database ID

Open the database as a full page, copy the URL. The 32-char chunk before `?v=`
is the database ID. (The setup script also accepts the whole URL and extracts it.)

## 5. Run the Startup Package

```bash
cd bootstrap
python3 setup.py
```

Paste the token + database ID. It verifies, then builds `locket-partner.tar.gz`
plus the exact `scp`/`ssh` commands to send it to your partner's Mac.

## Phone app

There's no separate PWA — your “app” is the **Notion mobile app** open to
**Locket — Notes**. Add it to your home screen for one-tap access. Toggle
**Live** on any note and it shows up next time they log in.
