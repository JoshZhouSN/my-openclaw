#!/bin/bash
# Send email using Gmail SMTP via msmtp

set -e

CONFIG_FILE="$HOME/.config/email-tool/config.env"
MSMTP_CONFIG="$HOME/.config/msmtp/config"

# Load config
if [ -f "$CONFIG_FILE" ]; then
    source "$CONFIG_FILE"
fi

# Check arguments
if [ $# -lt 3 ]; then
    echo "Usage: $0 <to> <subject> <body>"
    echo "Example: $0 user@example.com 'Hello' 'This is a test'"
    exit 1
fi

TO="$1"
SUBJECT="$2"
BODY="$3"

# Check if EMAIL_USER and EMAIL_PASS are set
if [ -z "$EMAIL_USER" ] || [ -z "$EMAIL_PASS" ]; then
    echo "Error: EMAIL_USER and EMAIL_PASS must be set in $CONFIG_FILE"
    exit 1
fi

# Ensure msmtp config exists
mkdir -p "$HOME/.config/msmtp"
if [ ! -f "$MSMTP_CONFIG" ]; then
cat > "$MSMTP_CONFIG" << EOF
defaults
auth on
tls on
tls_trust_file /etc/ssl/certs/ca-certificates.crt
logfile ~/.config/msmtp/msmtp.log

account gmail
host smtp.gmail.com
port 587
from $EMAIL_USER
user $EMAIL_USER
password $EMAIL_PASS

account default : gmail
EOF
    chmod 600 "$MSMTP_CONFIG"
fi

# Send email
echo -e "Subject: $SUBJECT\n\n$BODY" | msmtp "$TO"

if [ $? -eq 0 ]; then
    echo "✅ Email sent successfully to $TO"
else
    echo "❌ Failed to send email"
    exit 1
fi
