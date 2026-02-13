# OpenClaw 标准架构迁移计划
# 目标：将 ~/clawd/ 迁移到 ~/.openclaw/workspace/
# 要求：零宕机，可回滚

## 当前状态
- 实际数据在：~/clawd/
- ~/.openclaw/workspace → ~/clawd/workspace (软链接)
- ~/.openclaw/skills → ~/clawd/skills (软链接)
- OpenClaw 配置中 workspace 指向 /home/ubuntu/clawd

## 目标状态（官方标准架构）
- 实际数据在：~/.openclaw/workspace/
- ~/clawd → ~/.openclaw/workspace (软链接，可选，向后兼容)
- OpenClaw 配置中 workspace 指向 ~/.openclaw/workspace

## 迁移步骤

### Phase 1: 准备阶段（无风险）

1. **创建备份**
   ```bash
   # 完整备份当前状态
   cp -r ~/.openclaw ~/.openclaw.backup.pre-migration.$(date +%Y%m%d)
   ```

2. **验证当前配置**
   ```bash
   # 检查当前 workspace 配置
   cat ~/.openclaw/config.json | jq '.agents.defaults.workspace'
   ```

3. **创建新的 workspace 目录结构**
   ```bash
   # 创建目标目录（如果不存在）
   mkdir -p ~/.openclaw/workspace-new
   ```

### Phase 2: 数据迁移（关键步骤）

4. **迁移 workspace 内容**
   ```bash
   # 复制 workspace 文件（不是移动，保留原文件作为备份）
   cp -r ~/clawd/workspace/* ~/.openclaw/workspace-new/ 2>/dev/null || true
   cp -r ~/clawd/workspace/.* ~/.openclaw/workspace-new/ 2>/dev/null || true
   ```

5. **迁移根目录配置文档**
   ```bash
   # 复制核心配置文件
   cp ~/clawd/AGENTS.md ~/.openclaw/workspace-new/
   cp ~/clawd/SOUL.md ~/.openclaw/workspace-new/
   cp ~/clawd/USER.md ~/.openclaw/workspace-new/
   cp ~/clawd/IDENTITY.md ~/.openclaw/workspace-new/
   cp ~/clawd/TOOLS.md ~/.openclaw/workspace-new/
   cp ~/clawd/MEMORY.md ~/.openclaw/workspace-new/
   cp ~/clawd/HEARTBEAT.md ~/.openclaw/workspace-new/
   cp ~/clawd/BOOTSTRAP.md ~/.openclaw/workspace-new/ 2>/dev/null || true
   ```

6. **迁移记忆目录**
   ```bash
   cp -r ~/clawd/memory ~/.openclaw/workspace-new/
   ```

7. **迁移 skills（重要！）**
   ```bash
   # 创建 workspace 级别的 skills 目录
   mkdir -p ~/.openclaw/workspace-new/skills
   
   # 复制所有 skills（除了软链接）
   for skill in ~/clawd/skills/*/; do
       if [ -d "$skill" ] && [ ! -L "$skill" ]; then
           cp -r "$skill" ~/.openclaw/workspace-new/skills/
       fi
   done
   ```

8. **保留脚本和其他文件**
   ```bash
   # 这些可以留在 workspace 根目录或单独管理
   mkdir -p ~/.openclaw/workspace-new/scripts
   cp ~/clawd/scripts/* ~/.openclaw/workspace-new/scripts/ 2>/dev/null || true
   cp ~/clawd/*.sh ~/.openclaw/workspace-new/ 2>/dev/null || true
   cp ~/clawd/*.py ~/.openclaw/workspace-new/ 2>/dev/null || true
   ```

### Phase 3: 切换配置（谨慎操作）

9. **准备新配置**
   ```bash
   # 创建新配置文件
   cat > ~/.openclaw/config.json.new << 'EOF'
   {
     "agents": {
       "defaults": {
         "workspace": "/home/ubuntu/.openclaw/workspace",
         "model": "nvidia/moonshotai/kimi-k2.5",
         "subagents": {
           "archiveAfterMinutes": 60
         }
       },
       "registry": {
         "main": {
           "id": "main",
           "name": "Main Agent",
           "description": "Primary agent for user interactions",
           "model": "nvidia/moonshotai/kimi-k2.5",
           "workspace": "/home/ubuntu/.openclaw/workspace",
           "skills": [
             "web_fetch",
             "read",
             "write",
             "exec",
             "sessions_spawn",
             "sessions_list",
             "sessions_history",
             "sessions_send"
           ]
         },
         "worker": {
           "id": "worker",
           "name": "Worker Subagent",
           "description": "Specialized worker for parallel task execution",
           "model": "nvidia/moonshotai/kimi-k2.5",
           "workspace": "/home/ubuntu/.openclaw/workspace",
           "skills": [
             "web_fetch",
             "read",
             "write",
             "exec",
             "browser"
           ],
           "concurrency": 4,
           "timeoutSeconds": 120
         }
       }
     }
   }
   EOF
   ```

10. **原子切换（关键！）**
    ```bash
    # 1. 保存当前软链接
    mv ~/.openclaw/workspace ~/.openclaw/workspace-old-link
    mv ~/.openclaw/skills ~/.openclaw/skills-old-link
    
    # 2. 移动新数据到位
    mv ~/.openclaw/workspace-new ~/.openclaw/workspace
    
    # 3. 创建新的 skills 软链接（指向 workspace/skills）
    # 或者让 skills 直接在 workspace 里
    
    # 4. 切换配置
    cp ~/.openclaw/config.json ~/.openclaw/config.json.bak
    mv ~/.openclaw/config.json.new ~/.openclaw/config.json
    ```

11. **创建向后兼容的软链接**
    ```bash
    # 让 ~/clawd 指向新的位置（可选，为了兼容性）
    mv ~/clawd ~/clawd.backup
    ln -s ~/.openclaw/workspace ~/clawd
    ```

### Phase 4: 验证和清理

12. **验证测试**
    - 检查 OpenClaw 是否能正常读取 workspace
    - 验证 skills 是否能正常加载
    - 测试文件读写
    - 验证 Git 状态

13. **更新 Update Plus 配置**
    ```bash
    # 更新 backup_paths
    # 把 ~/.openclaw/workspace 加入备份
    ```

14. **清理（确认一切正常后）**
    ```bash
    # 删除备份
    rm -rf ~/.openclaw/workspace-old-link
    rm -rf ~/.openclaw/skills-old-link
    rm -rf ~/clawd.backup
    rm -rf ~/.openclaw.backup.pre-migration.*
    ```

## 回滚方案

如果出现问题，随时可以回滚：

```bash
# 1. 恢复配置
cp ~/.openclaw/config.json.bak ~/.openclaw/config.json

# 2. 恢复软链接
rm -f ~/.openclaw/workspace
mv ~/.openclaw/workspace-old-link ~/.openclaw/workspace
mv ~/.openclaw/skills-old-link ~/.openclaw/skills

# 3. 恢复 clawd 目录
rm -f ~/clawd
mv ~/clawd.backup ~/clawd
```

## 注意事项

1. **不要删除原数据** 直到确认新配置完全正常
2. **保持会话** 迁移过程中现有会话应该不受影响
3. **测试顺序** 先测试读取，再测试写入，最后测试新会话
4. **备份策略** Update Plus 会在下次运行时自动备份新位置
# Migration completed on Fri Feb 13 13:41:29 UTC 2026
