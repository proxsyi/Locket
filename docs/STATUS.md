# Locket — current status

_Last updated: 2026-06-23_

## Current release

- Public repo: `proxsyi/Locket`
- Current shipped tag: `v0.2.3`
- Current installed version on Cash's Mac: `v0.2.3` intended after reinstall
- Current installed version on Lauren's Mac: `v0.2.3`
- Backend: Notion database (`Locket — Notes`)
- Runtime target: macOS lock screen text via `LoginwindowText`

## How it works now

Locket is a server-free macOS lock-screen note system backed by Notion.

1. Notes live in the user's Notion database.
2. Exactly one note is considered `Live`.
3. The installed Mac agent writes the current note to macOS `LoginwindowText`.
4. A login LaunchAgent is intended to check for updates first, then rotate to a different note and write it immediately.
5. A sync LaunchAgent runs every 60 seconds and writes the current `Live` note without rotating.
6. An updater LaunchAgent runs at login/hourly and checks GitHub tags for newer versions.
7. The installer removes known legacy lock-screen LaunchAgents from earlier private builds so they do not fight Locket.

## Runtime agents

| Label | Trigger | Purpose |
|---|---|---|
| `com.locket.agent` | `RunAtLoad` | Runs `locket-login.sh`: update check first, then `locket-agent.py --rotate` |
| `com.locket.sync` | every 60 seconds | Runs `locket-agent.py --sync` and keeps the lock screen matched to the current Live note |
| `com.locket.updater` | `RunAtLoad` + hourly | Runs `locket-update.py`, checks GitHub tags, downloads newer tagged versions, and reinstalls |

## Verified

- Repo is public and secret scan was clean.
- `v0.2.0`, `v0.2.1`, and `v0.2.3` were pushed to GitHub.
- `v0.2.1` installed and worked on Cash's Mac.
- `v0.2.1` installed and worked on Lauren's Mac.
- `v0.2.3` package was rebuilt and manually installed on Lauren's Mac.
- Lauren's Mac reports `~/.locket/version` as `v0.2.3`.
- Lauren's Mac has all three Locket LaunchAgents present.
- Lauren's sync logs show repeated successful `ok sync` writes.
- Lauren's updater log shows `ok: current v0.2.3`.

## Known bugs / open issues

### Login agent needs confirmation/fix on Lauren's Mac

After manually running:

```bash
ssh -tt elizabethhassenzahl@100.89.27.66 'launchctl kickstart -k gui/$(id -u)/com.locket.agent; sleep 2; tail -10 ~/.locket/update.log; tail -10 ~/.locket/log.txt'
```

The logs showed sync activity and the updater's existing `ok: current v0.2.3`, but did not show a fresh update-check or `ok rotate` line from the kickstarted login agent.

This means the intended v0.2.3 behavior — "check for update, then pull/rotate current message instantly on login" — is not fully verified yet on Lauren's Mac. Sync still works, so messages update within 60 seconds, but the instant-login path should be investigated.

Possible causes to check:

- `com.locket.agent` exits with status 1 because `locket-login.sh` is failing before logging.
- LaunchAgent `ProgramArguments` for shell script execution need to call `/bin/bash ~/.locket/locket-login.sh` instead of executing the script directly.
- `locket-login.sh` may need explicit logging before/after updater + rotate.
- `launchctl kickstart` may be targeting the wrong GUI session or firing before the user's Aqua session is fully ready.

### Token still needs rotation

The current Notion integration token has been pasted in chat and saved privately in the Notion project page. It is not committed to GitHub, but it should still be rotated before treating this as clean long-term deployment.

### Setup still needs `.env` convenience

GitHub issue #1 tracks local `.env` support for `bootstrap/setup.py`, so repeated package builds do not require typing the same Notion token, database URL, property names, and partner target.

## Next planned work

1. Fix and verify the instant-login path.
2. Add explicit login-script logs like `login: update check start`, `login: update check done`, `login: rotate start`, `login: rotate done`.
3. Consider changing the login LaunchAgent to run `/bin/bash ~/.locket/locket-login.sh` explicitly.
4. Rotate the Notion token and rebuild/reinstall the package.
5. Implement `.env` support for setup.py (GitHub issue #1).
6. Add a troubleshooting section for `launchctl list`, `kickstart`, sync logs, update logs, and uninstall.
