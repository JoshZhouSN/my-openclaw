#!/usr/bin/env python3
"""
简化的日报生成系统
专注于从记忆文件中提取关键活动
"""

import os
import glob
from datetime import datetime, timedelta
import pytz


def extract_key_activities_from_memory_files(date_str):
    """
    从记忆文件中提取关键活动
    """
    # 查找指定日期的记忆文件
    memory_files = glob.glob(f"memory/{date_str}*.md")
    
    all_activities = {
        'projects': set(),
        'operations': set(), 
        'research': set(),
        'documentation': set(),
        'todos': set()
    }
    
    for file_path in memory_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 分割内容为行，便于处理
            lines = content.split('\n')
            
            for line in lines:
                line_lower = line.lower().strip()
                
                # 识别项目类活动
                if any(keyword in line_lower for keyword in ['创建', '开发', '实现', '构建', '技能', '系统', '工具', '功能']):
                    if len(line) > 20:  # 确保有足够的描述信息
                        # 提取有意义的部分
                        activity = clean_line(line)
                        if activity:
                            all_activities['projects'].add(activity)
                
                # 识别操作类活动
                elif any(keyword in line_lower for keyword in ['安装', '配置', '优化', '修复', '调试', '升级', '清理', '设置', '环境']):
                    if len(line) > 20:
                        activity = clean_line(line)
                        if activity:
                            all_activities['operations'].add(activity)
                
                # 识别研究类活动
                elif any(keyword in line_lower for keyword in ['调研', '研究', '评估', '测试', '验证', '探索', '分析', '比较', '学习']):
                    if len(line) > 20:
                        activity = clean_line(line)
                        if activity:
                            all_activities['research'].add(activity)
                
                # 识别文档类活动
                elif any(keyword in line_lower for keyword in ['文档', '记录', '整理', '撰写', '更新', '编写', '注释']):
                    if len(line) > 20:
                        activity = clean_line(line)
                        if activity:
                            all_activities['documentation'].add(activity)
                
                # 识别待办事项
                elif any(keyword in line_lower for keyword in ['待办', '计划', '需要', '后续', '未来', '考虑', '改进', '下一步']):
                    if len(line) > 20:
                        activity = clean_line(line)
                        if activity:
                            all_activities['todos'].add(activity)
        
        except Exception as e:
            print(f"处理文件 {file_path} 时出错: {e}")
    
    # 转换为排序后的列表
    for key in all_activities:
        all_activities[key] = sorted(list(all_activities[key]), key=len, reverse=True)
    
    return all_activities


def clean_line(line):
    """
    清理行内容，移除不必要的部分
    """
    # 移除常见的非活动描述内容
    if any(skip in line for skip in ['user:', 'assistant:', 'message_id', 'Session:', '##', '[', ']']):
        return None
    
    # 清理并返回有意义的描述
    cleaned = line.replace('\\n', ' ').replace('\\t', ' ').replace('  ', ' ').strip()
    cleaned = cleaned.replace('#', '').replace('*', '•').strip()
    
    # 确保不是太短的描述
    if len(cleaned) > 15:
        return cleaned
    
    return None


def generate_simple_report(activities, date_str):
    """
    生成简单的日报报告
    """
    report = f"# {date_str} 日报\n\n"
    
    # 项目部分
    report += "## 项目\n"
    if activities['projects']:
        for activity in activities['projects']:
            report += f"• {activity}\n"
    else:
        report += "• 无特定项目进展\n"
    report += "\n"
    
    # 杂项部分（操作、研究、文档）
    report += "## 杂项\n"
    all_misc = activities['operations'] + activities['research'] + activities['documentation']
    if all_misc:
        for activity in all_misc:
            report += f"• {activity}\n"
    else:
        report += "• 今日无重大活动记录\n"
    report += "\n"
    
    # 待办事项
    report += "## 待办事项\n"
    if activities['todos']:
        for activity in activities['todos']:
            report += f"• {activity}\n"
    else:
        report += "• 无特别待办事项\n"
    report += "\n"
    
    return report


def main():
    """
    主函数
    """
    import sys
    import pytz
    if len(sys.argv) > 1:
        target_date = sys.argv[1]
    else:
        # 默认处理昨天的日期 - 使用北京时间
        from datetime import timedelta
        beijing_tz = pytz.timezone('Asia/Shanghai')
        today_beijing = datetime.now(beijing_tz)
        target_date = (today_beijing - timedelta(days=1)).strftime('%Y-%m-%d')
    
    print(f"正在为日期 {target_date} 生成日报...")
    
    # 提取关键活动
    activities = extract_key_activities_from_memory_files(target_date)
    
    # 生成报告
    report = generate_simple_report(activities, target_date)
    
    # 保存报告
    filename = f"daily_journal_summary_{target_date}.md"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"日报已生成并保存至: {filename}")
    print("\n生成的日报内容:")
    print("="*50)
    print(report)


if __name__ == "__main__":
    main()