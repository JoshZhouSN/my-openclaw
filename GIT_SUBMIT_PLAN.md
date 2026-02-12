# my-openclaw 仓库提交规划

## 提交策略

### ✅ 第一批：核心文档 + 配置（建议优先提交）
- `AGENTS.md` - 工作空间指南
- `SOUL.md` - AI 助手人格设定
- `USER.md` - 用户信息
- `TOOLS.md` - 工具配置说明
- `BOOTSTRAP.md` - 首次启动指南
- `HEARTBEAT.md` - 心跳检查配置
- `IDENTITY.md` - AI 身份设定
- `CONFIG_INSTRUCTIONS.md` - 配置说明
- `.gitignore` - Git 忽略规则
- `GIT_SUBMIT_PLAN.md` - 提交规划
- `openclaw-config/` - OpenClaw 配置模板和恢复脚本

### ✅ 第二批：Skills 模块
- `skills/` 目录 - 所有技能模块
- `daily-journal-summary.skill` - 日报总结技能定义
- `daily-journal-summary/` - 日报技能目录

### ✅ 第三批：Scripts 脚本
- `scripts/` 目录 - 健康检查脚本等
- `generate_and_push_news_report.sh`
- `send_daily_report_email.sh`
- `feishu-config-setup.sh`

### ✅ 第四批：工具脚本（精选）
选择实用的、通用的工具脚本：
- `tavily_search_tool.py` - Tavily 搜索工具
- `simple_web_search.py` - 简单网页搜索
- `send_daily_news_report.py` - 日报发送
- `news_collector.py` - 新闻收集
- `intelligent_daily_journal_system.py` - 智能日报系统

### ✅ 第五批：Memory（历史记录）
- `memory/` 目录 - 历史对话记录

### ❌ 不提交的文件
1. **IDE配置目录** - `.cursor/`, `.claude/`, `.codex/` 等
2. **Python缓存** - `__pycache__/`, `*.pyc`
3. **大型文件** - `google-chrome-stable_current_amd64.deb`
4. **日志文件** - `news_report_cron.log`
5. **临时日报文件** - `daily_journal_2026-01-28.md` 等（已添加到 .gitignore）
6. **敏感配置** - `.env`, API keys
7. **已废弃的 Twitter 相关脚本**（如果需要可单独处理）

### ⚠️ 可选：考虑清理的文件
以下文件看起来是测试/废弃代码，可根据需要删除或归档：
- `enhanced_playwright_scraper.py`
- `enhanced_twitter_retriever.py`
- `final_twitter_workflow.py`
- `final_working_twitter_workflow.py`
- `twitter_content_retriever.py`
- `working_twitter_workflow.py`
- `test_*.py` (测试脚本)
- `input_credentials.py`
- `playwright_web_scraper.py`
- `run_daily_news_with_worker.py`
- `send_report_via_email.py`
- `simple_daily_journal_system.py`
- `improved_daily_journal_system.py`
- `update-plus.json`

## 提交命令示例

```bash
# 1. 配置 Git
git config user.name "Big-J"
git config user.email "zhou.zhengchao1@gmail.com"
git remote add origin https://github.com/JoshZhouSN/my-openclaw.git

# 2. 分批提交
git add AGENTS.md SOUL.md USER.md TOOLS.md BOOTSTRAP.md HEARTBEAT.md IDENTITY.md CONFIG_INSTRUCTIONS.md .gitignore GIT_SUBMIT_PLAN.md
git commit -m "feat: add core documentation"

git add openclaw-config/
git commit -m "feat: add OpenClaw config templates and restore script"

git add skills/
git commit -m "feat: add OpenClaw skills"

git add scripts/
git commit -m "feat: add utility scripts"

# 3. 推送到远程
git push -u origin master
```
