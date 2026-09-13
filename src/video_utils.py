import os
import subprocess
import json
import struct
import logging
from typing import Dict, Any, Tuple

logger = logging.getLogger("fb_automation")


def _probe_via_ffprobe(file_path: str) -> Tuple[int, int, float]:
    """Uses ffprobe to extract video width, height, and duration."""
    cmd = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height,duration:format=duration",
        "-of", "json",
        file_path
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
    data = json.loads(result.stdout)
    streams = data.get("streams", [])
    if not streams:
        raise ValueError("No video stream found in file.")

    width = int(streams[0].get("width", 0))
    height = int(streams[0].get("height", 0))
    duration_str = streams[0].get("duration") or data.get("format", {}).get("duration")
    duration = float(duration_str) if duration_str else 0.0

    return width, height, duration


def _probe_via_mp4_atoms(file_path: str) -> Tuple[int, int, float]:
    """Fallback pure-Python parser for MP4 'mvhd' atom to get duration and 'tkhd' for width/height."""
    width, height, duration = 0, 0, 0.0
    with open(file_path, "rb") as f:
        while True:
            header = f.read(8)
            if len(header) < 8:
                break
            atom_size, atom_type = struct.unpack(">I4s", header)
            if atom_size == 1:
                atom_size = struct.unpack(">Q", f.read(8))[0]
                data_size = atom_size - 16
            else:
                data_size = atom_size - 8

            if atom_type == b"moov":
                # Search inside moov container
                moov_bytes = f.read(data_size)
                # Find mvhd
                mvhd_idx = moov_bytes.find(b"mvhd")
                if mvhd_idx != -1:
                    # mvhd header is 4 bytes version/flags, then created/modified time, timescale, duration
                    version = moov_bytes[mvhd_idx + 4]
                    offset = mvhd_idx + 8
                    if version == 1:
                        # 64-bit creation (8), mod (8), timescale (4), duration (8)
                        offset += 16
                        timescale, dur = struct.unpack(">IQ", moov_bytes[offset:offset + 12])
                    else:
                        # 32-bit creation (4), mod (4), timescale (4), duration (4)
                        offset += 8
                        timescale, dur = struct.unpack(">II", moov_bytes[offset:offset + 8])
                    if timescale > 0:
                        duration = dur / timescale

                # Find tkhd for video track dimensions
                tkhd_idx = moov_bytes.find(b"tkhd")
                if tkhd_idx != -1:
                    # width and height are 16.16 fixed point numbers at the end of tkhd
                    # tkhd version 0 is 84 bytes + 8 header = 92 bytes, version 1 is 96 bytes + 8 = 104
                    v = moov_bytes[tkhd_idx + 4]
                    tkhd_len = 104 if v == 1 else 92
                    tkhd_data = moov_bytes[tkhd_idx:tkhd_idx + tkhd_len]
                    if len(tkhd_data) >= 8:
                        w_fixed, h_fixed = struct.unpack(">II", tkhd_data[-8:])
                        width = w_fixed >> 16
                        height = h_fixed >> 16
                break
            else:
                f.seek(data_size, 1)

    return width, height, duration


def inspect_video(file_path: str) -> Dict[str, Any]:
    """
    Measures video width, height, aspect ratio, and duration in seconds.
    Tries ffprobe first, falling back to pure-Python MP4 parsing.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Video file does not exist: {file_path}")

    width, height, duration = 0, 0, 0.0
    try:
        width, height, duration = _probe_via_ffprobe(file_path)
    except Exception as e:
        logger.debug(f"ffprobe unavailable or failed ({e}), falling back to MP4 atom probe.")
        try:
            width, height, duration = _probe_via_mp4_atoms(file_path)
        except Exception as inner_e:
            logger.warning(f"Could not probe video dimensions or duration: {inner_e}")

    aspect_ratio_val = (width / height) if (width > 0 and height > 0) else 0.0
    is_vertical = 0.45 <= aspect_ratio_val <= 0.65 if aspect_ratio_val > 0 else False
    aspect_str = f"{width}x{height}" if width > 0 else "unknown"

    return {
        "file_path": file_path,
        "width": width,
        "height": height,
        "aspect_ratio": aspect_ratio_val,
        "aspect_ratio_str": aspect_str,
        "is_vertical": is_vertical,
        "duration_seconds": duration
    }


def determine_post_route(video_info: Dict[str, Any]) -> str:
    """
    Determines whether the video should be published as a Facebook Reel or Classic Video.
    Rule (Section 9):
    - Reel: 9:16 (vertical), 3 to 90 seconds duration.
    - Classic: > 90 seconds, or non-vertical (horizontal/landscape), or failed Reel parameters.
    """
    duration = video_info.get("duration_seconds", 0.0)
    is_vertical = video_info.get("is_vertical", False)

    # If duration is strictly > 90s, Facebook Reels API will reject it
    if duration > 90.0:
        logger.info(
            f"Routing to CLASSIC VIDEO: Duration {duration:.1f}s exceeds Reels 90s limit."
        )
        return "classic_video"

    # If aspect ratio is not vertical (9:16)
    if not is_vertical and video_info.get("width", 0) > 0:
        logger.info(
            f"Routing to CLASSIC VIDEO: Aspect ratio is not 9:16 ({video_info.get('aspect_ratio_str')})."
        )
        return "classic_video"

    # If duration is too short (< 3s)
    if 0.0 < duration < 3.0:
        logger.info(
            f"Routing to CLASSIC VIDEO: Duration {duration:.1f}s is under Reels 3s minimum."
        )
        return "classic_video"

    # Default to Reels for short vertical video
    logger.info(f"Routing to REELS: Duration {duration:.1f}s, vertical format.")
    return "reel"
