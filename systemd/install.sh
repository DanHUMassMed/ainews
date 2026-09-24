#!/usr/bin/env bash
# ==============================================================================
# Install AI News systemd services & timer
# ==============================================================================
set -euo pipefail

# Ensure script is run as root or with sudo
if [[ $EUID -ne 0 ]]; then
   echo "Error: This script must be run as root or via sudo." >&2
   echo "Usage: sudo ./systemd/install.sh" >&2
   exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
SYSTEMD_DIR="/etc/systemd/system"

echo "=== Installing AI News Systemd Services & Timer ==="
echo "Source directory: $SCRIPT_DIR"
echo "Target directory: $SYSTEMD_DIR"

# Ensure logs directory exists with correct user ownership
mkdir -p "$REPO_DIR/logs"
touch "$REPO_DIR/logs/backend.log" "$REPO_DIR/logs/editorial_cron.log"
chown -R dan:dan "$REPO_DIR/logs"

# Copy unit files
echo "Copying unit files to $SYSTEMD_DIR..."
cp "$SCRIPT_DIR/ainews-backend.service" "$SYSTEMD_DIR/ainews-backend.service"
cp "$SCRIPT_DIR/ainews-editorial.service" "$SYSTEMD_DIR/ainews-editorial.service"
cp "$SCRIPT_DIR/ainews-editorial.timer" "$SYSTEMD_DIR/ainews-editorial.timer"

# Set permissions
chmod 644 "$SYSTEMD_DIR/ainews-backend.service"
chmod 644 "$SYSTEMD_DIR/ainews-editorial.service"
chmod 644 "$SYSTEMD_DIR/ainews-editorial.timer"

# Reload systemd
echo "Reloading systemd daemon..."
systemctl daemon-reload

# Enable and start backend service
echo "Enabling and starting ainews-backend.service..."
systemctl enable --now ainews-backend.service

# Enable and start timer
echo "Enabling and starting ainews-editorial.timer..."
systemctl enable --now ainews-editorial.timer

echo ""
echo "=== Installation Complete ==="
echo "Backend service status:"
systemctl status ainews-backend.service --no-pager || true

echo ""
echo "Timer status:"
systemctl status ainews-editorial.timer --no-pager || true

echo ""
echo "Next scheduled runs:"
systemctl list-timers --all | grep -E "ainews|NEXT" || true

echo ""
echo "To test the editorial service immediately without waiting for the timer:"
echo "  sudo systemctl start --no-block ainews-editorial.service"
echo ""
echo "To view live logs:"
echo "  Backend API:    tail -f $REPO_DIR/logs/backend.log"
echo "  Editorial Cron: tail -f $REPO_DIR/logs/editorial_cron.log"
