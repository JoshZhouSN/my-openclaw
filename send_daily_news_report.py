#!/usr/bin/env python3
"""
Daily News Report 自动推送脚本
每天早上8点自动生成新闻报告并通过Telegram推送
"""

import os
import sys
from datetime import datetime
import subprocess
import shutil


def generate_news_report():
    """生成新闻报告"""
    print("开始生成新闻报告...")
    
    # 切换到erduo-skills目录
    os.chdir("/home/ubuntu/clawd/erduo-skills")
    
    # 清除缓存
    cache_file = "skills/daily-news-report/cache.json"
    if os.path.exists(cache_file):
        with open(cache_file, 'w', encoding='utf-8') as f:
            f.write('''{
  "schema_version": "1.0",
  "description": "Daily News Report 缓存文件，用于避免重复抓取和跟踪历史表现",

  "last_run": {},

  "source_stats": {
    "_comment": "记录每个源的历史表现，用于动态调整优先级",
    "hn": {
      "total_fetches": 0,
      "success_count": 0,
      "avg_items_per_fetch": 0,
      "avg_quality_score": 0,
      "last_fetch": null,
      "last_success": null
    }
  },

  "url_cache": {
    "_comment": "已处理的 URL 缓存，避免重复收录",
    "_ttl_hours": 168,
    "entries": {}
  },

  "content_hashes": {
    "_comment": "内容指纹，用于去重",
    "_ttl_hours": 168,
    "entries": {}
  },

  "article_history": {
    "_comment": "已收录文章的简要记录",
    "2026-01-21": []
  }
}''')
    
    # 运行改进版的新闻报告生成器
    result = subprocess.run([
        sys.executable, "improved_daily_news_report.py"
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"生成报告时出错: {result.stderr}")
        return None
    
    print("报告生成完成")
    
    # 找到生成的报告文件
    today = datetime.now().strftime('%Y-%m-%d')
    report_filename = f"NewsReport/{today}-improved-news-report.md"
    
    if not os.path.exists(report_filename):
        print(f"未找到报告文件: {report_filename}")
        return None
    
    return report_filename


def move_report_to_documents(report_path):
    """将报告移动到documents/NewsReport目录"""
    destination_dir = "/home/ubuntu/clawd/workspace/documents/NewsReport"
    destination_path = os.path.join(destination_dir, os.path.basename(report_path))
    
    os.makedirs(destination_dir, exist_ok=True)
    shutil.copy(report_path, destination_path)
    print(f"报告已复制到: {destination_path}")
    
    return destination_path


def main():
    """主函数"""
    print(f"开始执行每日新闻报告推送任务 - {datetime.now()}")
    
    # 生成报告
    report_path = generate_news_report()
    if not report_path:
        print("未能生成报告，任务终止")
        return
    
    # 移动报告到文档目录
    doc_path = move_report_to_documents(report_path)
    print(f"报告已存储到: {doc_path}")
    
    # 读取报告内容
    with open(doc_path, 'r', encoding='utf-8') as f:
        report_content = f.read()
    
    # 发送到Telegram - 分段发送以避免长度限制
    import subprocess
    import json
    
    # 将报告内容分割成适合Telegram的消息块
    chunks = []
    lines = report_content.split('\n')
    current_chunk = ""
    
    for line in lines:
        if len(current_chunk + line + '\n') < 3000:  # 留出余量
            current_chunk += line + '\n'
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = line + '\n'
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    # 使用subprocess调用Moltbot的message命令发送消息块
    for i, chunk in enumerate(chunks):
        if chunk:  # 只发送非空块
            # 添加进度信息
            if len(chunks) > 1:
                chunk_with_progress = f"[{i+1}/{len(chunks)}]\n{chunk}"
            else:
                chunk_with_progress = chunk
            
            # 构建message命令
            message_cmd = [
                'moltbot', 'message', 'send',
                '--channel', 'telegram',
                '--target', 'telegram:1926016086',  # Telegram chat ID
                '--message', chunk_with_progress
            ]
            
            try:
                result = subprocess.run(message_cmd, capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    print(f"已发送第{i+1}部分到Telegram")
                else:
                    print(f"发送第{i+1}部分失败: {result.stderr}")
            except subprocess.TimeoutExpired:
                print(f"发送第{i+1}部分超时")
            except Exception as e:
                print(f"发送第{i+1}部分时发生异常: {str(e)}")
            
            # 短暂延迟避免发送过快
            import time
            time.sleep(2)
    
    print(f"新闻报告已尝试分{len(chunks)}部分推送到Telegram")


if __name__ == "__main__":
    main()