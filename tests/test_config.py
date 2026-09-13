import os
import pytest
from src.config import load_config, PageConfig

def test_load_config():
    config = load_config("config.yaml")
    assert config.page_group == "personal_fb_id_1"
    assert len(config.pages) == 6
    assert config.retry.max_attempts == 3

    page1 = config.pages[0]
    assert page1.name == "page_1"
    assert page1.token_env_var == "FB_TOKEN_PAGE_1"
    assert page1.daily_limit == 2

def test_page_token_resolution(monkeypatch):
    p = PageConfig(
        page_id="12345",
        name="test_page",
        drive_folder_id="folder_abc"
    )
    assert p.token_env_var == "FB_TOKEN_TEST_PAGE"

    # When no token set in environment
    assert p.get_access_token() is None

    # When set in environment
    monkeypatch.setenv("FB_TOKEN_TEST_PAGE", "token_xyz")
    assert p.get_access_token() == "token_xyz"
