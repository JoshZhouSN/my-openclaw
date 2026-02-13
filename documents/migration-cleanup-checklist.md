# 迁移后清理清单

## 背景

2026-02-13 完成了 OpenClaw 目录架构标准化迁移。以下文件是迁移过程中的备份和临时文件，在系统稳定运行一段时间后可删除。

## 待清理文件清单

### 1. 旧软链接备份（可立即删除）
```bash
rm ~/.openclaw/workspace-old-link
rm ~/.openclaw/skills-old-link
```

### 2. 迁移临时备份（建议观察1-2周后删除）
```bash
# 迁移前的完整备份
rm -rf ~/.openclaw.backup.pre-migration.202602131339

# 迁移时的临时备份目录
rm -rf ~/.openclaw/workspace.bak.20260213
rm -rf ~/.openclaw/skills.bak.20260213

# 原数据备份
rm -rf ~/clawd.backup
```

### 3. 配置文件备份（可选，确认稳定后可删）
```bash
rm ~/.openclaw/config.json.bak
rm ~/.openclaw/update-plus.json.bak
rm ~/.openclaw/openclaw.json.bak*
```

## 一键清理脚本

```bash
#!/bin/bash
# 迁移后清理脚本 - 请在确认系统稳定后执行

echo "开始清理迁移备份文件..."

# 旧软链接
rm -f ~/.openclaw/workspace-old-link
rm -f ~/.openclaw/skills-old-link
echo "✓ 旧软链接已删除"

# 迁移备份
rm -rf ~/.openclaw.backup.pre-migration.*
rm -rf ~/.openclaw/workspace.bak.*
rm -rf ~/.openclaw/skills.bak.*
rm -rf ~/clawd.backup
echo "✓ 迁移备份已删除"

# 配置备份（可选）
# rm -f ~/.openclaw/config.json.bak
# rm -f ~/.openclaw/update-plus.json.bak
# rm -f ~/.openclaw/openclaw.json.bak*
# echo "✓ 配置备份已删除"

echo "清理完成！"
echo "当前剩余备份:"
ls -d ~/.openclaw/*-old-link ~/.openclaw/*.bak* ~/.openclaw.backup.* ~/clawd.backup 2>/dev/null || echo "  无"
```

## 检查命令

清理前可执行以下命令查看将要删除的文件：

```bash
echo "=== 将要删除的文件 ==="
ls -d ~/.openclaw/*-old-link 2>/dev/null
ls -d ~/.openclaw/*.bak* 2>/dev/null
ls -d ~/.openclaw.backup.* 2>/dev/null
ls -d ~/clawd.backup 2>/dev/null
```

## 注意事项

1. **确认稳定后再清理** - 建议观察 1-2 周，确保一切运行正常
2. **config.json.bak** - 这是回滚的最后保障，建议保留更长时间
3. **openclaw.json.bak*** - 这些是运行时自动备份，可以安全删除
4. **~/clawd.backup** - 这是原数据的完整备份，确认新架构稳定后可删除

## 迁移完成状态

- ✅ 数据已迁移至 `~/.openclaw/workspace/`
- ✅ OpenClaw 配置已更新
- ✅ Cron 路径已统一
- ✅ Update Plus 配置已更新
- ✅ Git 仓库已推送至 GitHub
- ✅ 所有路径指向正确位置

---

*文档创建时间: 2026-02-13*
*迁移完成时间: 2026-02-13*
