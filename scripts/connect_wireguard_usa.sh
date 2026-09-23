#!/usr/bin/env bash
set -e

TARGET_LOC="${1:-usa}"
TARGET_LOC_LOWER=$(echo "$TARGET_LOC" | tr '[:upper:]' '[:lower:]')

echo "=========================================================="
echo "🔒 INITIALIZING SURFSHARK USA WIREGUARD AUTO-DEFENSE TUNNEL"
echo "   Target Regional Profile: $TARGET_LOC"
echo "=========================================================="

sudo apt-get update -y -qq
sudo apt-get install -y -qq wireguard wireguard-tools resolvconf curl jq

sudo mkdir -p /etc/wireguard

# Map accounts and locations to dedicated Surfshark endpoints and verified public keys
# Meghal Chauhan (Los Angeles, California 90012)
# Mia Shah (New York, New York 10007)
# Radika Patel (New York, New York 11419)
if [[ "$TARGET_LOC_LOWER" == *"lax"* ]] || [[ "$TARGET_LOC_LOWER" == *"los_angeles"* ]] || [[ "$TARGET_LOC_LOWER" == *"los angeles"* ]] || [[ "$TARGET_LOC_LOWER" == *"meghal"* ]] || [[ "$TARGET_LOC_LOWER" == *"california"* ]] || [[ "$TARGET_LOC_LOWER" == *"90012"* ]] || [[ "$TARGET_LOC_LOWER" == *"account_1"* ]] || [[ "$TARGET_LOC_LOWER" == *"usa1"* ]]; then
    TARGET_ENDPOINT="us-lax.prod.surfshark.com:51820"
    TARGET_PUBKEY="m+L7BVQWDwU2TxjfspMRLkRctvmo7fOkd+eVk6KC5lM="
    TARGET_REGION_DESC="Los Angeles, California (90012) [Account 1 - Meghal Chauhan]"
    TARGET_CITY="Los Angeles"
elif [[ "$TARGET_LOC_LOWER" == *"mia"* ]] || [[ "$TARGET_LOC_LOWER" == *"10007"* ]] || [[ "$TARGET_LOC_LOWER" == *"account_2"* ]] || [[ "$TARGET_LOC_LOWER" == *"usa2"* ]]; then
    TARGET_ENDPOINT="us-nyc.prod.surfshark.com:51820"
    TARGET_PUBKEY="rhuoCmHdyYrh0zW3J0YXZK4aN3It7DD26TXlACuWnwU="
    TARGET_REGION_DESC="New York, New York (10007) [Account 2 - Mia Shah]"
    TARGET_CITY="New York"
elif [[ "$TARGET_LOC_LOWER" == *"radika"* ]] || [[ "$TARGET_LOC_LOWER" == *"11419"* ]] || [[ "$TARGET_LOC_LOWER" == *"account_3"* ]] || [[ "$TARGET_LOC_LOWER" == *"usa3"* ]]; then
    TARGET_ENDPOINT="us-nyc.prod.surfshark.com:51820"
    TARGET_PUBKEY="rhuoCmHdyYrh0zW3J0YXZK4aN3It7DD26TXlACuWnwU="
    TARGET_REGION_DESC="New York, New York (11419) [Account 3 - Radika Patel]"
    TARGET_CITY="New York"
else
    # Default fallback to New York
    TARGET_ENDPOINT="us-nyc.prod.surfshark.com:51820"
    TARGET_PUBKEY="rhuoCmHdyYrh0zW3J0YXZK4aN3It7DD26TXlACuWnwU="
    TARGET_REGION_DESC="United States (US East Metro Gateway)"
    TARGET_CITY=""
fi

MAX_ATTEMPTS=4
ATTEMPT=1
CONNECT_SUCCESS=false

while [ $ATTEMPT -le $MAX_ATTEMPTS ]; do
    echo "----------------------------------------------------------"
    echo "📡 Attempt $ATTEMPT of $MAX_ATTEMPTS: Connecting to $TARGET_ENDPOINT"
    echo "   Profile Intent: $TARGET_REGION_DESC"
    echo "----------------------------------------------------------"

    # Clean existing tunnel if up
    sudo wg-quick down wg0 2>/dev/null || true
    sleep 1

    cat << EOF | sudo tee /etc/wireguard/wg0.conf > /dev/null
[Interface]
Address = 10.14.0.2/16
PrivateKey = sLFzckN6irubqb0Qm5E7xzSGnyDHOeFiP3orSn6E6nU=
DNS = 162.252.172.57, 149.154.159.92

[Peer]
PublicKey = $TARGET_PUBKEY
AllowedIPs = 0.0.0.0/0
Endpoint = $TARGET_ENDPOINT
PersistentKeepalive = 25
EOF

    sudo chmod 600 /etc/wireguard/wg0.conf

    echo "Bringing up WireGuard wg0..."
    if ! sudo wg-quick up wg0; then
        echo "⚠️ Failed to start WireGuard on $TARGET_ENDPOINT, retrying..."
        ATTEMPT=$((ATTEMPT + 1))
        sleep 2
        continue
    fi

    echo "Waiting for tunnel handshake..."
    sleep 3

    # Check Egress Telemetry
    GEO=$(curl -s --max-time 8 https://ipinfo.io/json || curl -s --max-time 8 https://ipapi.co/json || echo "{}")
    COUNTRY=$(echo "$GEO" | python3 -c "import sys, json; print(json.load(sys.stdin).get('country', ''))" 2>/dev/null || echo "")
    CITY=$(echo "$GEO" | python3 -c "import sys, json; print(json.load(sys.stdin).get('city', ''))" 2>/dev/null || echo "")
    IP=$(echo "$GEO" | python3 -c "import sys, json; print(json.load(sys.stdin).get('ip', ''))" 2>/dev/null || echo "")
    ORG=$(echo "$GEO" | python3 -c "import sys, json; print(json.load(sys.stdin).get('org', ''))" 2>/dev/null || echo "")

    echo "📍 Connected Egress IP: $IP"
    echo "📍 Detected Geo:        $CITY, $COUNTRY 🇺🇸"
    echo "📍 Network/ISP:         $ORG"

    # Enforce Country USA
    if [ "$COUNTRY" != "US" ] && [ "$COUNTRY" != "USA" ]; then
        echo "❌ Country mismatch: '$COUNTRY' is not US. Dropping tunnel..."
        sudo wg-quick down wg0 || true
        ATTEMPT=$((ATTEMPT + 1))
        sleep 2
        continue
    fi

    # PRE-FLIGHT DIRTY IP & META HEALTH AUDIT
    echo "🛡️ Executing Pre-Flight IP Health & Dirty Blacklist Audit for USA..."
    if python3 scripts/verify_ip_health.py --require-country US; then
        echo "=========================================================="
        echo "🎉 IP HEALTH CONFIRMED CLEAN! US IP $IP IS 100% SAFE."
        echo "=========================================================="
        CONNECT_SUCCESS=true
        break
    else
        echo "🚨 DIRTY / FLAGGED US IP DETECTED ($IP)! AUTO-ROTATING..."
        sudo wg-quick down wg0 || true
        ATTEMPT=$((ATTEMPT + 1))
        sleep 3
    fi
done

if [ "$CONNECT_SUCCESS" = false ]; then
    echo "❌ CRITICAL SECURITY ERROR: All USA connection attempts failed IP health audit!"
    echo "🚨 Aborting pipeline to protect USA Facebook accounts from flagged IPs."
    exit 1
fi

echo "✅ VERIFIED: Connected successfully to 100% Clean US IP ($IP) for $TARGET_LOC!"

if [ -n "$GITHUB_ENV" ]; then
    echo "RUNNER_GEO_JSON<<EOF" >> "$GITHUB_ENV"
    echo "$GEO" >> "$GITHUB_ENV"
    echo "EOF" >> "$GITHUB_ENV"
fi
