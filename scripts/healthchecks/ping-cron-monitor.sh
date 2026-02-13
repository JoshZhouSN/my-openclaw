#!/bin/bash
# Ping Healthchecks.io when critical cron jobs complete successfully
# This script should be called at the end of critical cron jobs

PING_URL="https://hc-ping.com/7971a6ce-4fb5-4d4a-80f8-efbc554f7d10"
JOB_NAME="${1:-cron-job}"

curl -fsS -o /dev/null "$PING_URL"
echo "$(date): Cron job '$JOB_NAME' completed, ping sent to Healthchecks.io"
