# TOOLS.md - Local Notes

Skills define *how* tools work. This file is for *your* specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:
- Camera names and locations
- SSH hosts and aliases  
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras
- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH
- home-server → 192.168.1.100, user: admin

### TTS
- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.

### Email (Gmail)
- **Account**: zhou.zhengchao1@gmail.com
- **SMTP**: smtp.gmail.com:587
- **IMAP**: imap.gmail.com:993
- **Config**: `~/.config/email-tool/config.env`
- **Skill**: `/home/ubuntu/clawd/skills/email-tool/`

### Usage
```bash
# Send email
./skills/email-tool/bin/send-email.sh "to@example.com" "Subject" "Body"

# Read recent emails
./skills/email-tool/bin/read-email.sh list 10

# Extract verification code
./skills/email-tool/bin/read-email.sh code
```

### Healthchecks.io Monitors
- **openclaw-heartbeat**: https://hc-ping.com/377fe462-b99f-4f93-b33e-65870c4c4ba1 (5min/10min)
- **openclaw-process**: https://hc-ping.com/ac39ce97-859e-4577-9c7a-7f48b04114b8 (5min/10min)
- **openclaw-cron-jobs**: https://hc-ping.com/7971a6ce-4fb5-4d4a-80f8-efbc554f7d10 (1day/2hr)
- **Scripts**: `/home/ubuntu/clawd/scripts/healthchecks/`
