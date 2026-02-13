# OpenClaw 灾难恢复手册

> 目标：从零开始，2 小时内完全恢复所有功能
> 适用范围：Ubuntu 22.04+ / Debian 系统
> 最后更新：2026-02-13
> 架构版本：OpenClaw 标准架构 v2.0
> 由 Big-J 维护

---

## 📋 恢复前准备

### ⚡ 快速恢复 vs 完整恢复

#### 方式一：Update Plus 备份恢复（推荐，30分钟）

如果你有 Update Plus 备份文件，**可以跳过大部分 API Key 配置**！

Update Plus 备份包含：
- ✅ `~/.openclaw/openclaw.json` - 包含所有 API Keys 和配置
- ✅ `~/.openclaw/credentials/` - 敏感凭证（OAuth tokens）
- ✅ `~/.openclaw/config.json` - 主配置
- ✅ `~/.openclaw/workspace/` - 工作区完整数据

**需要准备：**
| 信息 | 来源 | 用途 |
|------|------|------|
| **Update Plus 备份文件** | `~/.openclaw/backups/` | 恢复所有配置和数据 |
| **GitHub 仓库访问** | SSH Key 或 Token | 拉取最新代码 |
| **Telegram Bot Token** | @BotFather | 重新配对（Token 会变）|

#### 方式二：从零完整配置（2小时）

如果没有备份，需要准备：

| 信息 | 来源 | 用途 |
|------|------|------|
| **NVIDIA API Key** | https://build.nvidia.com/ | Kimi 模型访问 |
| **Qwen Portal OAuth** | https://portal.qwen.ai/ | Qwen Coder/Vision 模型 |
| **Telegram Bot Token** | @BotFather | Telegram 消息推送 |
| **Gmail App Password** | Google 账户设置 | 邮件发送/接收 |
| **GitHub 仓库访问** | SSH Key 或 Token | 代码拉取 |
| **Healthchecks.io URL** | 本手册下方 | 监控检查点 |

### 架构说明（重要！）

本手册基于 **OpenClaw 标准架构**：

```
~/.openclaw/                    ← OpenClaw 根目录
├── workspace/                  ← 实际工作区（Git管理）✅
│   ├── AGENTS.md, SOUL.md...  ← 核心配置文档
│   ├── memory/                 ← 记忆日志
│   ├── skills/                 ← 用户技能（15个）
│   ├── documents/              ← 文档
│   ├── projects/               ← 项目
│   ├── scripts/                ← 脚本
│   └── .git/                   ← Git仓库
│
├── config.json                 ← OpenClaw主配置
├── openclaw.json              ← 运行时状态
├── update-plus.json           ← Update Plus配置
├── backups/                   ← 备份文件
└── ...运行时数据

~/clawd -> ~/.openclaw/workspace  ← 向后兼容软链接
```

**关键变化（2026-02-13 迁移后）：**
- 工作区从 `~/clawd/` 迁移到 `~/.openclaw/workspace/`
- `~/clawd` 现在是软链接，指向 `~/.openclaw/workspace/`
- Skills 现在在 `~/.openclaw/workspace/skills/`（原来是 `~/.openclaw/skills/`）

---

## ⚡ 快速恢复：Update Plus 备份（30分钟）

如果你有 Update Plus 备份文件，这是最快速的恢复方式。

### 前提条件

- Update Plus 备份文件（`openclaw-backup-YYYY-MM-DD-HHMMSS.tar.gz`）
- 系统已安装基础依赖（Node.js, Python, git, jq）

### 快速恢复步骤

```bash
# 1. 创建目录结构
mkdir -p ~/.openclaw
mkdir -p ~/bin

# 2. 解压备份
tar -xzf openclaw-backup-YYYY-MM-DD-HHMMSS.tar.gz -C /tmp/restore

# 3. 恢复 OpenClaw 配置
cp -r /tmp/restore/config/* ~/.openclaw/

# 4. 恢复工作区
mkdir -p ~/.openclaw/workspace
cp -r /tmp/restore/workspace/* ~/.openclaw/workspace/

# 5. 创建向后兼容软链接
ln -s ~/.openclaw/workspace ~/clawd

# 6. 创建 update-plus 软链接
ln -s ~/.openclaw/workspace/skills/update-plus/bin/update-plus ~/bin/update-plus

# 7. 安装 OpenClaw（如果未安装）
npm install -g openclaw

# 8. 重新配对 Telegram（Token 可能已过期）
openclaw pairing telegram

# 9. 启动 Gateway
openclaw gateway start
```

### 备份中包含的敏感信息

✅ **会自动恢复（无需重新配置）：**
- `openclaw.json` - 所有 API Keys（NVIDIA, Qwen, etc.）
- `credentials/` - OAuth tokens, Telegram session
- `config.json` - 代理配置
- `workspace/` - 所有代码、记忆、技能

⚠️ **需要重新配置：**
- Telegram Bot Token（可能过期，需要 @BotFather 重新获取）
- 部分 OAuth 授权可能需要重新登录

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

# 安装 Node.js (v22+)
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt install -y nodejs

# 验证安装
node --version  # 应 >= v22.0.0
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

## 🏗️ 第二阶段：OpenClaw 安装和配置（25 分钟）

### 2.1 安装 OpenClaw

```bash
# 使用官方安装脚本
curl -sSL https://install.openclaw.ai | bash

# 或者使用 npm
npm install -g openclaw

# 验证安装
openclaw --version
```

### 2.2 创建目录结构（标准架构）

```bash
# 创建 OpenClaw 配置目录
mkdir -p ~/.openclaw

# 创建工作区目录（标准位置）
mkdir -p ~/.openclaw/workspace

# 创建向后兼容的软链接
ln -s ~/.openclaw/workspace ~/clawd
```

### 2.3 克隆仓库到标准位置

```bash
# 进入工作区
cd ~/.openclaw/workspace

# 克隆仓库（需要 GitHub 认证）
git clone https://github.com/JoshZhouSN/my-openclaw.git .

# 或者使用 SSH
git clone git@github.com:JoshZhouSN/my-openclaw.git .
```

### 2.4 恢复 OpenClaw 配置

```bash
# 复制基础配置到 ~/.openclaw/
cp ~/.openclaw/workspace/openclaw-config/config.json ~/.openclaw/

# 或者手动创建最小配置
cat > ~/.openclaw/config.json << 'EOF'
{
  "agents": {
    "defaults": {
      "workspace": "/home/ubuntu/.openclaw/workspace",
      "model": "nvidia/moonshotai/kimi-k2.5",
      "subagents": {
        "archiveAfterMinutes": 60
      }
    }
  }
}
EOF
```

**⚠️ 重要：** 确保 `config.json` 中的 `workspace` 指向 `/home/ubuntu/.openclaw/workspace`（新标准位置）

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

#### 3.2.2 Qwen Portal OAuth（用于 Qwen Coder/Vision）

**获取方式：**
1. 访问 https://portal.qwen.ai/
2. 使用 GitHub 账号登录
3. 在设置中查看或刷新 OAuth Token

**填入位置：**
```json
{
  "models": {
    "providers": {
      "qwen-portal": {
        "baseUrl": "https://portal.qwen.ai/v1",
        "apiKey": "qwen-YOUR_OAUTH_TOKEN_HERE",
        "api": "openai-completions"
      }
    }
  }
}
```

**可用模型：**
- `coder-model` - Qwen Coder（代码生成）
- `vision-model` - Qwen Vision（图像理解）

#### 3.2.3 Telegram Bot Token

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

> 将 `1926010086` 替换为你的 Telegram User ID

---

## 📊 第五阶段：Cron Jobs 恢复（10 分钟）

### 5.1 设置时区

```bash
# 设置为上海时区（用于新闻报告）
sudo timedatectl set-timezone Asia/Shanghai
```

### 5.2 配置 Cron Jobs（使用新标准路径）

```bash
# 编辑 crontab
crontab -e
```

添加以下内容：

```cron
# Healthchecks.io - openclaw-heartbeat monitor
*/5 * * * * curl -fsS -o /dev/null 'https://hc-ping.com/377fe462-b99f-4f93-b33e-65870c4c4ba1'

# Healthchecks.io - openclaw-process monitor (check every 5 min)
*/5 * * * * /home/ubuntu/.openclaw/workspace/scripts/healthchecks/check-openclaw-process.sh

# Update Plus - Daily Backup at 4:00 AM Beijing Time
0 4 * * * TZ=Asia/Shanghai /home/ubuntu/.openclaw/workspace/scripts/healthchecks/daily-backup.sh

# News report generation - with Healthchecks ping on success
0 0 * * * TZ=Asia/Shanghai /home/ubuntu/.openclaw/workspace/generate_and_push_news_report.sh && /home/ubuntu/.openclaw/workspace/scripts/healthchecks/ping-cron-monitor.sh "news-report"
```

**⚠️ 注意：** 路径已更新为 `~/.openclaw/workspace/`，不再是 `~/clawd/`

### 5.3 验证 Cron Jobs

```bash
crontab -l
```

---

## 📦 第六阶段：Update Plus 配置（10 分钟）

### 6.1 创建 Update Plus 配置

```bash
cat > ~/.openclaw/update-plus.json << 'EOF'
{
  "backup_dir": "/home/ubuntu/.openclaw/backups",
  "backup_before_update": true,
  "backup_count": 10,
  "backup_paths": [
    {
      "path": "/home/ubuntu/.openclaw",
      "label": "config",
      "exclude": ["backups", "logs", "media", "subagents"]
    },
    {
      "path": "/home/ubuntu/.openclaw/workspace",
      "label": "workspace",
      "exclude": [".git", "node_modules", "__pycache__", "*.pyc"]
    }
  ],
  "skills_dirs": [
    {
      "path": "/home/ubuntu/.openclaw/workspace/skills",
      "label": "user",
      "update": true
    }
  ],
  "notifications": {
    "enabled": false
  },
  "connection_retries": 3,
  "connection_retry_delay": 60
}
EOF
```

**⚠️ 重要变化：**
- `backup_paths` 现在指向 `~/.openclaw/workspace/`（新标准）
- `skills_dirs` 现在指向 `~/.openclaw/workspace/skills/`（不是 `~/.openclaw/skills/`）

### 6.2 创建 update-plus 符号链接

```bash
ln -s ~/.openclaw/workspace/skills/update-plus/bin/update-plus ~/bin/update-plus
```

---

## 🔍 第七阶段：健康检查配置（10 分钟）

### 7.1 Healthchecks.io 监控点

| 检查项 | URL | 用途 |
|--------|-----|------|
| openclaw-heartbeat | https://hc-ping.com/377fe462-b99f-4f93-b33e-65870c4c4ba1 | 基础心跳 |
| openclaw-process | https://hc-ping.com/ac39ce97-859e-4577-9c7a-7f48b04114b8 | 进程监控 |
| openclaw-cron-jobs | https://hc-ping.com/7971a6ce-4fb5-4d4a-80f8-efbc554f7d10 | Cron 执行监控 |

### 7.2 手动测试监控

```bash
# 测试心跳
curl -fsS -o /dev/null 'https://hc-ping.com/377fe462-b99f-4f93-b33e-65870c4c4ba1'

# 测试进程监控脚本
~/.openclaw/workspace/scripts/healthchecks/check-openclaw-process.sh
```

---

## 📦 第八阶段：Skills 安装（15 分钟）

### 8.1 Skills 位置说明

**标准架构下，Skills 分布在三个位置：**

| 位置 | 类型 | 数量 | 用途 |
|------|------|------|------|
| `~/.openclaw/workspace/skills/` | 用户技能 | 15个 | ✅ **Update Plus 管理** |
| `~/.openclaw/skills/` | 本地覆盖 | 可选 | 用户自定义覆盖 |
| `~/openclaw/skills/` | 捆绑技能 | 52个 | 随 OpenClaw 安装 |

### 8.2 通过 ClawHub 安装 Skills

```bash
# 进入工作区
cd ~/.openclaw/workspace

# 使用 clawhub 安装（如果有 origin.json）
clawhub install

# 或者手动链接已克隆的 skills
# 用户技能已经在 ~/.openclaw/workspace/skills/ 中（通过 Git 克隆）
```

### 8.3 验证 Skills

```bash
# 列出已安装的用户技能
ls -la ~/.openclaw/workspace/skills/

# 测试 skill 功能
openclaw skill list
```

---

## ✅ 第九阶段：验证和测试（15 分钟）

### 9.1 功能检查清单

- [ ] OpenClaw Gateway 运行正常
- [ ] Telegram 消息可以发送/接收
- [ ] 邮件可以发送/接收
- [ ] Web 搜索功能正常
- [ ] 浏览器自动化功能正常
- [ ] 新闻报告生成正常
- [ ] Healthchecks 收到心跳
- [ ] Cron jobs 执行正常
- [ ] Update Plus 备份正常

### 9.2 架构验证命令

```bash
# 1. 验证目录结构
echo "=== 目录结构验证 ==="
ls -la ~/.openclaw/ | grep -E "workspace|skills"
ls -la ~/clawd  # 应该是软链接

# 2. 验证配置
echo "=== 配置验证 ==="
grep '"workspace"' ~/.openclaw/config.json | head -1
grep '"path"' ~/.openclaw/update-plus.json | head -2

# 3. 测试 Update Plus 备份
echo "=== Update Plus 测试 ==="
update-plus backup --dry-run

# 4. 测试 Telegram
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/sendMessage" \
  -d "chat_id=1926016086" \
  -d "text=Test message from Big-J"

# 5. 测试邮件
echo "Test body" | mail -s "Test Subject" zhou.zhengchao1@gmail.com

# 6. 测试 Tavily 搜索
cd ~/.openclaw/workspace && python3 tavily_search_test.py
```

---

## 📦 第十阶段：备份恢复（如果适用）

### 10.1 使用 Update-Plus 恢复

如果你有之前的备份文件：

```bash
# 列出可用备份
update-plus list-backups

# 恢复特定备份（会覆盖当前工作区）
update-plus restore openclaw-backup-YYYY-MM-DD-HH:MM:SS.tar.gz
```

### 10.2 手动解压备份

```bash
# 解压到临时目录
tar -xzf openclaw-backup-YYYY-MM-DD-HH:MM:SS.tar.gz -C /tmp/restore

# 恢复配置
cp -r /tmp/restore/config/* ~/.openclaw/ 2>/dev/null || true

# 恢复工作区
cp -r /tmp/restore/workspace/* ~/.openclaw/workspace/
```

**⚠️ 注意：** 备份结构已更新，新的备份包含：
- `config/` → `~/.openclaw/`（排除项外）
- `workspace/` → `~/.openclaw/workspace/`

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

# 检查 workspace 路径是否正确
grep '"workspace"' ~/.openclaw/config.json

# 清理并重启
pkill -f openclaw
openclaw gateway start
```

### 问题 2: Skills 无法加载

**症状：** 技能列表为空或报错

**解决：**
```bash
# 检查 skills 目录是否存在
ls ~/.openclaw/workspace/skills/

# 检查 Update Plus 配置
cat ~/.openclaw/update-plus.json | jq '.skills_dirs'

# 验证软链接
ls -la ~/.openclaw/skills  # 应该是软链接或不存在
```

### 问题 3: Cron Jobs 执行失败

**症状：** 定时任务没有执行

**解决：**
```bash
# 检查路径是否正确（必须是 ~/.openclaw/workspace/）
crontab -l | grep openclaw

# 测试脚本权限
ls -la ~/.openclaw/workspace/scripts/healthchecks/

# 手动执行测试
~/.openclaw/workspace/scripts/healthchecks/daily-backup.sh
```

### 问题 4: 软链接问题

**症状：** `~/clawd` 指向错误位置

**解决：**
```bash
# 删除错误的软链接
rm ~/clawd

# 重新创建
ln -s ~/.openclaw/workspace ~/clawd

# 验证
ls -la ~/clawd
readlink ~/clawd
```

### 问题 5: Update Plus 备份失败

**症状：** 备份提示路径错误

**解决：**
```bash
# 检查配置路径
cat ~/.openclaw/update-plus.json | jq '.backup_paths'

# 确保路径正确（必须是 ~/.openclaw/workspace/）
# 如果配置旧了，按第六阶段重新创建
```

---

## 🆘 紧急回滚

如果迁移后出现问题，恢复到旧架构：

```bash
#!/bin/bash
# 紧急回滚脚本

echo "开始回滚到迁移前状态..."

# 1. 恢复配置
cp ~/.openclaw/config.json.bak ~/.openclaw/config.json 2>/dev/null || true

# 2. 删除新软链接
rm -f ~/.openclaw/workspace
rm -f ~/.openclaw/skills

# 3. 恢复旧软链接
mv ~/.openclaw/workspace-old-link ~/.openclaw/workspace 2>/dev/null || true
mv ~/.openclaw/skills-old-link ~/.openclaw/skills 2>/dev/null || true

# 4. 恢复 clawd 目录
rm -f ~/clawd
mv ~/clawd.backup ~/clawd 2>/dev/null || true

echo "回滚完成！请重启 OpenClaw"
```

---

## 📞 联系信息

- **维护者：** Big-J
- **邮箱：** zhou.zhengchao1@gmail.com
- **GitHub：** https://github.com/JoshZhouSN/my-openclaw

---

## 📝 更新记录

| 日期 | 版本 | 更新内容 |
|------|------|----------|
| 2026-02-13 | v2.0 | 迁移到标准架构：`~/.openclaw/workspace/` |
| 2026-02-12 | v1.0 | 初始版本，基于 `~/clawd/` 架构 |

### 架构变更摘要（v1.0 → v2.0）

| 项目 | 旧架构 | 新架构（标准） |
|------|--------|----------------|
| 工作区 | `~/clawd/` | `~/.openclaw/workspace/` |
| Skills | `~/.openclaw/skills/` | `~/.openclaw/workspace/skills/` |
| 软链接 | `~/.openclaw/skills → ~/clawd/skills` | `~/clawd → ~/.openclaw/workspace` |
| Cron 路径 | `~/clawd/...` | `~/.openclaw/workspace/...` |
| Update Plus | `~/.openclaw/skills/` | `~/.openclaw/workspace/skills/` |

---

**提醒：**
1. 定期更新此手册
2. 测试备份恢复流程
3. 保持 API Keys 安全
4. 监控 Healthchecks 状态
