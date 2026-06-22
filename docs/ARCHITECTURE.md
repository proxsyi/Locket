# Locket — Architecture (Notion backend, personal build)

```
   you, phone           Notion                     partner's Mac
  ┌──────────┐      ┌─────────────┐        ┌───────────────┐
  │ Notion   │─────▶│ Locket Notes │◀─────│ LaunchAgent    │
  │ app:     │ set  │ Live = true  │ read   │ at login +     │
  │ mark Live│      │ (one row)    │ (token)│ every 30 min    │
  └──────────┘      └─────────────┘        └──────┬───────┘
                                                  ▼ defaults write
                                          💌 LoginwindowText
```

## Why no server

Notion is the database + the API. Your phone writes via the Notion app; the Mac
reads via the Notion API. Nothing to host, nothing to pay for.

## Pieces

- **Notion DB (`Locket — Notes`)** — one row per note. `Live` checkbox marks the
  active one. The agent queries `Live = true`, newest-edited wins.
- **Bootstrap (`bootstrap/setup.py`)** — runs on your Mac. Verifies your Notion
  token + DB ID, bakes them into the agent config, emits `locket-partner.tar.gz`
  and the `scp`/`ssh` commands.
- **Agent (`agent/`)** — runs on the partner's Mac. `install.sh` drops it in
  `~/.locket`, adds a narrow single-command sudoers rule, registers a
  LaunchAgent (RunAtLoad + 30-min StartInterval). `locket-agent.py` GETs the
  Live note and writes `LoginwindowText`.

## Security model

- The partner's Mac holds a Notion **integration token** scoped to ONE database
  you explicitly shared with it. It can't see the rest of your workspace.
- Use a **read-only** integration if you don't care about the “Last Shown” stamp.
- Token lives in `~/.locket/locket.conf.json` (chmod 600). Harden by moving it
  into the login Keychain if you want.
- Kill switch: remove the integration from the DB's Connections (or uncheck all
  Live notes). Agent then gets nothing and leaves the screen as-is. Full removal:
  `uninstall.sh`.

## Limits / TODO

- macOS-only agent (uses `LoginwindowText`). Windows/Linux would each need their
  own installer + display path.
- Poll model (login + 30-min interval), not push. Fine for lock-screen notes.
- Single device assumed. Multiple partner Macs = run the installer on each.
- Notion rate limits are ~3 req/s — a non-issue at this cadence.
