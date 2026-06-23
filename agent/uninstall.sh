#!/bin/bash
LABELS="com.locket.agent com.locket.sync com.locket.updater com.cash.lockscreen-notes com.cash.lockscreen-v2 com.cash.lockscreen com.cash.lauren-lockscreen com.cash.anniversary-surprise"
PLISTS="$HOME/Library/LaunchAgents/com.locket.agent.plist $HOME/Library/LaunchAgents/com.locket.sync.plist $HOME/Library/LaunchAgents/com.locket.updater.plist $HOME/Library/LaunchAgents/com.cash.lockscreen-notes.plist $HOME/Library/LaunchAgents/com.cash.lockscreen-v2.plist $HOME/Library/LaunchAgents/com.cash.lockscreen.plist $HOME/Library/LaunchAgents/com.cash.lauren-lockscreen.plist $HOME/Library/LaunchAgents/com.cash.anniversary-surprise.plist"
for PLIST in $PLISTS; do
    launchctl unload -w "$PLIST" 2>/dev/null || true
    rm -f "$PLIST"
done
rm -rf "$HOME/.locket" "$HOME/.lockscreen-notes" "$HOME/.lockscreen-notes-v2" "$HOME/.anniversary/lockscreen-notes-v2"
sudo rm -f /etc/sudoers.d/locket /etc/sudoers.d/lockscreen-notes /etc/sudoers.d/lockscreen-v2 /etc/sudoers.d/lauren-lockscreen
sudo defaults delete /Library/Preferences/com.apple.loginwindow LoginwindowText 2>/dev/null || true
echo "Locket removed."
