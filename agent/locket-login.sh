#!/bin/bash
ROOT="$HOME/.locket"
if [ -x "$ROOT/locket-update.py" ] || [ -f "$ROOT/locket-update.py" ]; then
    /usr/bin/python3 "$ROOT/locket-update.py" || true
fi
/usr/bin/python3 "$ROOT/locket-agent.py" --rotate
