#!/bin/bash
# Update Plus 每日备份脚本 - 北京时间凌晨4点执行
# 只执行备份，不尝试更新（避免 bun 缺失问题）

export PATH="/home/ubuntu/bin:/usr/local/bin:/usr/bin:/bin"

LOG_FILE="/home/ubuntu/.openclaw/backups/cron-backup.log"
BACKUP_DIR="/home/ubuntu/.openclaw/backups"

echo "=== Backup started $(date) ===" >> "$LOG_FILE"

# 运行 update-plus backup
/home/ubuntu/bin/update-plus backup >> "$LOG_FILE" 2>&1
BACKUP_STATUS=$?

if [ $BACKUP_STATUS -eq 0 ]; then
    echo "✓ Backup completed successfully at $(date)" >> "$LOG_FILE"
    # 发送 Healthchecks 成功信号
    curl -fsS -o /dev/null 'https://hc-ping.com/7971a6ce-4fb5-4d4a-80f8-efbc554f7d10'
else
    echo "✗ Backup failed at $(date)" >> "$LOG_FILE"
    # 发送 Healthchecks 失败信号
    curl -fsS -o /dev/null 'https://hc-ping.com/7971a6ce-4fb5-4d4a-80f8-efbc554f7d10/fail'
fi

echo "" >> "$LOG_FILE"
exit $BACKUP_STATUS
