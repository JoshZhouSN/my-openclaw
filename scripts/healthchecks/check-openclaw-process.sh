#!/bin/bash
# Monitor OpenClaw process and ping Healthchecks.io

PING_URL="https://hc-ping.com/ac39ce97-859e-4577-9c7a-7f48b04114b8"

# Check if openclaw gateway is running (look for the node process)
if pgrep -f "openclaw.*gateway" > /dev/null 2>&1 || pgrep -f "node.*openclaw" > /dev/null 2>&1 || pgrep -f "clawd" > /dev/null 2>&1; then
    # Process is running, send success ping
    curl -fsS -o /dev/null "$PING_URL"
    echo "$(date): OpenClaw process is running, ping sent"
else
    # Process is not running, send failure signal
    curl -fsS -o /dev/null "$PING_URL/fail"
    echo "$(date): WARNING: OpenClaw process not found, failure signal sent"
fi
