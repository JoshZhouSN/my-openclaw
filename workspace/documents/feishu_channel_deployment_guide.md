# Clawdbot 飞书渠道部署指南

## 概述

这是一个用于将 Clawdbot 连接到飞书(Lark)的插件，允许通过飞书与您的 AI 助手交互。该插件支持私聊和群聊，具备丰富的功能特性。

## 部署步骤

### 1. 安装插件

```bash
clawdbot plugins install @m1heng-clawd/feishu
```

或者通过 npm 安装：

```bash
npm install @m1heng-clawd/feishu
```

### 2. 配置飞书开放平台应用

1. 访问 [飞书开放平台](https://open.feishu.cn/)
2. 创建一个自建应用
3. 应用信息中填写应用名称和描述

### 3. 获取凭证

1. 在应用控制台的「凭证与基础信息」页面获取：
   - App ID (应用ID)
   - App Secret (应用秘钥)

### 4. 配置权限

在应用控制台的「权限管理」页面添加以下必需权限：

| 权限 | 范围 | 说明 |
|------|------|------|
| `contact:user.base:readonly` | 用户信息 | 获取用户基本信息 |
| `im:message` | 消息 | 发送和接收消息 |
| `im:message.p2p_msg:readonly` | 私聊 | 读取发给机器人的私聊消息 |
| `im:message.group_at_msg:readonly` | 群聊 | 接收群内 @机器人 的消息 |
| `im:message:send_as_bot` | 发送 | 以机器人身份发送消息 |
| `im:resource` | 媒体 | 上传和下载图片/文件 |

### 5. 配置事件订阅（重要！）

在应用控制台的「事件与回调」页面：

1. 事件配置方式：选择「使用长连接接收事件」（推荐）
2. 添加事件订阅，勾选以下事件：
   - `im.message.receive_v1` - 接收消息（必需）
   - `im.message.message_read_v1` - 消息已读回执
   - `im.chat.member.bot.added_v1` - 机器人进群
   - `im.chat.member.bot.deleted_v1` - 机器人被移出群

3. 确保事件订阅的权限已申请并通过审核

### 6. 配置 Clawdbot

使用以下命令配置飞书渠道：

```bash
clawdbot config set channels.feishu.appId "你的App ID"
clawdbot config set channels.feishu.appSecret "你的App Secret"
clawdbot config set channels.feishu.enabled true
```

或者在配置文件中直接设置：

```yaml
channels:
  feishu:
    enabled: true
    appId: "你的App ID"
    appSecret: "你的App Secret"
    # 域名: "feishu" (国内) 或 "lark" (国际)
    domain: "feishu"
    # 连接模式: "websocket" (推荐) 或 "webhook"
    connectionMode: "websocket"
    # 私聊策略: "pairing" | "open" | "allowlist"
    dmPolicy: "pairing"
    # 群聊策略: "open" | "allowlist" | "disabled"
    groupPolicy: "allowlist"
    # 群聊是否需要 @机器人
    requireMention: true
    # 媒体文件最大大小 (MB, 默认 30)
    mediaMaxMb: 30
    # 回复渲染模式: "auto" | "raw" | "card"
    renderMode: "auto"
```

## 配置选项详解

### 基础配置

- `enabled`: 启用/禁用飞书渠道
- `appId`: 飞书应用ID
- `appSecret`: 飞书应用密钥
- `domain`: 飞书域名，"feishu"(中国) 或 "lark"(国际)

### 连接配置

- `connectionMode`: 连接模式，"websocket"(推荐) 或 "webhook"
- `webhookPath`: Webhook路径，默认 "/feishu/events"
- `webhookPort`: Webhook端口（可选）

### 访问控制配置

- `dmPolicy`: 私聊策略
  - `"pairing"`: 需要配对（推荐）
  - `"open"`: 开放访问
  - `"allowlist"`: 白名单访问
- `allowFrom`: 允许的用户列表
- `groupPolicy`: 群聊策略
  - `"open"`: 开放群聊
  - `"allowlist"`: 白名单群聊
  - `"disabled"`: 禁用群聊
- `requireMention`: 群聊中是否需要@机器人

### 高级配置

- `renderMode`: 渲染模式
  - `"auto"`: 自动检测（默认），有代码块或表格时用卡片
  - `"raw"`: 纯文本
  - `"card"`: 卡片模式，支持完整Markdown渲染
- `mediaMaxMb`: 媒体文件最大大小（MB）
- `historyLimit`: 历史消息限制
- `textChunkLimit`: 文本分块限制

## 功能特性

- WebSocket 和 Webhook 连接模式
- 私聊和群聊支持
- 消息回复和引用上下文
- 入站媒体支持（AI 可以看到图片、读取文件）
- 图片和文件上传（出站）
- 输入指示器（通过表情回复实现）
- 私聊配对审批流程
- 用户和群组目录查询
- 卡片渲染模式（支持语法高亮的 Markdown 渲染）

## 故障排除

### 机器人收不到消息

检查以下配置：
1. 是否配置了事件订阅？
2. 事件配置方式是否选择了长连接？
3. 是否添加了 `im.message.receive_v1` 事件？
4. 相关权限是否已申请并审核通过？

### 发送消息时出现 403 错误

确保已申请 `im:message:send_as_bot` 权限，并且权限已审核通过。

### 如何开启新对话

在聊天中发送 `/new` 命令即可开启新对话。

### 在飞书中找不到机器人

1. 确保应用已发布（至少发布到测试版本）
2. 在飞书搜索框中搜索机器人名称
3. 检查应用可用范围是否包含你的账号

## 安全注意事项

- 飞书应用的 App Secret 应妥善保管，不要泄露
- 建议使用 "pairing" 或 "allowlist" 策略限制访问权限
- 如果使用 "open" 策略，需要在 allowFrom 中包含通配符 "*"
- 定期检查和更新权限设置

## 总结

通过以上步骤，您可以成功将 Clawdbot 与飞书集成，实现通过飞书与 AI 助手的交互。插件提供了丰富的功能和灵活的配置选项，可以根据实际需求进行定制。