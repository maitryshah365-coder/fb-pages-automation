"""
CLI Tool: Post Reel to Apex House via Samsung Galaxy S25 (New York Anti-Detect Profile)
"""

import sys
import os
import argparse

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from src.anti_detect.reels_uploader import AntiDetectReelsUploader


def main():
    parser = argparse.ArgumentParser(description="Post Reel via Samsung S25 Anti-Detect Engine")
    parser.add_argument("--video", required=False, help="Path to video file (.mp4)")
    parser.add_argument("--caption", default="#reels #viral #trending #fyp", help="Caption text for Reel")
    parser.add_argument("--dry-run", action="store_true", help="Perform dry run without clicking publish")
    parser.add_argument("--headed", action="store_true", help="Open visible browser window")
    args = parser.parse_args()

    uploader = AntiDetectReelsUploader()

    if not args.video:
        print("Usage: python scripts/post_s25_reel.py --video <path_to_video.mp4> [--caption '...'] [--dry-run] [--headed]")
        return

    res = uploader.upload_reel(
        video_path=args.video,
        caption=args.caption,
        headless=not args.headed,
        dry_run=args.dry_run
    )
    print("\nResult:", res)


if __name__ == "__main__":
    main()
