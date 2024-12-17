#!/bin/bash

# Variables
TARGET_URL="http://playteawbeta.apexmc.co:1849"
TUNNEL_PORT="1880"  # This is where the Cloudflare tunnel will connect to
SERVER_NAME="map.toendallwars.org"
NGINX_CONF_PATH="/etc/nginx/sites-available/bluemap"


check_service() {
    systemctl is-active --quiet "$1"
}

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" >&2
   exit 1
fi


if ! command -v nginx &> /dev/null; then
    echo "Nginx is not installed. Installing..."
    apt update && apt install -y nginx
else
    echo "Nginx is already installed"
fi


cat <<EOF > "$NGINX_CONF_PATH"
server {
    listen $TUNNEL_PORT;
    server_name $SERVER_NAME;

    location / {
        proxy_pass $TARGET_URL;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;

        # Optional: Cache static assets
        proxy_cache_valid 200 1d;
        proxy_cache_bypass \$http_upgrade;
    }

    # Optional: Return custom error page for 502 errors
    error_page 502 /502.html;
    location = /502.html {
        root /usr/share/nginx/html;
        internal;
    }
}
EOF


if [[ ! -L "$NGINX_ENABLED_PATH" ]]; then
    ln -s "$NGINX_CONF_PATH" "$NGINX_ENABLED_PATH"
    echo "Enabled the bluemap site configuration"
else
    echo "Bluemap site configuration is already enabled"
fi


if nginx -t; then
    echo "Nginx configuration test passed"
else
    echo "Nginx configuration test failed. Exiting" >&2
    exit 1
fi


if check_service nginx; then
    echo "Reloading Nginx..."
    systemctl reload nginx
else
    echo "Starting Nginx..."
    systemctl start nginx
fi

echo "Nginx proxy setup for $SERVER_NAME completed"
