#!/bin/bash
set -e
USER_NAME="$(whoami)"
ROOT="$HOME/.locket"
PLIST="$HOME/Library/LaunchAgents/com.locket.agent.plist"
LABEL="com.locket.agent"

echo "Installing Locket for $USER_NAME"
mkdir -p "$ROOT"
chmod 700 "$ROOT"
cp locket-agent.py "$ROOT/locket-agent.py"
cp locket.conf.json "$ROOT/locket.conf.json"
chmod 600 "$ROOT/locket.conf.json"
chmod 700 "$ROOT/locket-agent.py"

SUDO_RULE="$USER_NAME ALL=(root) NOPASSWD: /usr/bin/defaults write /Library/Preferences/com.apple.loginwindow LoginwindowText *"
echo "Adding a scoped sudoers rule (needs your password once)"
echo "$SUDO_RULE" | sudo tee /etc/sudoers.d/locket >/dev/null
sudo chmod 440 /etc/sudoers.d/locket

mkdir -p "$HOME/Library/LaunchAgents"
cat > "$PLIST" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key><string>$LABEL</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>$ROOT/locket-agent.py</string>
    </array>
    <key>RunAtLoad</key><true/>
    <key>StartInterval</key><integer>1800</integer>
    <key>LimitLoadToSessionType</key><string>Aqua</string>
    <key>StandardOutPath</key><string>$ROOT/stdout.log</string>
    <key>StandardErrorPath</key><string>$ROOT/stderr.log</string>
</dict>
</plist>
PLIST

launchctl unload "$PLIST" 2>/dev/null || true
launchctl load -w "$PLIST"
launchctl kickstart -k "gui/$(id -u)/$LABEL" 2>/dev/null || true

echo "Installed. It updates the lock screen at every login."
echo "Logs: $ROOT/log.txt"
