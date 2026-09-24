#!/usr/bin/env bash
# ==============================================================================
# Uninstall AI News systemd services & timer
# ==============================================================================
set -euo pipefail

if [[ $EUID -ne 0 ]]; then
   echo "Error: This script must be run as root or via sudo." >&2
   echo "Usage: sudo ./systemd/uninstall.sh" >&2
   exit 1
fi

SYSTEMD_DIR="/etc/systemd/system"

echo "=== Uninstalling AI News Systemd Services & Timer ==="

# Stop and disable timer & services
systemctl stop ainews-editorial.timer 2>/dev/null || true
systemctl disable ainews-editorial.timer 2>/dev/null || true
systemctl stop ainews-editorial.service 2>/dev/null || true
systemctl disable ainews-editorial.service 2>/dev/null || true
systemctl stop ainews-backend.service 2>/dev/null || true
systemctl disable ainews-backend.service 2>/dev/null || true

# Remove unit files
rm -f "$SYSTEMD_DIR/ainews-backend.service"
rm -f "$SYSTEMD_DIR/ainews-editorial.service"
rm -f "$SYSTEMD_DIR/ainews-editorial.timer"

# Reload systemd
systemctl daemon-reload

echo "Uninstallation complete. All ainews services and timers removed."
