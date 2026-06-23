#!/bin/bash
set -e
TARGET="$1"
if [ -z "$TARGET" ]; then
    echo "usage: ./deploy.sh user@their-ip"
    exit 1
fi
cd "$(dirname "$0")"
if [ ! -f locket-partner.tar.gz ]; then
    echo "locket-partner.tar.gz not found. Run python3 setup.py first."
    exit 1
fi
scp locket-partner.tar.gz "$TARGET":~/
ssh "$TARGET" 'tar xzf locket-partner.tar.gz && cd locket-partner && ./install.sh'
echo "deployed to $TARGET"
