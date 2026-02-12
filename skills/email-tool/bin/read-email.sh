#!/bin/bash
# Read emails using Gmail IMAP via mbsync

set -e

CONFIG_FILE="$HOME/.config/email-tool/config.env"
MBSYNC_CONFIG="$HOME/.mbsyncrc"
MAILDIR="$HOME/.local/share/mail/gmail"

# Load config
if [ -f "$CONFIG_FILE" ]; then
    source "$CONFIG_FILE"
fi

# Check if EMAIL_USER and EMAIL_PASS are set
if [ -z "$EMAIL_USER" ] || [ -z "$EMAIL_PASS" ]; then
    echo "Error: EMAIL_USER and EMAIL_PASS must be set in $CONFIG_FILE"
    exit 1
fi

# Ensure mbsync config exists
if [ ! -f "$MBSYNC_CONFIG" ]; then
cat > "$MBSYNC_CONFIG" << EOF
IMAPAccount gmail
Host imap.gmail.com
Port 993
User $EMAIL_USER
Pass "${EMAIL_PASS}"
SSLType IMAPS

IMAPStore gmail-remote
Account gmail

MaildirStore gmail-local
Path $MAILDIR/
Inbox $MAILDIR/inbox
SubFolders Verbatim

Channel gmail-inbox
Far :gmail-remote:
Near :gmail-local:inbox
Create Both
Expunge Both
Patterns *
SyncState *
EOF
    chmod 600 "$MBSYNC_CONFIG"
fi

# Function to sync emails
sync_emails() {
    mkdir -p "$MAILDIR/inbox"
    mbsync gmail-inbox 2>&1 || true
}

# Function to list recent emails
list_emails() {
    local count=${1:-10}
    sync_emails
    
    if [ ! -d "$MAILDIR/inbox/cur" ]; then
        echo "No emails found"
        return
    fi
    
    echo "=== Recent Emails ==="
    ls -1t "$MAILDIR/inbox/cur" 2>/dev/null | head -n "$count" | while read -r file; do
        if [ -f "$MAILDIR/inbox/cur/$file" ]; then
            subject=$(grep -m1 "^Subject:" "$MAILDIR/inbox/cur/$file" | sed 's/Subject: //' || echo "No Subject")
            from=$(grep -m1 "^From:" "$MAILDIR/inbox/cur/$file" | sed 's/From: //' || echo "Unknown")
            date=$(grep -m1 "^Date:" "$MAILDIR/inbox/cur/$file" | sed 's/Date: //' || echo "Unknown")
            echo ""
            echo "From: $from"
            echo "Subject: $subject"
            echo "Date: $date"
            echo "---"
        fi
    done
}

# Function to extract verification code
extract_code() {
    sync_emails
    
    if [ ! -d "$MAILDIR/inbox/cur" ]; then
        echo "No emails found"
        return
    fi
    
    # Look for recent emails (last 5 minutes) with verification codes
    find "$MAILDIR/inbox/cur" -type f -mmin -5 2>/dev/null | while read -r file; do
        content=$(cat "$file" 2>/dev/null)
        # Extract 6-digit codes
        code=$(echo "$content" | grep -oE '\b[0-9]{6}\b' | head -n1)
        if [ -n "$code" ]; then
            subject=$(grep -m1 "^Subject:" "$file" | sed 's/Subject: //' || echo "No Subject")
            echo "Found verification code: $code"
            echo "From email: $subject"
            return
        fi
    done
}

# Function to extract verification links
extract_links() {
    sync_emails
    
    if [ ! -d "$MAILDIR/inbox/cur" ]; then
        echo "No emails found"
        return
    fi
    
    # Look for recent emails with links
    find "$MAILDIR/inbox/cur" -type f -mmin -10 2>/dev/null | while read -r file; do
        content=$(cat "$file" 2>/dev/null)
        # Extract http/https links
        links=$(echo "$content" | grep -oE 'https?://[^ ]+' | grep -E '(verify|confirm|activate|auth)' | head -n3)
        if [ -n "$links" ]; then
            subject=$(grep -m1 "^Subject:" "$file" | sed 's/Subject: //' || echo "No Subject")
            echo "Found links in: $subject"
            echo "$links"
            return
        fi
    done
}

# Main command handler
case "${1:-list}" in
    list)
        list_emails "${2:-10}"
        ;;
    code)
        extract_code
        ;;
    links)
        extract_links
        ;;
    sync)
        sync_emails
        echo "Emails synced"
        ;;
    *)
        echo "Usage: $0 {list|code|links|sync} [args]"
        echo "  list [count] - List recent emails"
        echo "  code         - Extract verification code from recent emails"
        echo "  links        - Extract verification links from recent emails"
        echo "  sync         - Sync emails manually"
        exit 1
        ;;
esac
