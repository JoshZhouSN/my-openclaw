# OpenClaw 灾难恢复手册

> 目标：从零开始，2 小时内完全恢复所有功能
> 适用范围：Ubuntu 22.04+ / Debian 系统
> 最后更新：2026-02-12
> 由 Big-J 维护

---

## 📋 恢复前准备

### 需要准备的信息

在开始恢复前，确保你有以下信息：

| 信息 | 来源 | 用途 |
|------|------|------|
| **NVIDIA API Key** | https://build.nvidia.com/ | Kimi 模型访问 |
| **Telegram Bot Token** | @BotFather | Telegram 消息推送 |
| **Gmail App Password** | Google 账户设置 | 邮件发送/接收 |
| **GitHub 仓库访问** | SSH Key 或 Token | 代码拉取 |
| **Healthchecks.io URL** | 本手册下方 | 监控检查点 |

---

## 🚀 第一阶段：基础环境（30 分钟）

### 1.1 系统更新

```bash
sudo apt update && sudo apt upgrade -y
```

### 1.2 安装基础依赖

```bash
# 安装基础工具
sudo apt install -y git curl wget vim jq rsync tar gzip

# 安装邮件工具
sudo apt install -y msmtp msmtp-mta mbsync ripmime mailutils

# 安装 Python 和 pip
sudo apt install -y python3 python3-pip python3-venv

# 安装 Node.js (v20+)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# 验证安装
node --version  # 应 >= v20.0.0
npm --version   # 应 >= 10.0.0
python3 --version  # 应 >= 3.10
```

### 1.3 安装 Chrome 浏览器（用于 Playwright）

```bash
# 下载并安装 Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install -y ./google-chrome-stable_current_amd64.deb
rm google-chrome-stable_current_amd64.deb

# 验证
google-chrome --version
```

### 1.4 安装 Playwright

```bash
pip3 install playwright beautifulsoup4 requests
python3 -m playwright install chromium

# 验证
playwright --version
```

---

## 🏗️ 第二阶段：OpenClaw 安装（20 分钟）

### 2.1 安装 OpenClaw

```bash
# 使用官方安装脚本
curl -sSL https://install.openclaw.ai | bash

# 或者使用 npm
npm install -g openclaw

# 验证安装
openclaw --version
```

### 2.2 克隆仓库

```bash
# 创建工作目录
mkdir -p ~/clawd
cd ~/clawd

# 克隆仓库（需要 GitHub 认证）
git clone https://github.com/JoshZhouSN/my-openclaw.git .

# 或者使用 SSH
git clone git@github.com:JoshZhouSN/my-openclaw.git .
```

### 2.3 恢复 OpenClaw 配置

```bash
# 创建配置目录
mkdir -p ~/.openclaw

# 复制基础配置
cp ~/clawd/openclaw-config/config.json ~/.openclaw/
cp ~/clawd/openclaw-config/openclaw.json.template ~/.openclaw/openclaw.json

# 设置权限
chmod 600 ~/.openclaw/openclaw.json
```

---

## 🔑 第三阶段：API Keys 配置（20 分钟）

### 3.1 编辑主配置文件

```bash
nano ~/.openclaw/openclaw.json
```

### 3.2 必须填入的 API Keys

#### 3.2.1 NVIDIA API Key（用于 Kimi 模型）

**获取方式：**
1. 访问 https://build.nvidia.com/
2. 注册/登录账号
3. 创建 API Key

**填入位置：**
```json
{
  "models": {
    "providers": {
      "nvidia": {
        "apiKey": "nvapi-YOUR_KEY_HERE"
      }
    }
  }
}
```

#### 3.2.2 Telegram Bot Token

**获取方式：**
1. 在 Telegram 中搜索 @BotFather
2. 发送 `/newbot` 创建新机器人
3. 复制提供的 Token

**填入位置：**
```json
{
  "channels": {
    "telegram": {
      "botToken": "YOUR_BOT_TOKEN_HERE"
    }
  }
}
```

#### 3.2.3 Gateway Token（可选，会自动生成）

如果不填，首次启动时会自动生成。

**填入位置：**
```json
{
  "gateway": {
    "auth": {
      "token": "YOUR_TOKEN_HERE"
    }
  }
}
```

### 3.3 配置邮件工具

```bash
# 创建配置目录
mkdir -p ~/.config/email-tool

# 创建配置文件
cat > ~/.config/email-tool/config.env << 'EOF'
EMAIL_USER=zhou.zhengchao1@gmail.com
EMAIL_PASS="YOUR_GMAIL_APP_PASSWORD"
EOF

chmod 600 ~/.config/email-tool/config.env
```

**获取 Gmail App Password：**
1. 访问 https://myaccount.google.com/security
2. 启用 2-Step Verification（必须）
3. 进入 "App passwords"
4. 选择 "Mail" 和设备类型
5. 复制 16 位密码

---

## 🤖 第四阶段：启动和配对（15 分钟）

### 4.1 首次启动 OpenClaw

```bash
# 启动 Gateway
openclaw gateway start

# 检查状态
openclaw gateway status
```

### 4.2 配对 Telegram

```bash
# 查看配对二维码
openclaw pairing telegram

# 或者使用命令行
openclaw message send --channel telegram --target "YOUR_USER_ID" --message "Hello from Big-J!"
```

### 4.3 允许特定用户

编辑 `~/.openclaw/credentials/telegram-allowFrom.json`：

```json
{
  "version": 1,
  "allowFrom": [
    "1926016086"
  ]
}
```

> 将 `1926016086` 替换为你的 Telegram User ID

---

## 📊 第五阶段：Cron Jobs 恢复（10 分钟）

### 5.1 设置时区

```bash
# 设置为上海时区（用于新闻报告）
sudo timedatectl set-timezone Asia/Shanghai
```

### 5.2 配置 Cron Jobs

```bash
# 编辑 crontab
crontab -e
```

添加以下内容：

```cron
# Healthchecks.io - openclaw-heartbeat monitor
*/5 * * * * curl -fsS -o /dev/null 'https://hc-ping.com/377fe462-b99f-4f93-b33e-65870c4c4ba1'

# Healthchecks.io - openclaw-process monitor (check every 5 min)
*/5 * * * * /home/ubuntu/clawd/scripts/healthchecks/check-openclaw-process.sh

# News report generation - with Healthchecks ping on success
0 0 * * * TZ=Asia/Shanghai /home/ubuntu/clawd/generate_and_push_news_report.sh && /home/ubuntu/clawd/scripts/healthchecks/ping-cron-monitor.sh "news-report"
```

### 5.3 验证 Cron Jobs

```bash
crontab -l
```

---

## 🔍 第六阶段：健康检查配置（10 分钟）

### 6.1 Healthchecks.io 监控点

| 检查项 | URL | 用途 |
|--------|-----|------|
| openclaw-heartbeat | https://hc-ping.com/377fe462-b99f-4f93-b33e-65870c4c4ba1 | 基础心跳 |
| openclaw-process | https://hc-ping.com/ac39ce97-859e-4577-9c7a-7f48b04114b8 | 进程监控 |
| openclaw-cron-jobs | https://hc-ping.com/7971a6ce-4fb5-4d4a-80f8-efbc554f7d10 | Cron 执行监控 |

### 6.2 手动测试监控

```bash
# 测试心跳
curl -fsS -o /dev/null 'https://hc-ping.com/377fe462-b99f-4f93-b33e-65870c4c4ba1'

# 测试进程监控脚本
/home/ubuntu/clawd/scripts/healthchecks/check-openclaw-process.sh
```

---

## 📦 第七阶段：Skills 安装（15 分钟）

### 7.1 通过 ClawHub 安装 Skills

```bash
# 进入技能目录
cd ~/clawd

# 使用 clawhub 安装（如果有 lock.json）
clawhub install

# 或者手动链接已克隆的 skills
ln -sf ~/clawd/skills/agent-browser ~/.openclaw/skills/
ln -sf ~/clawd/skills/email-tool ~/.openclaw/skills/
ln -sf ~/clawd/skills/tavily-search ~/.openclaw/skills/
# ... 其他 skills
```

### 7.2 验证 Skills

```bash
# 列出已安装的技能
ls -la ~/.openclaw/skills/

# 测试 skill 功能
openclaw skill list
```

---

## ✅ 第八阶段：验证和测试（15 分钟）

### 8.1 功能检查清单

- [ ] OpenClaw Gateway 运行正常
- [ ] Telegram 消息可以发送/接收
- [ ] 邮件可以发送/接收
- [ ] Web 搜索功能正常
- [ ] 浏览器自动化功能正常
- [ ] 新闻报告生成正常
- [ ] Healthchecks 收到心跳
- [ ] Cron jobs 执行正常

### 8.2 测试命令

```bash
# 1. 测试 Gateway
openclaw gateway status

# 2. 测试 Telegram
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/sendMessage" \
  -d "chat_id=1926016086" \
  -d "text=Test message from Big-J"

# 3. 测试邮件
echo "Test body" | mail -s "Test Subject" zhou.zhengchao1@gmail.com

# 4. 测试 Tavily 搜索
cd ~/clawd && python3 tavily_search_test.py

# 5. 测试浏览器
cd ~/clawd && python3 test_browser_service.py
```

---

## 🆘 第九阶段：备份恢复（如果适用）

### 9.1 使用 Update-Plus 备份

如果你有之前的备份文件：

```bash
# 列出可用备份
bash ~/clawd/skills/update-plus/bin/update-plus list-backups

# 恢复特定备份
bash ~/clawd/skills/update-plus/bin/update-plus restore openclaw-backup-YYYY-MM-DD-HH:MM:SS.tar.gz
```

### 9.2 手动解压备份

```bash
# 解压到临时目录
tar -xzf openclaw-backup-YYYY-MM-DD-HH:MM:SS.tar.gz -C /tmp/restore

# 恢复配置
cp -r /tmp/restore/config/* ~/.openclaw/
cp -r /tmp/restore/workspace/* ~/clawd/
```

---

## 🔧 故障排除

### 问题 1: OpenClaw 启动失败

**症状：** `openclaw gateway start` 无响应

**解决：**
```bash
# 检查日志
tail -f ~/.openclaw/logs/gateway.log

# 检查端口占用
sudo lsof -i :18789

# 清理并重启
pkill -f openclaw
openclaw gateway start
```

### 问题 2: Telegram 消息发送失败

**症状：** 消息无法发送到 Telegram

**解决：**
```bash
# 1. 检查 Bot Token 是否正确
# 2. 检查是否已发送 /start 给 Bot
# 3. 检查 allowFrom 配置
cat ~/.openclaw/credentials/telegram-allowFrom.json

# 4. 测试 API
curl "https://api.telegram.org/bot<TOKEN>/getMe"
```

### 问题 3: Playwright 浏览器启动失败

**症状：** 浏览器自动化报错

**解决：**
```bash
# 重新安装浏览器
python3 -m playwright install chromium

# 检查 Chrome 路径
which google-chrome

# 验证安装
python3 -c "from playwright.sync_api import sync_playwright; print('OK')"
```

### 问题 4: 邮件发送失败

**症状：** 邮件无法发送

**解决：**
```bash
# 检查配置
cat ~/.config/email-tool/config.env

# 测试 SMTP
msmtp -S zhou.zhengchao1@gmail.com < /dev/null

# 检查 App Password 是否正确
# 注意：需要 2-Step Verification 才能使用 App Password
```

---

## 📞 联系信息

- **维护者：** Big-J
- **邮箱：** zhou.zhengchao1@gmail.com
- **GitHub：** https://github.com/JoshZhouSN/my-openclaw

---

## 📝 更新记录

| 日期 | 更新内容 |
|------|----------|
| 2026-02-12 | 初始版本，基于当前系统配置 |

---

**提醒：** 定期更新此手册，特别是 API Keys 变更时！
