import os
import tempfile
import pytest
from src.db import DatabaseManager

@pytest.fixture
def temp_db():
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_videos.db")
    db = DatabaseManager(db_path)
    yield db
    if os.path.exists(db_path):
        os.remove(db_path)

def test_database_initialization(temp_db):
    assert not temp_db.is_already_posted("page_1", "drive_file_1")
    assert len(temp_db.get_posted_drive_file_ids("page_1")) == 0
    assert temp_db.get_today_upload_count("page_1") == 0

def test_record_selection_and_success(temp_db):
    page_id = "page_100"
    file_id = "drive_123"

    temp_db.record_selection(page_id, file_id, "test_video.mp4")
    assert not temp_db.is_already_posted(page_id, file_id)

    # Record successful post
    temp_db.record_success(
        page_id=page_id,
        drive_file_id=file_id,
        facebook_video_id="fb_vid_999",
        post_type="reel",
        duration_seconds=45.0,
        aspect_ratio="1080x1920"
    )

    # Now duplicate check must return True
    assert temp_db.is_already_posted(page_id, file_id)
    assert file_id in temp_db.get_posted_drive_file_ids(page_id)
    assert temp_db.get_today_upload_count(page_id) == 1

def test_daily_limit_counter(temp_db):
    page_id = "page_200"
    assert temp_db.get_today_upload_count(page_id) == 0

    temp_db.record_selection(page_id, "file_1", "video1.mp4")
    temp_db.record_success(page_id, "file_1", "fb_1", "reel")
    assert temp_db.get_today_upload_count(page_id) == 1

    temp_db.record_selection(page_id, "file_2", "video2.mp4")
    temp_db.record_success(page_id, "file_2", "fb_2", "reel")
    assert temp_db.get_today_upload_count(page_id) == 2

def test_record_failure_and_permanent_skip(temp_db):
    page_id = "page_300"
    file_id = "file_corrupt"

    temp_db.record_selection(page_id, file_id, "corrupt.mp4")
    temp_db.record_failure(page_id, file_id, "File corrupted", is_permanent=True)

    perm_failed = temp_db.get_permanently_failed_file_ids(page_id)
    assert file_id in perm_failed
    assert not temp_db.is_already_posted(page_id, file_id)
