#!/bin/bash
# OpenClaw Restore Script
# 用于在新设备上恢复 Big-J 的配置

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== OpenClaw 配置恢复脚本 ===${NC}"
echo "By Big-J"
echo ""

# 检查是否已安装 OpenClaw
if ! command -v openclaw &> /dev/null; then
    echo -e "${YELLOW}OpenClaw 未安装，正在安装...${NC}"
    curl -sSL https://install.openclaw.ai | bash
else
    echo -e "${GREEN}✓ OpenClaw 已安装${NC}"
fi

# 创建配置目录
CONFIG_DIR="$HOME/.openclaw"
mkdir -p "$CONFIG_DIR"

echo ""
echo -e "${YELLOW}步骤 1: 恢复基础配置${NC}"
cp openclaw-config/config.json "$CONFIG_DIR/"
echo -e "${GREEN}✓ config.json 已复制${NC}"

echo ""
echo -e "${YELLOW}步骤 2: 创建 openclaw.json 模板${NC}"
cp openclaw-config/openclaw.json.template "$CONFIG_DIR/openclaw.json"
echo -e "${GREEN}✓ openclaw.json 模板已创建${NC}"

echo ""
echo -e "${RED}========================================${NC}"
echo -e "${RED}重要：请手动填入以下敏感信息${NC}"
echo -e "${RED}========================================${NC}"
echo ""
echo "编辑 ~/.openclaw/openclaw.json，替换以下占位符："
echo ""
echo "1. NVIDIA API Key:"
echo "   搜索: YOUR_NVIDIA_API_KEY"
echo "   替换为: nvapi-xxxxx"
echo ""
echo "2. Telegram Bot Token:"
echo "   搜索: YOUR_TELEGRAM_BOT_TOKEN"
echo "   替换为: 从 @BotFather 获取"
echo ""
echo "3. Gateway Token (可选，会自动生成):"
echo "   搜索: YOUR_GATEWAY_TOKEN"
echo ""
echo "4. Qwen OAuth Token (如使用):"
echo "   搜索: YOUR_QWEN_OAUTH_TOKEN"
echo ""
echo -e "${YELLOW}步骤 3: 安装依赖${NC}"
echo "正在检查并安装必要依赖..."

# 检查 Python 依赖
pip3 install -q playwright beautifulsoup4 requests 2>/dev/null || echo "部分 Python 包安装失败，请手动检查"

# 检查 Node.js
if command -v node &> /dev/null; then
    echo -e "${GREEN}✓ Node.js 已安装: $(node --version)${NC}"
else
    echo -e "${YELLOW}⚠ Node.js 未安装，某些功能可能不可用${NC}"
fi

echo ""
echo -e "${YELLOW}步骤 4: 恢复工作空间${NC}"

# 获取仓库目录
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET_WORKSPACE="$HOME/clawd"

if [ "$REPO_DIR" != "$TARGET_WORKSPACE" ]; then
    echo "将仓库链接到 $TARGET_WORKSPACE..."
    if [ -d "$TARGET_WORKSPACE" ]; then
        echo -e "${YELLOW}警告: $TARGET_WORKSPACE 已存在${NC}"
        echo "请选择操作:"
        echo "1) 备份现有目录并替换"
        echo "2) 跳过工作空间恢复"
        read -p "选择 [1/2]: " choice
        case $choice in
            1)
                mv "$TARGET_WORKSPACE" "$TARGET_WORKSPACE.backup.$(date +%Y%m%d)"
                ln -s "$REPO_DIR" "$TARGET_WORKSPACE"
                echo -e "${GREEN}✓ 工作空间已链接${NC}"
                ;;
            2)
                echo "跳过工作空间恢复"
                ;;
            *)
                echo "无效选择，跳过"
                ;;
        esac
    else
        ln -s "$REPO_DIR" "$TARGET_WORKSPACE"
        echo -e "${GREEN}✓ 工作空间已链接到 $TARGET_WORKSPACE${NC}"
    fi
else
    echo -e "${GREEN}✓ 工作空间已在正确位置${NC}"
fi

echo ""
echo -e "${YELLOW}步骤 5: 安装 Playwright 浏览器${NC}"
python3 -m playwright install chromium 2>/dev/null || echo "Playwright 浏览器安装失败，请手动运行: python3 -m playwright install"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}恢复脚本执行完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "后续步骤:"
echo "1. 编辑 ~/.openclaw/openclaw.json 填入 API keys"
echo "2. 运行 'openclaw gateway status' 检查状态"
echo "3. 运行 'openclaw gateway start' 启动服务"
echo ""
echo "如需完整备份恢复，请使用 update-plus:"
echo "   update-plus restore <backup-file.tar.gz>"
echo ""
echo -e "${GREEN}祝使用愉快！ - Big-J${NC}"
