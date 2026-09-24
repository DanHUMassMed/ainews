# Nginx & SSL Setup: `ainews.danhiggins.org`

This directory provides the production **Nginx reverse proxy configuration**, **deployment automation**, and **Certbot SSL setup** for **AI Industry News Daily** under the subdomain `ainews.danhiggins.org`.

---

## 1. Architecture Overview

```
                      Internet (HTTPS Port 443 / HTTP Port 80)
                                      │
                                      ▼
                      ┌───────────────────────────────┐
                      │    Nginx (ainews.danhiggins.org)│
                      └───────┬───────────────┬───────┘
                              │               │
                    Static SPA│               │/api/ Proxy
                              ▼               ▼
        ┌───────────────────────────┐   ┌───────────────────────────┐
        │ /var/www/ainews.danhiggins│   │ FastAPI Backend           │
        │ .org/html (Vite Bundle)   │   │ http://192.168.1.101:8000 │
        └───────────────────────────┘   └───────────────────────────┘
```

- **Domain**: `ainews.danhiggins.org`
- **Frontend**: High-performance static SPA serving from `/var/www/ainews.danhiggins.org/html` with `try_files $uri $uri/ /index.html` fallback.
- **Backend**: Reverse proxy for `/api/` forwarding to the FastAPI application running on `http://192.168.1.101:8000`.
- **SSL / TLS**: Automated Let's Encrypt certificates managed by **Certbot**, enforcing HTTPS with HTTP $\rightarrow$ HTTPS 301 redirects.
- **Site Visibility**: Managed via Debian/Ubuntu standard `/etc/nginx/sites-available/` and `/etc/nginx/sites-enabled/` symlinks.

---

## 2. Prerequisites

1. **DNS Record**:
   - Ensure an **A Record** or **CNAME** for `ainews.danhiggins.org` points to your public IP address.
   ```bash
   dig +short ainews.danhiggins.org
   ```
2. **Firewall / Port Forwarding**:
   - Port **80** (HTTP) and Port **443** (HTTPS) must be accessible from the internet so Let's Encrypt can complete ACME domain validation.
3. **Backend Running**:
   - The FastAPI backend should be running and listening on `192.168.1.101:8000` (or `127.0.0.1:8000`).

---

## 3. Quick Installation (Automated & Idempotent)

Run the included automated installer script from the project root:

```bash
./nginx/install.sh
```

### Safety & Idempotency Guarantees:
- **Protects Existing SSL Certificates**: Checks if `/etc/nginx/sites-available/ainews.danhiggins.org` already exists. If so, it **skips copying** to prevent overwriting the SSL certificate blocks and redirects added by Certbot.
- **Strict Syntax Test Gate**: Executes `sudo nginx -t`. If the test fails, it halts immediately and **aborts the reload**, guaranteeing active sites on the server are never disrupted.
- **Safe Repeated Execution**: Can be run repeatedly at any time to recompile and deploy frontend updates into `/var/www/ainews.danhiggins.org/html` without touching your Nginx SSL setup.
- **Automatic SSL Status Detection**: Detects whether SSL is active and displays either the live `https://` URL or the exact `certbot` command to run.

---

## 4. Manual Installation Step-by-Step

If you prefer performing each step manually:

### Step 1: Create Web Root & Deploy Frontend
```bash
# Create directory
sudo mkdir -p /var/www/ainews.danhiggins.org/html
sudo chown -R dan:www-data /var/www/ainews.danhiggins.org
sudo chmod -R 775 /var/www/ainews.danhiggins.org

# Build frontend production bundle
cd /home/dan/Code/www/ainews
npm --prefix frontend run build

# Copy dist files to web root
sudo rsync -av --delete frontend/dist/ /var/www/ainews.danhiggins.org/html/
sudo chown -R dan:www-data /var/www/ainews.danhiggins.org/html
sudo chmod -R 755 /var/www/ainews.danhiggins.org/html
```

### Step 2: Install Nginx Configuration
```bash
sudo cp /home/dan/Code/www/ainews/nginx/ainews.danhiggins.org.conf /etc/nginx/sites-available/ainews.danhiggins.org
```

### Step 3: Enable the Site (Symlink)
```bash
sudo ln -sf /etc/nginx/sites-available/ainews.danhiggins.org /etc/nginx/sites-enabled/ainews.danhiggins.org
```

### Step 4: Test Syntax & Reload
```bash
sudo nginx -t
sudo systemctl reload nginx
```

---

## 5. SSL Certificate Generation with Certbot

Once the HTTP site is enabled and DNS resolves to your server, run Certbot to request and install the SSL certificate:

```bash
sudo certbot --nginx -d ainews.danhiggins.org
```

### What Certbot Does Automatically:
1. Performs the HTTP-01 challenge verification through Nginx.
2. Generates SSL certificates and stores them in:
   - Certificate: `/etc/letsencrypt/live/ainews.danhiggins.org/fullchain.pem`
   - Private Key: `/etc/letsencrypt/live/ainews.danhiggins.org/privkey.pem`
3. Injects the SSL directives (`listen 443 ssl`, certificate paths, and SSL options) into `/etc/nginx/sites-available/ainews.danhiggins.org`.
4. Adds the automatic HTTP (port 80) $\rightarrow$ HTTPS (port 443) redirect block.
5. Reloads Nginx.

### Verifying Automated Certificate Renewal
Certbot installs a systemd renewal timer (`certbot.timer`). You can verify renewal works with a dry run:

```bash
sudo certbot renew --dry-run
```

---

## 6. Resulting Post-Certbot Configuration Reference

Once Certbot finishes, your `/etc/nginx/sites-available/ainews.danhiggins.org` will match the pattern used across your other sites (`searxng.danhiggins.org`, `danhiggins.org`):

```nginx
upstream ainews_backend {
    server 192.168.1.101:8000;
    keepalive 32;
}

server {
    server_name ainews.danhiggins.org;

    root /var/www/ainews.danhiggins.org/html;
    index index.html;

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript image/svg+xml;
    gzip_vary on;
    gzip_min_length 1024;

    client_max_body_size 10m;

    # API proxy
    location /api/ {
        proxy_pass http://ainews_backend;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;

        proxy_connect_timeout 60s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
        proxy_buffering off;
    }

    # Static assets
    location /assets/ {
        expires 1y;
        add_header Cache-Control "public, max-age=31536000, immutable";
        access_log off;
    }

    # SPA routing
    location / {
        try_files $uri $uri/ /index.html;
    }

    # SSL Configuration (managed by Certbot)
    listen [::]:443 ssl;
    listen 443 ssl;
    ssl_certificate /etc/letsencrypt/live/ainews.danhiggins.org/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/ainews.danhiggins.org/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
}

# HTTP to HTTPS 301 Redirect (managed by Certbot)
server {
    if ($host = ainews.danhiggins.org) {
        return 301 https://$host$request_uri;
    }

    server_name ainews.danhiggins.org;
    listen 80;
    listen [::]:80;
    return 404;
}
```

---

## 7. Site Visibility & Maintenance Commands

### To Disable the Site:
```bash
sudo rm /etc/nginx/sites-enabled/ainews.danhiggins.org
sudo nginx -t
sudo systemctl reload nginx
```

### To Re-Enable the Site:
```bash
sudo ln -s /etc/nginx/sites-available/ainews.danhiggins.org /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### To Deploy Frontend Updates:
Whenever you make frontend changes, recompile and rsync:
```bash
npm --prefix /home/dan/Code/www/ainews/frontend run build
sudo rsync -av --delete /home/dan/Code/www/ainews/frontend/dist/ /var/www/ainews.danhiggins.org/html/
```
