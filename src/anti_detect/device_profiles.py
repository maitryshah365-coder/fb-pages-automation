"""
Device Profiles Catalog for Anti-Detect Browser Emulation
Defines authentic hardware configurations, screen viewports, and regional telemetry.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any


@dataclass
class DeviceProfile:
    profile_id: str
    device_name: str
    brand: str
    model: str
    os_name: str
    os_version: str
    user_agent: str
    platform: str
    viewport_width: int
    viewport_height: int
    device_scale_factor: float
    is_mobile: bool
    has_touch: bool
    max_touch_points: int
    hardware_concurrency: int
    device_memory_gb: int
    webgl_vendor: str
    webgl_renderer: str
    battery_level: float
    battery_charging: bool
    battery_discharging_time: int
    
    # Regional Telemetry & Geolocation
    timezone_id: str
    locale: str
    languages: List[str]
    latitude: float
    longitude: float
    accuracy: float
    
    # Network Connection API hints
    network_effective_type: str = "4g"
    network_downlink_mbps: float = 35.0
    network_rtt_ms: int = 35


# --------------------------------------------------------------------------
# Samsung Galaxy S25 (US Model SM-S931U) • New York Dedicated Profile
# --------------------------------------------------------------------------
S25_NEWYORK_PROFILE = DeviceProfile(
    profile_id="samsung_s25_newyork",
    device_name="Samsung Galaxy S25 (US 5G)",
    brand="Samsung",
    model="SM-S931U",
    os_name="Android",
    os_version="15",
    user_agent=(
        "Mozilla/5.0 (Linux; Android 15; SM-S931U) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/133.0.6943.126 Mobile Safari/537.36"
    ),
    platform="Linux armv8l",
    viewport_width=393,
    viewport_height=852,
    device_scale_factor=3.0,
    is_mobile=True,
    has_touch=True,
    max_touch_points=5,
    hardware_concurrency=8,        # Snapdragon 8 Elite 8-core
    device_memory_gb=12,           # 12 GB LPDDR5X RAM
    webgl_vendor="Qualcomm",
    webgl_renderer="Adreno (TM) 830",
    battery_level=0.88,            # 88% Battery
    battery_charging=False,
    battery_discharging_time=32400, # 9 hours
    
    # New York, USA Telemetry (Strict Anti-Leak)
    timezone_id="America/New_York",
    locale="en-US",
    languages=["en-US", "en"],
    latitude=40.7128,              # New York City Center
    longitude=-74.0060,            # New York City Center
    accuracy=12.0,                 # High-accuracy GPS lock in meters
    
    network_effective_type="4g",
    network_downlink_mbps=45.0,
    network_rtt_ms=30
)
