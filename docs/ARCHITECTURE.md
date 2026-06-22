# Locket — Architecture (Notion backend)

```
   you, phone           Notion                     their Mac
  ┌──────────┐      ┌───────────────┐       ┌─────────────────┐
  │ Notion   │─────▶│ Locket — Notes │◀──────│ LaunchAgent      │
  │ app:     │ set  │ Live = true    │ read   │ login +          │
  │ mark Live│      │ (one row)      │(token) │ every 60s        │
  └──────────┘      └───────────────┘       └───────┬─────────┘
                                                     ▼ defaults write
                                             💌 LoginwindowText
```

## Why no server

Notion is the database and the API. Your phone writes via the Notion app; the Mac reads via the Notion API. Nothing to host, nothing to pay for.

## Pieces

- **Notion DB (`Locket — Notes`)** — one row per note. `Live` marks the active one.
- **Bootstrap (`bootstrap/setup.py`)** — runs on your Mac. Verifies token + DB ID, bakes them into the agent config, emits `locket-partner.tar.gz` and the send commands.
- **Agent (`agent/`)** — runs on the recipient's Mac. `install.sh` drops it in `~/.locket`, adds a narrow single-command sudoers rule, and registers a LaunchAgent (RunAtLoad + 60-second StartInterval). `locket-agent.py` reads the Live note and writes `LoginwindowText`.

## Single-Live enforcement

Notion has no native "exactly one checkbox" constraint, so the agent enforces it every run:

- More than one Live → keep the most recently edited, uncheck the rest.
- Zero Live → auto-check the least recently shown.
- Exactly one Live → no change.

This needs the integration's **Update content** capability. Read-only falls back to "newest Live wins" with no self-correction.

## Security model

- Token scoped to ONE shared database; it can't see the rest of the workspace.
- Token in `~/.locket/locket.conf.json` (chmod 600), never committed.
- Kill switch: remove the integration from the database's Connections, or `uninstall.sh`.

## Limits / TODO

- macOS-only agent (uses `LoginwindowText`). Windows / Linux would each need their own installer and display path.
- Poll model (login + every 60s), not push. Fine for lock-screen notes.
- One Live note is shared across all devices. Multiple Macs show the same note; per-device notes would need an extra field.
- Notion rate limits (~3 req/s) are a non-issue at this cadence.
