# Locket — Notion setup (one time)

Locket uses **Notion as the backend** — no server. You manage notes from the Notion app; the recipient's Mac reads whichever note is **Live** and shows it on the lock screen.

## 1. Create the database

Easiest: paste this to **Notion AI**:

```
Create a new database called "Locket — Notes" with these properties:
- Note (title)
- Live (checkbox)
- Vibe (select with options: sweet, silly, hype, inside joke, real one)
- Last Shown (date)
- Added (created time)
Add a board view "Live board" grouped by Live, and a table view "All notes" sorted by Added newest first.
```

Or build it by hand with those columns:

- **Note** (title) — the exact text shown on the lock screen (keep ≤100 chars).
- **Live** (checkbox) — check ONE to make it the live one.
- **Vibe** (select) — optional, for organizing.
- **Last Shown** (date) — the agent stamps this when it pushes a note.
- **Added** (created time).

## 2. Make an internal integration

1. https://www.notion.so/my-integrations → **New integration** (Internal).
2. Name it `Locket`. Give it **Read content** + **Update content**. (Update powers the "Last Shown" stamp and the auto-enforce-one-Live behavior; read-only works but can't self-correct.)
3. Copy the **Internal Integration Secret** (`ntn_...` / `secret_...`).

## 3. Share the database with it

**Locket — Notes** → `•••` → **Connections** → add `Locket`. Required, or the token can't see the database.

## 4. Get the database ID

Open the database as a full page, copy the URL; the 32-char chunk before `?v=` is the ID. (setup.py also accepts the whole URL.)

## 5. Build the package

```bash
cd bootstrap
python3 setup.py
```

Paste the token + database ID. It verifies, then builds `locket-partner.tar.gz` plus the `scp` / `ssh` commands to send it to the recipient's Mac.

## Phone

Your "app" is the **Notion mobile app** open to **Locket — Notes**. Add it to your home screen. Check **Live** on any note and it shows up within a minute on the recipient's Mac.
