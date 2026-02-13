# Moltbot安全部署记录

**日期**: 2026年1月29日

## 部署概述

对Moltbot实例进行了安全加固，以符合Nick Spisak在X上发布的安全建议。

## 已实施的安全措施

### 1. 防火墙配置 (UFW)

**操作**:
- 安装并配置了UFW防火墙
- 设置默认策略：拒绝所有入站连接，允许所有出站连接
- 允许SSH访问（端口22）
- 允许本地访问Moltbot网关（端口18789，仅限127.0.0.1）

**具体命令**:
```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow from 127.0.0.1 to any port 18789
sudo ufw --force enable
```

**验证结果**:
```
Status: active
Logging: on (low)
Default: deny (incoming), allow (outgoing), disabled (routed)
New profiles: skip

To                         Action      From
--                         ------      ----
22/tcp                     ALLOW IN    Anywhere                  
18789                      ALLOW IN    127.0.0.1                 
22/tcp (v6)                ALLOW IN    Anywhere (v6)
```

### 2. 禁用mDNS广播

**操作**:
- 在~/.bashrc中添加环境变量以禁用mDNS广播

**具体命令**:
```bash
echo 'export CLAWDBOT_DISABLE_BONJOUR=1' >> ~/.bashrc
```

## 当前安全配置状态

### 网络绑定
- Moltbot网关配置为`"bind": "loopback"`（仅本地访问）
- 端口18789仅在127.0.0.1上监听
- 外部无法直接访问Moltbot网关

### 认证
- 配置为令牌认证模式
- 使用安全的访问令牌

### 文件权限
- ~/.moltbot目录权限: drwx------ (700)
- 敏感配置文件权限适当

### Node.js版本
- 版本: v24.13.0 (较新版本，安全性较好)

## 回滚计划

如果需要恢复到之前的状态：

### 1. 禁用防火墙
```bash
sudo ufw disable
```

### 2. 恢复mDNS广播
编辑~/.bashrc并删除或注释掉:
```bash
export CLAWDBOT_DISABLE_BONJOUR=1
```

### 3. 验证Moltbot功能
- 重启Moltbot服务: `moltbot gateway restart`
- 验证基本功能正常

## 影响评估

### 正面影响
- 显著提高系统安全性
- 防止外部未授权访问
- 符合安全最佳实践

### 潜在影响
- 无法从外部直接访问Moltbot Web界面
- 需要通过SSH隧道或VPN进行远程管理

### 服务连通性
- 所有出站连接（API调用、外部服务）不受影响
- Telegram机器人功能正常
- AI模型访问正常

## 验证步骤

1. 确认防火墙已激活
2. 确认Moltbot服务仍在运行
3. 测试基本功能（如发送消息）
4. 验证出站连接正常

## 维护建议

- 定期检查防火墙规则
- 监控系统日志中的异常访问尝试
- 定期更新系统和Moltbot版本