#!/usr/bin/env bash
set -e

TARGET_LOC="${1:-london}"
TARGET_LOC_LOWER=$(echo "$TARGET_LOC" | tr '[:upper:]' '[:lower:]')

echo "=========================================================="
echo "🔒 INITIALIZING SURFSHARK UK WIREGUARD AUTO-DEFENSE TUNNEL"
echo "   Target Account Profile: $TARGET_LOC"
echo "=========================================================="

sudo apt-get update -y -qq
sudo apt-get install -y -qq wireguard wireguard-tools resolvconf curl jq

sudo mkdir -p /etc/wireguard

# Build Priority Endpoint Pool based on target location:
# Sweta Shah (Newport, Wales NP20 6) prioritizes West UK (Manchester) then Glasgow then London
# London accounts prioritize London then Manchester then Glasgow
if [[ "$TARGET_LOC_LOWER" == *"sweta"* ]] || [[ "$TARGET_LOC_LOWER" == *"wales"* ]] || [[ "$TARGET_LOC_LOWER" == *"newport"* ]] || [[ "$TARGET_LOC_LOWER" == *"uk6"* ]] || [[ "$TARGET_LOC_LOWER" == *"np20"* ]]; then
    POOL=("uk-man.prod.surfshark.com:51820" "uk-gla.prod.surfshark.com:51820" "uk-lon.prod.surfshark.com:51820")
    TARGET_REGION_DESC="Newport, Wales (NP20 6) [West UK Regional Gateway]"
else
    POOL=("uk-lon.prod.surfshark.com:51820" "uk-man.prod.surfshark.com:51820" "uk-gla.prod.surfshark.com:51820")
    TARGET_REGION_DESC="London, England [Metro Gateway]"
fi

CONNECT_SUCCESS=false

for ENDPOINT in "${POOL[@]}"; do
    echo "----------------------------------------------------------"
    echo "📡 Attempting WireGuard connection to: $ENDPOINT"
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
PublicKey = iBJRXLZwXuWWrOZE1ZrAXEKMgV/z0WjG0Tks5rnWLBI=
AllowedIPs = 0.0.0.0/0
Endpoint = $ENDPOINT
PersistentKeepalive = 25
EOF

    sudo chmod 600 /etc/wireguard/wg0.conf

    echo "Bringing up WireGuard wg0..."
    if ! sudo wg-quick up wg0; then
        echo "⚠️ Failed to start WireGuard on $ENDPOINT, trying next pool node..."
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
    echo "📍 Detected Geo:        $CITY, $COUNTRY 🇬🇧"
    echo "📍 Network/ISP:         $ORG"

    # Enforce Country UK
    if [ "$COUNTRY" != "GB" ] && [ "$COUNTRY" != "UK" ]; then
        echo "❌ Country mismatch: '$COUNTRY' is not UK. Dropping tunnel..."
        sudo wg-quick down wg0 || true
        continue
    fi

    # PRE-FLIGHT DIRTY IP & META HEALTH AUDIT
    echo "🛡️ Executing Pre-Flight IP Health & Dirty Blacklist Audit..."
    if python3 scripts/verify_ip_health.py --require-country GB; then
        echo "=========================================================="
        echo "🎉 IP HEALTH CONFIRMED CLEAN! IP $IP IS 100% UNFLAGGED & SAFE."
        echo "=========================================================="
        CONNECT_SUCCESS=true
        break
    else
        echo "🚨 DIRTY / FLAGGED IP DETECTED ($IP)! AUTO-ROTATING TO NEXT SERVER..."
        sudo wg-quick down wg0 || true
        sleep 2
    fi
done

if [ "$CONNECT_SUCCESS" = false ]; then
    echo "❌ CRITICAL SECURITY ERROR: All UK server endpoints failed IP health check!"
    echo "🚨 Aborting pipeline to protect Facebook accounts from flagged IPs."
    exit 1
fi

echo "✅ VERIFIED: Connected successfully to 100% Clean UK IP ($IP) for $TARGET_LOC!"

if [ -n "$GITHUB_ENV" ]; then
    echo "RUNNER_GEO_JSON<<EOF" >> "$GITHUB_ENV"
    echo "$GEO" >> "$GITHUB_ENV"
    echo "EOF" >> "$GITHUB_ENV"
fi
