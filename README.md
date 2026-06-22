# 💌 Locket

Leave a little note on someone's Mac lock screen, controlled from your phone. No server, no hosting, no monthly cost — **Notion is the backend**.

You keep a small database of notes in Notion. Mark one **Live**, and their Mac shows it on the login / lock screen. Change it anytime from the Notion app on your phone.

> macOS only for now. The lock screen text uses macOS's `LoginwindowText`.

## How it works

```
  you (Notion app)        Notion                  their Mac
 ┌──────────────┐   ┌─────────────────┐    ┌─────────────────────┐
 │ mark a note  │──▶│ Locket — Notes   │◀──│ LaunchAgent          │
 │ "Live"       │   │ (one Live row)   │    │ login + every 60s    │
 └──────────────┘   └─────────────────┘    └──────────┬──────────┘
                                                       ▼ defaults write
                                                💌 lock screen text
```

- Their Mac runs a tiny Python agent as a Login Item.
- Every login, and every 60 seconds while logged in, it reads the **Live** note from your Notion database and writes it to the lock screen.
- Exactly one note is ever Live — the agent enforces that (see below).

## What you need

- A free Notion account (web + the mobile app on your phone).
- The Mac that should receive the notes.
- Your own Mac to build and send the one-time setup package.
- About 10 minutes.

## Setup

### 1. Create the database in Notion

Build it by hand, or — easiest — paste this prompt to **Notion AI** and let it build the database for you:

```
Create a new database called "Locket — Notes" with these properties:
- Note (title)
- Live (checkbox)
- Vibe (select with options: sweet, silly, hype, inside joke, real one)
- Last Shown (date)
- Added (created time)
Add two views:
- A board view called "Live board" grouped by the Live checkbox
- A table view called "All notes" sorted by Added, newest first
Then add a few example notes in the Note column.
```

Property cheat sheet:

| Property | Type | What it's for |
|---|---|---|
| **Note** | Title | The exact text shown on the lock screen (keep it ≤100 chars) |
| **Live** | Checkbox | The one note currently on the lock screen |
| **Vibe** | Select | Optional, just for you to organize |
| **Last Shown** | Date | The agent stamps this when it pushes a note |
| **Added** | Created time | Auto |

### 2. Make a Notion integration

1. Go to https://www.notion.so/my-integrations → **New integration** → **Internal**.
2. Name it `Locket`. Give it **Read content** and **Update content** capabilities. (Update powers the "Last Shown" stamp and the auto-enforce-one-Live behavior. Read-only still shows notes but can't self-correct.)
3. Copy the **Internal Integration Secret** (starts with `ntn_` or `secret_`). Treat it like a password.

### 3. Share the database with the integration

Open **Locket — Notes** as a full page → `•••` menu → **Connections** → add **Locket**. Without this, the token can't see your database.

### 4. Get the database ID

Open the database as a full page and copy the URL. The 32-character chunk before `?v=` is the database ID. (The setup script also accepts the whole URL and pulls the ID out for you.)

### 5. Build the setup package (on your Mac)

```bash
git clone https://github.com/proxsyi/Locket.git
cd Locket/bootstrap
python3 setup.py
```

Paste your token and database ID/URL when asked, accept the property-name defaults, and it builds `locket-partner.tar.gz` — the only thing you send to the other Mac. It also prints ready-to-run send commands.

### 6. Install on the recipient's Mac

Get `locket-partner.tar.gz` onto their Mac (AirDrop, USB, or `scp`), then:

```bash
tar xzf locket-partner.tar.gz
cd locket-partner
./install.sh
```

It asks for their Mac password **once** — that authorizes a single scoped command (writing the lock screen text), nothing else. After that it runs at every login and refreshes every 60 seconds.

If both Macs are on the same network (or a VPN / Tailscale) with **Remote Login** turned on, you can push it remotely instead:

```bash
scp locket-partner.tar.gz USER@THEIR_IP:~/
ssh USER@THEIR_IP 'tar xzf locket-partner.tar.gz && cd locket-partner && ./install.sh'
```

### 7. Use it from your phone

Open the Notion app to **Locket — Notes** (add it to your home screen for one-tap access) and check **Live** on whichever note you want showing. It appears on their lock screen within a minute, or at their next login.

## The "always exactly one Live" rule

Notion can't enforce this on its own, so the agent does, every run:

- If **more than one** note is Live, it keeps the most recently edited one and unchecks the rest.
- If **no** note is Live, it auto-checks the least recently shown one.
- If exactly one is Live, it leaves everything alone.

So you can just check a new note and the previous one sorts itself out.

## Running it manually / checking logs

```bash
python3 ~/.locket/locket-agent.py
launchctl kickstart -k gui/$(id -u)/com.locket.agent
tail -f ~/.locket/log.txt
```

## Multiple Macs

Run `install.sh` on each Mac. They all read the same database and show the **same** Live note (there's one Live flag for everyone), and the same token works on all of them. You can't show different notes on different Macs with this setup — that would need a per-device field.

## Uninstall

```bash
cd locket-partner && ./uninstall.sh
```

Removes the Login Item, the config, the sudoers rule, and clears the lock screen text.

## Security

- The token is scoped to the **one** database you shared with it — it can't see the rest of your workspace.
- It lives in `~/.locket/locket.conf.json` (chmod 600) and is **never** committed to git.
- Kill switch: remove the integration from the database's Connections, or run `uninstall.sh`.
- Forking this public? Never commit `locket.conf.json` or `locket-partner*` — they hold your token and are gitignored for that reason.

## License

MIT. Do what you like with it.
