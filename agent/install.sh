#!/bin/bash
set -e
MODE="$1"
VERSION_ARG="$2"
USER_NAME="$(whoami)"
ROOT="$HOME/.locket"
PLIST_DIR="$HOME/Library/LaunchAgents"
AGENT_PLIST="$PLIST_DIR/com.locket.agent.plist"
SYNC_PLIST="$PLIST_DIR/com.locket.sync.plist"
UPDATER_PLIST="$PLIST_DIR/com.locket.updater.plist"
AGENT_LABEL="com.locket.agent"
SYNC_LABEL="com.locket.sync"
UPDATER_LABEL="com.locket.updater"
SRC_DIR="$(cd "$(dirname "$0")" && pwd)"

copy_file() {
    FILE="$1"
    if [ -f "$SRC_DIR/$FILE" ]; then
        if [ "$SRC_DIR/$FILE" != "$ROOT/$FILE" ]; then
            cp "$SRC_DIR/$FILE" "$ROOT/$FILE"
        fi
    fi
}

write_agent_plist() {
    cat > "$AGENT_PLIST" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key><string>$AGENT_LABEL</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>$ROOT/locket-login.sh</string>
    </array>
    <key>RunAtLoad</key><true/>
    <key>LimitLoadToSessionType</key><string>Aqua</string>
    <key>StandardOutPath</key><string>$ROOT/stdout.log</string>
    <key>StandardErrorPath</key><string>$ROOT/stderr.log</string>
</dict>
</plist>
PLIST
}

write_sync_plist() {
    cat > "$SYNC_PLIST" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key><string>$SYNC_LABEL</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>$ROOT/locket-agent.py</string>
        <string>--sync</string>
    </array>
    <key>StartInterval</key><integer>60</integer>
    <key>LimitLoadToSessionType</key><string>Aqua</string>
    <key>StandardOutPath</key><string>$ROOT/stdout.log</string>
    <key>StandardErrorPath</key><string>$ROOT/stderr.log</string>
</dict>
</plist>
PLIST
}

write_updater_plist() {
    cat > "$UPDATER_PLIST" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key><string>$UPDATER_LABEL</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>$ROOT/locket-update.py</string>
    </array>
    <key>RunAtLoad</key><true/>
    <key>StartInterval</key><integer>3600</integer>
    <key>LimitLoadToSessionType</key><string>Aqua</string>
    <key>StandardOutPath</key><string>$ROOT/update-stdout.log</string>
    <key>StandardErrorPath</key><string>$ROOT/update-stderr.log</string>
</dict>
</plist>
PLIST
}


cleanup_legacy() {
    LEGACY_PLISTS="$HOME/Library/LaunchAgents/com.cash.lockscreen-notes.plist $HOME/Library/LaunchAgents/com.cash.lockscreen-v2.plist $HOME/Library/LaunchAgents/com.cash.lockscreen.plist $HOME/Library/LaunchAgents/com.cash.lauren-lockscreen.plist $HOME/Library/LaunchAgents/com.cash.anniversary-surprise.plist"
    for PLIST in $LEGACY_PLISTS; do
        launchctl unload -w "$PLIST" 2>/dev/null || true
        rm -f "$PLIST"
    done
    rm -rf "$HOME/.lockscreen-notes" "$HOME/.lockscreen-notes-v2" "$HOME/.anniversary/lockscreen-notes-v2"
    sudo rm -f /etc/sudoers.d/lockscreen-notes /etc/sudoers.d/lockscreen-v2 /etc/sudoers.d/lauren-lockscreen 2>/dev/null || true
}

load_plist() {
    PLIST="$1"
    LABEL="$2"
    SHOULD_KICK="$3"
    launchctl unload "$PLIST" 2>/dev/null || true
    launchctl load -w "$PLIST"
    if [ "$SHOULD_KICK" = "yes" ]; then
        launchctl kickstart -k "gui/$(id -u)/$LABEL" 2>/dev/null || true
    fi
}

echo "Installing Locket for $USER_NAME"
cleanup_legacy
mkdir -p "$ROOT"
chmod 700 "$ROOT"
copy_file locket-agent.py
copy_file locket-update.py
copy_file locket-login.sh
copy_file install.sh
copy_file uninstall.sh
copy_file README.md
if [ -f "$SRC_DIR/locket.conf.json" ]; then
    cp "$SRC_DIR/locket.conf.json" "$ROOT/locket.conf.json"
elif [ ! -f "$ROOT/locket.conf.json" ]; then
    echo "Missing locket.conf.json. Run setup.py first."
    exit 1
fi
chmod 600 "$ROOT/locket.conf.json"
chmod 700 "$ROOT/locket-agent.py" "$ROOT/locket-update.py" "$ROOT/locket-login.sh"
if [ -n "$VERSION_ARG" ]; then
    echo "$VERSION_ARG" > "$ROOT/version"
elif [ -f "$SRC_DIR/VERSION" ]; then
    cp "$SRC_DIR/VERSION" "$ROOT/version"
else
    echo "v0.2.0" > "$ROOT/version"
fi

if [ "$MODE" != "--update" ]; then
    SUDO_RULE="$USER_NAME ALL=(root) NOPASSWD: /usr/bin/defaults write /Library/Preferences/com.apple.loginwindow LoginwindowText *"
    echo "Adding a scoped sudoers rule (needs your password once)"
    echo "$SUDO_RULE" | sudo tee /etc/sudoers.d/locket >/dev/null
    sudo chmod 440 /etc/sudoers.d/locket
elif [ ! -f /etc/sudoers.d/locket ]; then
    echo "Update installed, but the sudoers rule is missing. Run install.sh manually once."
fi

mkdir -p "$PLIST_DIR"
write_agent_plist
write_sync_plist
write_updater_plist
load_plist "$AGENT_PLIST" "$AGENT_LABEL" "no"
load_plist "$SYNC_PLIST" "$SYNC_LABEL" "yes"
if [ "$MODE" != "--update" ]; then
    load_plist "$UPDATER_PLIST" "$UPDATER_LABEL" "no"
fi
if [ "$MODE" != "--update" ]; then
    launchctl kickstart -k "gui/$(id -u)/$AGENT_LABEL" 2>/dev/null || true
fi

echo "Installed. It rotates on login, syncs every 60 seconds, and checks for updates hourly."
echo "Logs: $ROOT/log.txt"
echo "Update logs: $ROOT/update.log"
