# Locket — Partner Package

This is the package you got from your partner. Running it once makes a sweet
note show up on your Mac's login/lock screen, and it keeps itself updated.

## Install (one time)

Unpack and run the installer:

```bash
tar xzf locket-partner.tar.gz
cd locket-partner
./install.sh
```

It'll ask for your password once — that's to allow the single command that
writes the lock screen text. Nothing else.

### If your partner is sending it to you over the network

They run this from their machine (replace the user + IP):

```bash
scp locket-partner.tar.gz you@YOUR_IP:~/
ssh you@YOUR_IP 'tar xzf locket-partner.tar.gz && cd locket-partner && ./install.sh'
```

(Both Macs need to be reachable — same network, or Tailscale/VPN. SSH “Remote
Login” must be on under System Settings → General → Sharing.)

## What it does

- Installs to `~/.locket`
- Adds a Login Item (LaunchAgent `com.locket.agent`) that runs at every login
  and refreshes every 30 minutes while you're logged in
- Pulls whatever note is currently “live” and shows it on the lock screen

## Uninstall

```bash
cd locket-partner && ./uninstall.sh
```

## Notes

- macOS only for now (uses `LoginwindowText`).
- Keychain isn't used here since the device token is read-only and scoped to
  one function; the config lives in `~/.locket/locket.conf.json` (chmod 600).
- Tahoe may ask to grant Automation/Full Disk Access to `python3` the first
  time — allow it if the lock screen doesn't change.
