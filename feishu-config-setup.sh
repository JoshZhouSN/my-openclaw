#!/bin/bash

echo "开始配置 Moltbot 飞书通道..."

echo "第一步：启用飞书通道"
moltbot config set channels.feishu.enabled true

echo "第二步：设置飞书应用ID（请替换为您自己的值）"
echo "注意：您需要先在飞书开放平台创建应用并获取 App ID"
echo "示例命令：moltbot config set channels.feishu.appId \"cli_xxx_your_app_id\""

echo "第三步：设置飞书应用密钥（请替换为您自己的值）"
echo "注意：您需要先在飞书开放平台创建应用并获取 App Secret"
echo "示例命令：moltbot config set channels.feishu.appSecret \"your_app_secret_here\""

echo "第四步：设置其他推荐配置"
moltbot config set channels.feishu.domain "feishu"
moltbot config set channels.feishu.connectionMode "websocket"
moltbot config set channels.feishu.dmPolicy "pairing"
moltbot config set channels.feishu.groupPolicy "allowlist"
moltbot config set channels.feishu.requireMention true
moltbot config set channels.feishu.mediaMaxMb 30
moltbot config set channels.feishu.renderMode "auto"

echo "配置设置完成！"
echo ""
echo "重要提醒："
echo "1. 请务必在飞书开放平台完成以下设置："
echo "   - 创建自建应用"
echo "   - 获取 App ID 和 App Secret"
echo "   - 配置所需权限（contact:user.base:readonly, im:message, 等）"
echo "   - 配置事件订阅（im.message.receive_v1 等）"
echo "2. 然后使用实际的 App ID 和 App Secret 替换配置"
echo ""
echo "设置真实凭证的命令示例："
echo "moltbot config set channels.feishu.appId \"您的实际App ID\""
echo "moltbot config set channels.feishu.appSecret \"您的实际App Secret\""
echo ""
echo "完成后，重启 Moltbot 服务："
echo "moltbot gateway restart"