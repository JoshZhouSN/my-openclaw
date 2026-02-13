#!/usr/bin/env python3
"""
通过电子邮件发送日报和新闻报告
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from datetime import datetime, timedelta
import sys
import json

def send_report_email(subject, body, recipient_email, smtp_config=None):
    """
    发送报告邮件
    """
    # 从环境变量或配置文件获取SMTP配置
    if not smtp_config:
        smtp_config = {
            'server': os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com'),
            'port': int(os.getenv('EMAIL_SMTP_PORT', 587)),
            'username': os.getenv('EMAIL_USERNAME'),
            'password': os.getenv('EMAIL_PASSWORD'),
            'sender': os.getenv('EMAIL_SENDER')
        }
    
    # 检查必要参数
    if not all([smtp_config['username'], smtp_config['password'], smtp_config['sender']]):
        print("错误：缺少必要的邮件配置信息。请设置以下环境变量：")
        print("- EMAIL_SMTP_SERVER: SMTP服务器地址")
        print("- EMAIL_SMTP_PORT: SMTP端口")
        print("- EMAIL_USERNAME: 邮箱用户名")
        print("- EMAIL_PASSWORD: 邮箱密码或应用专用密码")
        print("- EMAIL_SENDER: 发送者邮箱地址")
        return False
    
    try:
        # 创建邮件对象
        msg = MIMEMultipart()
        msg['From'] = Header(smtp_config['sender'])
        msg['To'] = Header(recipient_email)
        msg['Subject'] = Header(subject, 'utf-8')
        
        # 添加邮件正文
        msg.attach(MIMEText(body, 'html', 'utf-8'))
        
        # 连接SMTP服务器并发送邮件
        server = smtplib.SMTP(smtp_config['server'], smtp_config['port'])
        server.starttls()  # 启用加密传输
        server.login(smtp_config['username'], smtp_config['password'])
        
        text = msg.as_string()
        server.sendmail(smtp_config['sender'], recipient_email, text)
        server.quit()
        
        print(f"邮件已成功发送到 {recipient_email}")
        return True
        
    except Exception as e:
        print(f"发送邮件失败: {str(e)}")
        return False

def read_report_file(report_path):
    """
    读取报告文件内容
    """
    try:
        with open(report_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"无法读取报告文件 {report_path}: {str(e)}")
        return None

def main():
    # 获取命令行参数
    if len(sys.argv) < 3:
        print("用法: python send_report_via_email.py <report_file_path> <recipient_email>")
        sys.exit(1)
    
    report_path = sys.argv[1]
    recipient_email = sys.argv[2]
    
    # 获取报告类型（从文件名判断）
    if 'news' in report_path.lower():
        report_type = "新闻报告"
    elif 'journal' in report_path.lower() or 'daily' in report_path.lower():
        report_type = "日报"
    else:
        report_type = "报告"
    
    # 读取报告内容
    report_content = read_report_file(report_path)
    if not report_content:
        print(f"无法读取报告文件: {report_path}")
        sys.exit(1)
    
    # 准备邮件主题和内容
    date_str = datetime.now().strftime('%Y-%m-%d')
    subject = f"{report_type} - {date_str}"
    
    # 将报告内容转换为HTML格式
    html_body = f"""
    <html>
    <head>
        <meta charset="UTF-8">
    </head>
    <body>
        <h2>{subject}</h2>
        <div style="font-family: monospace; white-space: pre-wrap; font-size: 14px;">
        {report_content.replace('<', '&lt;').replace('>', '&gt;').replace('\\n', '<br>')}
        </div>
        <hr>
        <p><small>此邮件由自动报告系统发送</small></p>
    </body>
    </html>
    """
    
    # 发送邮件
    success = send_report_email(subject, html_body, recipient_email)
    
    if success:
        print("邮件发送成功！")
        sys.exit(0)
    else:
        print("邮件发送失败！")
        sys.exit(1)

if __name__ == "__main__":
    main()