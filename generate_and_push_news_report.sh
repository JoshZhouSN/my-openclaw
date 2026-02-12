#!/bin/bash
# 每日新闻报告生成和推送脚本

cd /home/ubuntu/clawd

# 运行erduo-skills中的改进版新闻报告生成器
cd /home/ubuntu/clawd/erduo-skills
python3 improved_daily_news_report.py

# 读取生成的报告内容并发送到Telegram
cd /home/ubuntu/clawd
REPORT_PATH="/home/ubuntu/clawd/erduo-skills/NewsReport/$(date +%Y-%m-%d)-improved-news-report.md"

if [ -f "$REPORT_PATH" ]; then
    echo "找到报告文件，正在发送到Telegram..."
    
    # 读取报告内容
    REPORT_CONTENT=$(cat "$REPORT_PATH")
    
    # 将报告内容分段发送到Telegram
    # 由于报告可能很长，我们需要分段发送
    echo "$REPORT_CONTENT" | split -C 3000 - /tmp/news_report_part_
    
    for part_file in /tmp/news_report_part_*; do
        if [ -f "$part_file" ]; then
            PART_CONTENT=$(cat "$part_file")
            # 使用moltbot的message工具发送到Telegram
            moltbot message send --channel telegram --target telegram:1926016086 --message "$PART_CONTENT"
            rm "$part_file"  # 删除临时文件
            sleep 2  # 稍作延迟避免发送过快
        fi
    done
    
    echo "新闻报告已发送到Telegram"
else
    echo "未找到报告文件: $REPORT_PATH"
fi