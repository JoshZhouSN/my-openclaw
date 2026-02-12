---
name: email-tool
description: Send and receive emails using Gmail SMTP/IMAP. Supports reading emails, extracting verification codes and links.
---

# Email Tool

A tool for AI agents to interact with Gmail via SMTP and IMAP.

## Features

- ✅ Send emails via Gmail SMTP
- ✅ Receive emails via Gmail IMAP
- ✅ Extract verification codes from emails
- ✅ Extract and open verification links
- ✅ List recent emails

## Prerequisites

1. Gmail account: `zhou.zhengchao1@gmail.com`
2. Gmail App Password (not your regular password!)

### How to Get Gmail App Password

1. Go to https://myaccount.google.com/security
2. Enable 2-Step Verification (required for App Passwords)
3. Go to "App passwords" section
4. Select "Mail" and your device
5. Copy the 16-character password

## Configuration

Create `~/.config/email-tool/config.env`:

```bash
EMAIL_USER=zhou.zhengchao1@gmail.com
EMAIL_PASS=your_app_password_here
```

## Usage

### Send Email

```bash
# Via skill script
./skills/email-tool/bin/send-email.sh "recipient@example.com" "Subject" "Body text"
```

### Read Latest Emails

```bash
# List last 10 emails
./skills/email-tool/bin/read-email.sh list 10
```

### Check for Verification Code

```bash
# Search for verification code in last 5 minutes
./skills/email-tool/bin/read-email.sh code
```

## Security Notes

- App Password is stored in plain text - keep the config file secure
- Use file permissions: `chmod 600 ~/.config/email-tool/config.env`
- Never commit credentials to git
