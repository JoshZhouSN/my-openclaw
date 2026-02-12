# OpenClaw 配置备份与恢复

这是 Big-J 的 OpenClaw 配置备份目录。

## 文件说明

| 文件 | 说明 |
|------|------|
| `config.json` | 代理和技能配置（无敏感信息，可直接使用） |
| `openclaw.json.template` | 主配置模板（敏感信息已脱敏） |
| `restore.sh` | 一键恢复脚本 |

## 恢复流程

### 方式一：使用恢复脚本（推荐）

```bash
cd /path/to/my-openclaw
./openclaw-config/restore.sh
```

脚本会自动：
1. 安装 OpenClaw（如未安装）
2. 复制基础配置
3. 创建配置模板
4. 链接工作空间
5. 提示填入敏感信息

### 方式二：手动恢复

```bash
# 1. 安装 OpenClaw
curl -sSL https://install.openclaw.ai | bash

# 2. 复制配置
mkdir -p ~/.openclaw
cp openclaw-config/config.json ~/.openclaw/
cp openclaw-config/openclaw.json.template ~/.openclaw/openclaw.json

# 3. 编辑配置填入 API keys
nano ~/.openclaw/openclaw.json
```

### 需要填入的敏感信息

编辑 `~/.openclaw/openclaw.json`，替换以下占位符：

1. **NVIDIA API Key**
   - 搜索: `YOUR_NVIDIA_API_KEY`
   - 从 https://build.nvidia.com/ 获取

2. **Telegram Bot Token**
   - 搜索: `YOUR_TELEGRAM_BOT_TOKEN`
   - 从 @BotFather 获取

3. **Gateway Token**（可选，启动时会自动生成）
   - 搜索: `YOUR_GATEWAY_TOKEN`

4. **Qwen OAuth Token**（如使用 Qwen 模型）
   - 搜索: `YOUR_QWEN_OAUTH_TOKEN`

## 完整备份恢复

如果已有完整备份（使用 update-plus 创建）：

```bash
# 恢复完整备份
update-plus restore openclaw-backup-2026-xx-xx-xx:xx:xx.tar.gz
```

完整备份包含：
- 真实配置文件（含 API keys）
- 工作空间
- Skills
- 历史记录

## 安全提示

- ✅ **提交到 Git**：配置模板（脱敏）
- ❌ **不要提交**：含真实 API keys 的配置文件
- 🔒 **本地备份**：使用 `update-plus backup` 创建加密备份

---

*By Big-J*
