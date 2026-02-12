#!/bin/bash

# 设置环境变量（这些应该通过更安全的方式配置）
export TZ='Asia/Shanghai'

# 获取昨天的日期
YESTERDAY=$(date -d "yesterday" +%Y-%m-%d)

# 邮箱地址（需要替换为实际地址）
RECIPIENT_EMAIL="your_email@example.com"

# 报告文件路径
REPORT_FILE="/home/ubuntu/clawd/workspace/documents/journal/${YESTERDAY}-daily-summary.md"
NEWS_REPORT_FILE="/home/ubuntu/clawd/workspace/documents/NewsReport/$(date +%Y-%m-%d)-improved-news-report.md"

# 检查日报文件是否存在
if [ -f "$REPORT_FILE" ]; then
    echo "Sending daily journal report via email..."
    python3 /home/ubuntu/clawd/send_report_via_email.py "$REPORT_FILE" "$RECIPIENT_EMAIL"
else
    echo "Journal report file not found: $REPORT_FILE"
fi

# 检查新闻报告文件是否存在
if [ -f "$NEWS_REPORT_FILE" ]; then
    echo "Sending daily news report via email..."
    python3 /home/ubuntu/clawd/send_report_via_email.py "$NEWS_REPORT_FILE" "$RECIPIENT_EMAIL"
else
    echo "News report file not found: $NEWS_REPORT_FILE"
fi

echo "Email sending process completed."