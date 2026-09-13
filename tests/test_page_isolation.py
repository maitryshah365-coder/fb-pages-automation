import os
import tempfile
import pytest
from unittest.mock import MagicMock
from src.config import PageConfig, AppConfig, RetryConfig, NotificationConfig
from src.db import DatabaseManager
from src.page_runner import PageRunner

@pytest.fixture
def mock_app():
    temp_dir = tempfile.mkdtemp()
    db = DatabaseManager(os.path.join(temp_dir, "test.db"))

    page1 = PageConfig(page_id="p1", name="page_fail", drive_folder_id="f1", daily_limit=2)
    page2 = PageConfig(page_id="p2", name="page_success", drive_folder_id="f2", daily_limit=2)

    config = AppConfig(
        page_group="test_group",
        ai_disclosure_status="pending",
        database_path=db.db_path,
        retry=RetryConfig(),
        notifications=NotificationConfig(),
        pages=[page1, page2]
    )

    drive_client = MagicMock()
    # f1 raises exception
    # f2 succeeds with a video
    def list_folder_side_effect(folder_id):
        if folder_id == "f1":
            raise RuntimeError("Folder 1 Drive Error")
        return [{"id": "vid_2", "name": "reel2.mp4", "mimeType": "video/mp4"}]

    drive_client.list_folder_videos.side_effect = list_folder_side_effect
    drive_client.select_next_video.side_effect = lambda f, p, pf: None if f == "f1" else {"id": "vid_2", "name": "reel2.mp4", "mimeType": "video/mp4"}

    notifier = MagicMock()

    runner = PageRunner(
        config=config,
        db=db,
        drive_client=drive_client,
        notifier=notifier,
        dry_run=True  # Dry run to verify isolation without live FB network
    )

    return runner, page1, page2

def test_page_isolation_guarantee(mock_app):
    runner, page1, page2 = mock_app

    # Execute page 1 -> fails
    res1 = runner.run_page(page1)
    assert res1["status"] == "failed"
    assert "Folder 1 Drive Error" in res1["error"]

    # Execute page 2 -> must still execute successfully despite page 1 failure!
    res2 = runner.run_page(page2)
    assert res2["status"] == "dry_run_success"
    assert res2["file"] == "reel2.mp4"
