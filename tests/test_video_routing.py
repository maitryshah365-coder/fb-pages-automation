import pytest
from src.video_utils import determine_post_route

def test_reels_routing_standard_vertical():
    # 9:16 aspect ratio (1080x1920), 45 seconds -> Reel
    video_info = {
        "width": 1080,
        "height": 1920,
        "aspect_ratio": 1080 / 1920,
        "aspect_ratio_str": "1080x1920",
        "is_vertical": True,
        "duration_seconds": 45.0
    }
    assert determine_post_route(video_info) == "reel"

def test_classic_routing_duration_exceeds_90s():
    # 9:16 aspect ratio (1080x1920), 95 seconds -> Classic Video
    video_info = {
        "width": 1080,
        "height": 1920,
        "aspect_ratio": 1080 / 1920,
        "aspect_ratio_str": "1080x1920",
        "is_vertical": True,
        "duration_seconds": 95.0
    }
    assert determine_post_route(video_info) == "classic_video"

def test_classic_routing_long_form_video():
    # 5-7 minute video (360 seconds) -> Classic Video
    video_info = {
        "width": 1080,
        "height": 1920,
        "aspect_ratio": 1080 / 1920,
        "aspect_ratio_str": "1080x1920",
        "is_vertical": True,
        "duration_seconds": 360.0
    }
    assert determine_post_route(video_info) == "classic_video"

def test_classic_routing_landscape_aspect_ratio():
    # 16:9 horizontal video (1920x1080), 30 seconds -> Classic Video
    video_info = {
        "width": 1920,
        "height": 1080,
        "aspect_ratio": 1920 / 1080,
        "aspect_ratio_str": "1920x1080",
        "is_vertical": False,
        "duration_seconds": 30.0
    }
    assert determine_post_route(video_info) == "classic_video"

def test_classic_routing_under_3_seconds():
    # Vertical but only 2 seconds -> Classic Video
    video_info = {
        "width": 1080,
        "height": 1920,
        "aspect_ratio": 1080 / 1920,
        "aspect_ratio_str": "1080x1920",
        "is_vertical": True,
        "duration_seconds": 2.0
    }
    assert determine_post_route(video_info) == "classic_video"
