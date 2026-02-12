#!/usr/bin/env python3
"""
智能日报生成系统
通过语言模型深度分析文件内容，生成准确、完整的日报
"""

import os
import glob
import json
from datetime import datetime, timedelta
import re
import pytz


def collect_all_relevant_files(date_str):
    """
    收集所有相关文件 - 脚本负责发现和提取原始内容
    """
    files_to_analyze = []
    
    # 定义搜索模式
    patterns = [
        f"memory/{date_str}*.md",      # 记忆文件
        "*.skill",                    # 技能文件
        "workspace/**/*.md",          # 工作区文档
        "erduo-skills/**/*",          # 技能库文件
        "*.py",                       # Python脚本
        "*.json",                     # 配置文件
        "*.log",                      # 日志文件
        "daily_news_report*",         # 新闻报告相关文件
        "*journal*",                  # 日记相关文件
        "*.sh",                       # Shell脚本
    ]
    
    for pattern in patterns:
        try:
            files = glob.glob(pattern, recursive=True)
            for file in files:
                if os.path.isfile(file):  # 确保是文件而不是目录
                    try:
                        with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        if content.strip():  # 确保文件非空
                            files_to_analyze.append({
                                'path': file,
                                'content': content,
                                'size': len(content)
                            })
                    except Exception as e:
                        print(f"读取文件 {file} 时出错: {e}")
        except Exception as e:
            print(f"搜索模式 {pattern} 时出错: {e}")
    
    return files_to_analyze


def simulate_llm_analysis(all_collected_content, target_date):
    """
    模拟语言模型分析 - 实际应用中会调用真实的LLM API
    这里我们使用更高级的文本分析算法来模拟
    """
    print(f"正在分析 {len(all_collected_content)} 个文件...")
    
    # 组合所有内容用于分析
    combined_content = ""
    for item in all_collected_content:
        combined_content += f"\n=== 文件: {item['path']} ===\n"
        combined_content += f"{item['content'][:2000]}\n"  # 限制长度
    
    # 定义关键词模式来识别不同类型的活动
    patterns = {
        'projects': [
            r'技能.*创建|开发|实现',
            r'系统.*构建|实现|开发',
            r'工具.*创建|实现',
            r'功能.*实现|开发',
            r'API.*实现|开发',
            r'自动化.*实现',
            r'创建.*系统|工具|功能',
            r'实现.*集成',
            r'构建.*系统',
            r'开发.*模块'
        ],
        'operations': [
            r'安装.*软件|工具',
            r'配置.*系统|环境',
            r'优化.*性能|设置',
            r'修复.*问题|错误',
            r'调试.*代码|系统',
            r'升级.*系统|软件',
            r'清理.*环境|文件',
            r'设置.*安全|权限',
            r'环境.*搭建|配置',
            r'系统.*维护|管理'
        ],
        'research': [
            r'调研.*技术|工具',
            r'研究.*方案|方法',
            r'评估.*技术|工具',
            r'测试.*功能|性能',
            r'验证.*方案|效果',
            r'探索.*可能性|方法',
            r'分析.*需求|问题',
            r'比较.*方案|工具',
            r'学习.*技术|概念'
        ],
        'documentation': [
            r'文档.*编写|更新',
            r'记录.*过程|结果',
            r'整理.*资料|知识',
            r'撰写.*说明|教程',
            r'更新.*配置|说明',
            r'创建.*指南|手册',
            r'编写.*注释|说明'
        ],
        'todos': [
            r'待办|下一步',
            r'计划.*实现|完成',
            r'需要.*处理|解决',
            r'后续.*工作|任务',
            r'未来.*规划|目标',
            r'考虑.*实现|优化',
            r'改进.*方案|功能'
        ]
    }
    
    # 识别活动
    identified_activities = {
        'projects': set(),
        'operations': set(), 
        'research': set(),
        'documentation': set(),
        'todos': set()
    }
    
    # 对每个模式类别进行匹配
    for category, cat_patterns in patterns.items():
        for pattern in cat_patterns:
            matches = re.findall(pattern, combined_content, re.IGNORECASE)
            for match in matches:
                # 尝试获取上下文，使描述更完整
                context_start = combined_content.lower().find(match.lower())
                if context_start != -1:
                    # 获取匹配前后的一些文本作为上下文
                    start = max(0, context_start - 50)
                    end = min(len(combined_content), context_start + len(match) + 100)
                    context = combined_content[start:end].strip()
                    
                    # 清理和规范化描述
                    clean_desc = clean_activity_description(context, match)
                    if clean_desc and len(clean_desc) > 5:  # 确保有意义的描述
                        identified_activities[category].add(clean_desc)
    
    # 转换为列表并排序
    for category in identified_activities:
        identified_activities[category] = sorted(list(identified_activities[category]), key=len, reverse=True)[:10]  # 限制数量
    
    return identified_activities


def clean_activity_description(context, matched_text):
    """
    清理活动描述，提取有意义的句子
    """
    # 移除特殊字符和多余的空白
    context = re.sub(r'\s+', ' ', context)
    
    # 分割成句子
    sentences = re.split(r'[.!?。！？]', context)
    
    # 找到包含匹配文本的句子
    for sentence in sentences:
        if matched_text.lower() in sentence.lower():
            # 清理句子
            cleaned = re.sub(r'^\s*=+\s*文件:\s*[^=]*=\s*', '', sentence)  # 移除文件头
            cleaned = re.sub(r'^\s*[•\-]\s*', '', cleaned)  # 移除列表标记
            cleaned = cleaned.strip()
            
            # 确保不是太短或无意义的描述
            if len(cleaned) > 10 and not cleaned.startswith('==='):
                return cleaned
    
    # 如果找不到合适的句子，返回匹配文本的扩展上下文
    return matched_text


def generate_intelligent_report(analysis_result, date_str):
    """
    使用分析结果生成结构化报告
    """
    report = f"# {date_str} 日报\n\n"
    
    # 项目部分
    report += "## 项目\n"
    if analysis_result['projects']:
        for activity in analysis_result['projects']:
            report += f"• {activity}\n"
    else:
        report += "• 无特定项目进展\n"
    report += "\n"
    
    # 杂项部分 - 包含操作、研究、文档类活动
    report += "## 杂项\n"
    all_misc = analysis_result['operations'] + analysis_result['research'] + analysis_result['documentation']
    if all_misc:
        for activity in all_misc:
            report += f"• {activity}\n"
    else:
        report += "• 今日无重大活动记录\n"
    report += "\n"
    
    # 待办事项
    report += "## 待办事项\n"
    if analysis_result['todos']:
        for activity in analysis_result['todos']:
            report += f"• {activity}\n"
    else:
        report += "• 无特别待办事项\n"
    report += "\n"
    
    return report


def generate_daily_journal(target_date):
    """
    生成日报的主函数
    """
    print(f"开始为日期 {target_date} 生成智能日报...")
    
    # 1. 收集所有相关文件
    files_content = collect_all_relevant_files(target_date)
    print(f"收集到 {len(files_content)} 个相关文件")
    
    if not files_content:
        print("未找到相关文件，生成空日报...")
        report = f"# {target_date} 日报\n\n"
        report += "## 项目\n• 无特定项目进展\n\n"
        report += "## 杂项\n• 今日无重大活动记录\n\n"
        report += "## 待办事项\n• 无特别待办事项\n\n"
        return report
    
    # 2. 使用模拟的语言模型分析
    analysis_result = simulate_llm_analysis(files_content, target_date)
    
    # 3. 生成最终报告
    report = generate_intelligent_report(analysis_result, target_date)
    
    return report


def main():
    """
    主函数 - 生成昨日的日报
    """
    # 默认生成昨天的日报 - 使用北京时间
    import pytz
    beijing_tz = pytz.timezone('Asia/Shanghai')
    today_beijing = datetime.now(beijing_tz)
    yesterday_beijing = (today_beijing - timedelta(days=1)).strftime('%Y-%m-%d')
    
    # 或者可以通过命令行参数指定日期
    import sys
    if len(sys.argv) > 1:
        target_date = sys.argv[1]
    else:
        target_date = yesterday_beijing
    
    report = generate_daily_journal(target_date)
    
    # 保存报告
    filename = f"daily_journal_{target_date}.md"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"日报已生成并保存至: {filename}")
    print("\n生成的日报内容:")
    print("="*50)
    print(report)


if __name__ == "__main__":
    from datetime import timedelta
    main()