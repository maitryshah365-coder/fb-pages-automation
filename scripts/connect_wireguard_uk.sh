#!/usr/bin/env bash
set -e

echo "=========================================================="
echo "🔒 INITIALIZING SURFSHARK LONDON WIREGUARD TUNNEL"
echo "=========================================================="

sudo apt-get update -y
sudo apt-get install -y wireguard wireguard-tools resolvconf

sudo mkdir -p /etc/wireguard

cat << 'EOF' | sudo tee /etc/wireguard/wg0.conf > /dev/null
[Interface]
Address = 10.14.0.2/16
PrivateKey = sLFzckN6irubqb0Qm5E7xzSGnyDHOeFiP3orSn6E6nU=
DNS = 162.252.172.57, 149.154.159.92

[Peer]
PublicKey = iBJRXLZwXuWWrOZE1ZrAXEKMgV/z0WjG0Tks5rnWLBI=
AllowedIPs = 0.0.0.0/0
Endpoint = uk-lon.prod.surfshark.com:51820
PersistentKeepalive = 25
EOF

sudo chmod 600 /etc/wireguard/wg0.conf

echo "Connecting WireGuard wg0 tunnel to London, UK..."
sudo wg-quick up wg0

echo "Waiting for tunnel handshake..."
sleep 3

# Verify IP Geolocation via 2 independent endpoints
GEO=$(curl -s --max-time 10 https://ipinfo.io/json || curl -s --max-time 10 https://ipapi.co/json || echo "{}")
echo "Tunnel Telemetry Response: $GEO"

COUNTRY=$(echo "$GEO" | python3 -c "import sys, json; print(json.load(sys.stdin).get('country', ''))" 2>/dev/null || echo "")
CITY=$(echo "$GEO" | python3 -c "import sys, json; print(json.load(sys.stdin).get('city', ''))" 2>/dev/null || echo "")
IP=$(echo "$GEO" | python3 -c "import sys, json; print(json.load(sys.stdin).get('ip', ''))" 2>/dev/null || echo "")
ORG=$(echo "$GEO" | python3 -c "import sys, json; print(json.load(sys.stdin).get('org', ''))" 2>/dev/null || echo "")

echo "=========================================================="
echo "📍 VERIFIED EGRESS IP: $IP"
echo "📍 LOCATION: $CITY, $COUNTRY 🇬🇧"
echo "📍 NETWORK/ISP: $ORG"
echo "=========================================================="

# HARD FAIL-SAFE KILL-SWITCH: Enforce United Kingdom (GB)
if [ "$COUNTRY" != "GB" ] && [ "$COUNTRY" != "UK" ]; then
    echo "❌ CRITICAL SECURITY ERROR: IP is NOT in United Kingdom! Detected: '$COUNTRY'"
    echo "🚨 HARD KILL-SWITCH ACTIVATED: Aborting process to prevent non-UK upload!"
    sudo wg-quick down wg0 || true
    exit 1
fi

echo "✅ VERIFIED: Connected successfully to London, United Kingdom 🇬🇧!"

if [ -n "$GITHUB_ENV" ]; then
    echo "RUNNER_GEO_JSON<<EOF" >> "$GITHUB_ENV"
    echo "$GEO" >> "$GITHUB_ENV"
    echo "EOF" >> "$GITHUB_ENV"
fi

