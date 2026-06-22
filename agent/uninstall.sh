#!/bin/bash
LABEL="com.locket.agent"
PLIST="$HOME/Library/LaunchAgents/com.locket.agent.plist"
launchctl unload -w "$PLIST" 2>/dev/null || true
rm -f "$PLIST"
rm -rf "$HOME/.locket"
sudo rm -f /etc/sudoers.d/locket
sudo defaults delete /Library/Preferences/com.apple.loginwindow LoginwindowText 2>/dev/null || true
echo "Locket removed."
