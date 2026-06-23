#!/bin/bash
LABELS="com.locket.agent com.locket.sync com.locket.updater"
PLISTS="$HOME/Library/LaunchAgents/com.locket.agent.plist $HOME/Library/LaunchAgents/com.locket.sync.plist $HOME/Library/LaunchAgents/com.locket.updater.plist"
for PLIST in $PLISTS; do
    launchctl unload -w "$PLIST" 2>/dev/null || true
    rm -f "$PLIST"
done
rm -rf "$HOME/.locket"
sudo rm -f /etc/sudoers.d/locket
sudo defaults delete /Library/Preferences/com.apple.loginwindow LoginwindowText 2>/dev/null || true
echo "Locket removed."
