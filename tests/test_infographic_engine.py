import os
import sys
import unittest
from PIL import Image

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.infographic_db import InfographicDB
from src.infographic_scheduler import InfographicScheduler
from src.infographic_engine import InfographicEngine, AUTHENTIC_VERTICAL_DATA, TEMPLATE_STYLES, PALETTE_THEMES

class TestInfographicAutomationEngine(unittest.TestCase):

    def setUp(self):
        self.test_db_path = "temp/test_infographics.db"
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        self.db = InfographicDB(self.test_db_path)
        self.engine = InfographicEngine(cache_dir="temp/test_cache")

    def tearDown(self):
        if os.path.exists(self.test_db_path):
            try:
                os.remove(self.test_db_path)
            except Exception:
                pass

    def test_deduplication_and_infinite_rotation(self):
        """Audit Check: Verifies that duplicate topic+angle combinations are rejected."""
        page_id = "test_page_101"
        slug = "bengal_tiger"
        angle = "anatomical_pointer:midnight_cyan"

        # Initially unposted
        self.assertFalse(self.db.is_topic_angle_posted(page_id, slug, angle))

        # Record upload
        self.db.record_upload(
            page_id=page_id,
            vertical_key="wildlife_apex_predators",
            topic_slug=slug,
            angle_mode=angle,
            title="Bengal Tiger Guide",
            hashtags="#tiger #wildlife",
            image_path="temp/dummy.png",
            fb_photo_id="12345",
            status="posted"
        )

        # Now detected as posted
        self.assertTrue(self.db.is_topic_angle_posted(page_id, slug, angle))

        # Other angle for same topic must be free
        self.assertFalse(self.db.is_topic_angle_posted(page_id, slug, "bento_dashboard:obsidian_amber"))

    def test_dynamic_style_and_theme_rotation(self):
        """Audit Check: Verifies that subsequent runs for a page rotate through templates and themes."""
        page_id = "test_page_rotate_99"
        topic_pool = AUTHENTIC_VERTICAL_DATA["miniature_diorama_disaster"]["topics"]
        templates = TEMPLATE_STYLES
        palettes = list(PALETTE_THEMES.keys())

        # First selection
        plan1 = self.db.get_next_rotation_plan(page_id, topic_pool, templates, palettes)
        self.assertIn(plan1["template"], templates)
        self.assertIn(plan1["theme"], palettes)

        # Record first upload
        self.db.record_upload(
            page_id=page_id,
            vertical_key="miniature_diorama_disaster",
            topic_slug=plan1["topic"]["slug"],
            angle_mode=plan1["angle_mode"],
            title=plan1["topic"]["title"],
            hashtags="#miniatures",
            image_path="temp/dummy1.png",
            fb_photo_id="111",
            status="posted"
        )

        # Second selection must be a DIFFERENT template
        plan2 = self.db.get_next_rotation_plan(page_id, topic_pool, templates, palettes)
        self.assertNotEqual(plan1["template"], plan2["template"], "Template failed to rotate!")

    def test_staggered_scheduler_anti_collision(self):
        """Audit Check: Verifies 6-times daily slots with perfect collision-free distribution."""
        res = InfographicScheduler.verify_no_collisions(total_pages=171)
        self.assertEqual(res["status"], "perfect_stagger")
        self.assertEqual(res["slots_verified"], 6)

        # Test video cron avoidance: Check that minute is never :00, :20, :40
        for p_idx in range(50):
            sched = InfographicScheduler.calculate_page_slot_time(p_idx, slot_index=0)
            minute = sched["scheduled_minute"]
            self.assertNotIn(minute, [0, 20, 40], f"Page {p_idx} collided with video cron minute {minute}")

    def test_all_five_templates_render_successfully(self):
        """Audit Check: Verifies that all 5 distinct design archetypes render to 1080x1350 RGB."""
        topic = AUTHENTIC_VERTICAL_DATA["miniature_diorama_disaster"]["topics"][0]

        for template in TEMPLATE_STYLES:
            out_path = f"temp/test_render_{template}.png"
            res = self.engine.render_infographic(
                page_name="Mix Mood",
                vertical_key="miniature_diorama_disaster",
                topic=topic,
                output_path=out_path,
                template_name=template,
                theme_name="obsidian_amber"
            )
            self.assertTrue(os.path.exists(out_path), f"Failed to render template {template}")
            with Image.open(out_path) as im:
                self.assertEqual(im.size, (1080, 1350))
                self.assertEqual(im.mode, "RGB")
            if os.path.exists(out_path):
                os.remove(out_path)

    def test_all_13_verticals_populated(self):
        """Audit Check: Verifies that all 13 fleet content verticals exist with authentic topics."""
        self.assertGreaterEqual(len(AUTHENTIC_VERTICAL_DATA), 13)
        for v_key, v_data in AUTHENTIC_VERTICAL_DATA.items():
            self.assertTrue("topics" in v_data, f"Vertical {v_key} missing topics")
            self.assertGreaterEqual(len(v_data["topics"]), 1, f"Vertical {v_key} has empty topics")
            t0 = v_data["topics"][0]
            self.assertTrue("title" in t0)
            self.assertTrue("slug" in t0)

if __name__ == "__main__":
    unittest.main()
