#!/usr/bin/env bash
set -e

TARGET_LOC="${1:-london}"
TARGET_LOC_LOWER=$(echo "$TARGET_LOC" | tr '[:upper:]' '[:lower:]')

echo "=========================================================="
echo "🔒 INITIALIZING SURFSHARK UK WIREGUARD TUNNEL"
echo "   Target Account Profile: $TARGET_LOC"
echo "=========================================================="

sudo apt-get update -y -qq
sudo apt-get install -y -qq wireguard wireguard-tools resolvconf curl jq

sudo mkdir -p /etc/wireguard

# Smart Regional Endpoint Selection:
# Sweta Shah is Newport, Wales (NP20 6) -> Route through UK West / Manchester gateway
# London accounts (Binjal, Chanda, Mahi, Nidhi, Richi, Riya) -> Route through London gateway
if [[ "$TARGET_LOC_LOWER" == *"sweta"* ]] || [[ "$TARGET_LOC_LOWER" == *"wales"* ]] || [[ "$TARGET_LOC_LOWER" == *"newport"* ]] || [[ "$TARGET_LOC_LOWER" == *"uk6"* ]] || [[ "$TARGET_LOC_LOWER" == *"np20"* ]]; then
    WG_ENDPOINT="uk-man.prod.surfshark.com:51820"
    TARGET_REGION_DESC="Newport, Wales (NP20 6) [West UK Regional Gateway]"
else
    WG_ENDPOINT="uk-lon.prod.surfshark.com:51820"
    TARGET_REGION_DESC="London, England [Metro Gateway]"
fi

echo "Connecting WireGuard wg0 tunnel to $TARGET_REGION_DESC ($WG_ENDPOINT)..."

cat << EOF | sudo tee /etc/wireguard/wg0.conf > /dev/null
[Interface]
Address = 10.14.0.2/16
PrivateKey = sLFzckN6irubqb0Qm5E7xzSGnyDHOeFiP3orSn6E6nU=
DNS = 162.252.172.57, 149.154.159.92

[Peer]
PublicKey = iBJRXLZwXuWWrOZE1ZrAXEKMgV/z0WjG0Tks5rnWLBI=
AllowedIPs = 0.0.0.0/0
Endpoint = $WG_ENDPOINT
PersistentKeepalive = 25
EOF

sudo chmod 600 /etc/wireguard/wg0.conf

echo "Starting WireGuard tunnel..."
sudo wg-quick up wg0

echo "Waiting for tunnel handshake..."
sleep 3

# Resolve Telemetry
GEO=$(curl -s --max-time 10 https://ipinfo.io/json || curl -s --max-time 10 https://ipapi.co/json || echo "{}")
COUNTRY=$(echo "$GEO" | python3 -c "import sys, json; print(json.load(sys.stdin).get('country', ''))" 2>/dev/null || echo "")
CITY=$(echo "$GEO" | python3 -c "import sys, json; print(json.load(sys.stdin).get('city', ''))" 2>/dev/null || echo "")
IP=$(echo "$GEO" | python3 -c "import sys, json; print(json.load(sys.stdin).get('ip', ''))" 2>/dev/null || echo "")
ORG=$(echo "$GEO" | python3 -c "import sys, json; print(json.load(sys.stdin).get('org', ''))" 2>/dev/null || echo "")

echo "=========================================================="
echo "📍 VERIFIED EGRESS IP: $IP"
echo "📍 LOCATION:          $CITY, $COUNTRY 🇬🇧"
echo "📍 TARGET INTENT:     $TARGET_REGION_DESC"
echo "📍 NETWORK/ISP:       $ORG"
echo "=========================================================="

# HARD FAIL-SAFE KILL-SWITCH: Enforce United Kingdom (GB)
if [ "$COUNTRY" != "GB" ] && [ "$COUNTRY" != "UK" ]; then
    echo "❌ CRITICAL SECURITY ERROR: IP is NOT in United Kingdom! Detected: '$COUNTRY'"
    echo "🚨 HARD KILL-SWITCH ACTIVATED: Aborting process to prevent non-UK upload!"
    sudo wg-quick down wg0 || true
    exit 1
fi

# PRE-FLIGHT IP HEALTH & META REPUTATION AUDIT
echo "🛡️ Running Pre-Flight IP Health & Blacklist Check..."
if python3 scripts/verify_ip_health.py --require-country GB; then
    echo "✅ PRE-FLIGHT AUDIT PASSED: IP $IP is 100% Clean & Healthy!"
else
    echo "🚨 PRE-FLIGHT AUDIT FAILED: IP $IP was flagged as Dirty or Failed Meta Check!"
    echo "🔄 Disconnecting and switching to alternate UK endpoint..."
    sudo wg-quick down wg0 || true
    sleep 2

    # Alternate endpoint failover
    if [ "$WG_ENDPOINT" = "uk-lon.prod.surfshark.com:51820" ]; then
        ALT_ENDPOINT="uk-man.prod.surfshark.com:51820"
    else
        ALT_ENDPOINT="uk-lon.prod.surfshark.com:51820"
    fi

    echo "Connecting to alternate endpoint: $ALT_ENDPOINT"
    sudo sed -i "s|Endpoint = .*|Endpoint = $ALT_ENDPOINT|g" /etc/wireguard/wg0.conf
    sudo wg-quick up wg0
    sleep 3
    python3 scripts/verify_ip_health.py --require-country GB
fi

echo "✅ VERIFIED: Connected successfully to United Kingdom 🇬🇧 for $TARGET_LOC!"

if [ -n "$GITHUB_ENV" ]; then
    echo "RUNNER_GEO_JSON<<EOF" >> "$GITHUB_ENV"
    echo "$GEO" >> "$GITHUB_ENV"
    echo "EOF" >> "$GITHUB_ENV"
fi
