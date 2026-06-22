# 💌 Locket

Leave a little note on your partner's Mac lock screen. Personal build — no
server, **Notion is the backend**.

- **Your phone app** = the Notion mobile app, open to your **Locket — Notes** DB.
- **Mark a note Live** → the partner's Mac shows it on the lock screen at next login.
- **One-time setup** on the partner's Mac via a tiny package you send them.

## How it works

```
you (Notion app) --> Locket — Notes DB --> partner's Mac agent --> lock screen
     mark Live          (Live = true)        reads on login
```

## Layout

- `NOTION-SETUP.md` — start here: integration token, sharing, database ID.
- `bootstrap/` — the Startup Package you run on your Mac. Bakes your Notion
  token + DB ID into a partner package and prints the send commands.
- `agent/` — what the partner runs once. Installs a Login Item that reads the
  Live note from Notion and writes the lock screen. macOS only.
- `docs/ARCHITECTURE.md` — the full picture + security notes.

## Quick start

1. Read `NOTION-SETUP.md`, make the integration, share the DB, grab the IDs.
2. `cd bootstrap && python3 setup.py` → builds `locket-partner.tar.gz`.
3. Send it to your partner's Mac, they run `./install.sh` once.
4. Toggle **Live** on any note from your phone. Done.
