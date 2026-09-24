#!/usr/bin/env bash
set -e

# ==============================================================================
# Installation & Deployment Script for ainews.danhiggins.org Nginx Site
# Idempotent: safe to run multiple times without overwriting SSL certificates.
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
SITE_NAME="ainews.danhiggins.org"
WEB_ROOT="/var/www/${SITE_NAME}/html"
TARGET_CONF="/etc/nginx/sites-available/${SITE_NAME}"
ENABLED_LINK="/etc/nginx/sites-enabled/${SITE_NAME}"

echo "=================================================================="
echo " Deploying ${SITE_NAME} Nginx Configuration"
echo " Project Root: ${PROJECT_ROOT}"
echo " Web Root:     ${WEB_ROOT}"
echo " Config Path:  ${TARGET_CONF}"
echo "=================================================================="

# 1. Ensure production web root directory exists
echo "==> Ensuring web root directory exists: ${WEB_ROOT}..."
sudo mkdir -p "${WEB_ROOT}"
sudo chown -R dan:www-data "/var/www/${SITE_NAME}"
sudo chmod -R 775 "/var/www/${SITE_NAME}"

# 2. Build production frontend assets
echo "==> Building frontend assets (Vite)..."
npm --prefix "${PROJECT_ROOT}/frontend" run build

# 3. Copy production build into web root
echo "==> Deploying latest frontend bundle into ${WEB_ROOT}..."
sudo rsync -av --delete "${PROJECT_ROOT}/frontend/dist/" "${WEB_ROOT}/"
sudo chown -R dan:www-data "${WEB_ROOT}"
sudo chmod -R 755 "${WEB_ROOT}"

# 4. Copy Nginx site configuration to sites-available ONLY IF not already present
#    (Protects existing SSL certificates and certbot changes from being overwritten)
if [ -f "${TARGET_CONF}" ]; then
    echo "==> [PRESERVE] ${TARGET_CONF} already exists."
    echo "    Skipping copy to protect existing configuration and SSL certificates."
else
    echo "==> [INSTALL] Staging initial Nginx site configuration to ${TARGET_CONF}..."
    sudo cp "${SCRIPT_DIR}/ainews.danhiggins.org.conf" "${TARGET_CONF}"
fi

# 5. Enable site by creating symlink in sites-enabled if not already active
if [ -L "${ENABLED_LINK}" ] && [ "$(readlink -f "${ENABLED_LINK}")" = "${TARGET_CONF}" ]; then
    echo "==> [SYMLINK] ${ENABLED_LINK} is already active."
else
    echo "==> [SYMLINK] Creating symlink in ${ENABLED_LINK}..."
    sudo ln -sf "${TARGET_CONF}" "${ENABLED_LINK}"
fi

# 6. Test Nginx syntax and only reload if the test passes
echo "==> Verifying Nginx configuration syntax..."
if sudo nginx -t; then
    echo "==> Syntax test passed. Reloading Nginx service..."
    sudo systemctl reload nginx
    echo "==> Nginx service successfully reloaded."
else
    echo "==> ERROR: Nginx configuration test failed! Not reloading Nginx to protect running services." >&2
    exit 1
fi

# 7. Check if SSL is already configured or if Certbot is still needed
HAS_SSL=false
if grep -q "ssl_certificate" "${TARGET_CONF}" 2>/dev/null; then
    HAS_SSL=true
fi

echo ""
echo "=================================================================="
if [ "${HAS_SSL}" = true ]; then
    echo " ✓ Site ${SITE_NAME} is active with HTTPS / SSL enabled!"
    echo "   Visit: https://${SITE_NAME}/"
else
    echo " ✓ Site ${SITE_NAME} is active on HTTP!"
    echo ""
    echo " Next Step: Obtain Let's Encrypt SSL Certificate with Certbot:"
    echo "   sudo certbot --nginx -d ${SITE_NAME}"
    echo ""
    echo " Certbot will automatically configure HTTPS (port 443) and"
    echo " the HTTP -> HTTPS redirect in ${TARGET_CONF}."
fi
echo "=================================================================="
