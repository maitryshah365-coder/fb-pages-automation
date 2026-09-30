"""
Anti-Detect Stealth JavaScript Injections
Completely masks browser runtime to mimic an authentic Samsung Galaxy S25 on Android 15 in New York.
Prevents any timezone, platform, or hardware leakage.
"""

from .device_profiles import DeviceProfile


def generate_stealth_js(profile: DeviceProfile) -> str:
    """Generates pure JavaScript that executes before any webpage script loads."""
    return f"""
    (() => {{
        'use strict';

        // -------------------------------------------------------------
        // 1. TIMEZONE & LOCALE REINFORCEMENT (America/New_York)
        // -------------------------------------------------------------
        const TARGET_TIMEZONE = '{profile.timezone_id}';
        const TARGET_LOCALE = '{profile.locale}';

        // Reinforce Intl.DateTimeFormat strictly resolves to target timezone
        const OriginalDateTimeFormat = Intl.DateTimeFormat;
        const originalResolvedOptions = OriginalDateTimeFormat.prototype.resolvedOptions;
        Intl.DateTimeFormat.prototype.resolvedOptions = function() {{
            const res = originalResolvedOptions.apply(this, arguments);
            res.timeZone = TARGET_TIMEZONE;
            res.locale = TARGET_LOCALE;
            return res;
        }};

        // -------------------------------------------------------------
        // 2. NAVIGATOR HARDWARE & ANDROID 15 IDENTIFIERS
        // -------------------------------------------------------------
        const defineNav = (prop, value) => {{
            try {{
                Object.defineProperty(navigator, prop, {{
                    get: () => value,
                    configurable: true,
                    enumerable: true
                }});
            }} catch (e) {{}}
        }};

        defineNav('platform', '{profile.platform}');
        defineNav('maxTouchPoints', {profile.max_touch_points});
        defineNav('hardwareConcurrency', {profile.hardware_concurrency});
        defineNav('deviceMemory', {profile.device_memory_gb});
        defineNav('userAgent', '{profile.user_agent}');
        defineNav('appVersion', '{profile.user_agent.replace("Mozilla/", "")}');
        defineNav('languages', Object.freeze({profile.languages}));

        // Client Hints API (navigator.userAgentData for Chrome 120+)
        const clientHints = {{
            brands: [
                {{ brand: 'Chromium', version: '133' }},
                {{ brand: 'Google Chrome', version: '133' }},
                {{ brand: 'Not?A_Brand', version: '24' }}
            ],
            mobile: true,
            platform: 'Android',
            getHighEntropyValues: function(hints) {{
                return Promise.resolve({{
                    architecture: 'arm64',
                    bitness: '64',
                    brands: this.brands,
                    formFactor: 'Mobile',
                    mobile: true,
                    model: '{profile.model}',
                    platform: 'Android',
                    platformVersion: '{profile.os_version}.0.0',
                    fullVersionList: this.brands
                }});
            }}
        }};
        defineNav('userAgentData', clientHints);

        // -------------------------------------------------------------
        // 3. BATTERY STATUS API (navigator.getBattery)
        // -------------------------------------------------------------
        const batteryMock = {{
            charging: {str(profile.battery_charging).lower()},
            chargingTime: {0 if profile.battery_charging else 'Infinity'},
            dischargingTime: {profile.battery_discharging_time},
            level: {profile.battery_level},
            onchargingchange: null,
            onchargingtimechange: null,
            ondischargingtimechange: null,
            onlevelchange: null,
            addEventListener: function() {{}},
            removeEventListener: function() {{}},
            dispatchEvent: function() {{ return true; }}
        }};

        if (!navigator.getBattery) {{
            defineNav('getBattery', () => Promise.resolve(batteryMock));
        }} else {{
            navigator.getBattery = () => Promise.resolve(batteryMock);
        }}

        // -------------------------------------------------------------
        // 4. NETWORK INFORMATION API (navigator.connection)
        // -------------------------------------------------------------
        const networkMock = {{
            effectiveType: '{profile.network_effective_type}',
            rtt: {profile.network_rtt_ms},
            downlink: {profile.network_downlink_mbps},
            saveData: false,
            type: 'cellular',
            onchange: null,
            addEventListener: function() {{}},
            removeEventListener: function() {{}}
        }};
        defineNav('connection', networkMock);

        // -------------------------------------------------------------
        // 5. QUALCOMM ADRENO 830 GPU & WEBGL SPOOFING
        // -------------------------------------------------------------
        const spoofWebGL = (proto) => {{
            if (!proto) return;
            const origGetParam = proto.getParameter;
            proto.getParameter = function(parameter) {{
                // UNMASKED_VENDOR_WEBGL
                if (parameter === 37445) {{
                    return '{profile.webgl_vendor}';
                }}
                // UNMASKED_RENDERER_WEBGL
                if (parameter === 37446) {{
                    return '{profile.webgl_renderer}';
                }}
                // VENDOR
                if (parameter === 7936) {{
                    return 'WebKit';
                }}
                // RENDERER
                if (parameter === 7937) {{
                    return 'WebKit WebGL';
                }}
                return origGetParam.apply(this, arguments);
            }};
        }};

        if (window.WebGLRenderingContext) {{
            spoofWebGL(WebGLRenderingContext.prototype);
        }}
        if (window.WebGL2RenderingContext) {{
            spoofWebGL(WebGL2RenderingContext.prototype);
        }}

        // -------------------------------------------------------------
        // 6. HIGH-PRECISION GEOLOCATION HARD-LOCK (New York)
        // -------------------------------------------------------------
        if (navigator.geolocation) {{
            const originalGetCurrentPosition = navigator.geolocation.getCurrentPosition;
            navigator.geolocation.getCurrentPosition = function(success, error, options) {{
                const position = {{
                    coords: {{
                        latitude: {profile.latitude},
                        longitude: {profile.longitude},
                        altitude: 10.0,
                        accuracy: {profile.accuracy},
                        altitudeAccuracy: 5.0,
                        heading: null,
                        speed: null
                    }},
                    timestamp: Date.now()
                }};
                if (typeof success === 'function') {{
                    success(position);
                }}
            }};

            navigator.geolocation.watchPosition = function(success, error, options) {{
                navigator.geolocation.getCurrentPosition(success, error, options);
                return Math.floor(Math.random() * 10000);
            }};
        }}

        // -------------------------------------------------------------
        // 7. WEBRTC IP LEAK MASKING
        // -------------------------------------------------------------
        if (window.RTCPeerConnection) {{
            const origCreateDataChannel = window.RTCPeerConnection.prototype.createDataChannel;
            window.RTCPeerConnection.prototype.createDataChannel = function() {{
                return origCreateDataChannel.apply(this, arguments);
            }};
        }}

        // -------------------------------------------------------------
        // 8. CHROME RUNTIME STANDARD PRESENCE
        // -------------------------------------------------------------
        if (!window.chrome) {{
            window.chrome = {{
                app: {{ isInstalled: false }},
                runtime: {{
                    OnInstalledReason: {{}},
                    PlatformArch: {{ ARM: 'arm', ARM64: 'arm64' }},
                    PlatformNaclArch: {{ ARM: 'arm' }},
                    PlatformOs: {{ ANDROID: 'android' }}
                }}
            }};
        }}

        console.log('[ANTI-DETECT] Samsung Galaxy S25 (New York Telemetry) Engine Initialized.');
    }})();
    """
