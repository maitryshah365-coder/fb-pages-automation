import asyncio
from playwright.async_api import async_playwright
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

ARTIFACTS_DIR = r"C:\Users\Win\.gemini\antigravity-ide\brain\313a3f26-ac39-434f-8050-53be5bd48383"

async def verify_dashboard():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1440, "height": 900})
        
        print("1. Loading http://localhost:8888/ ...")
        await page.goto("http://localhost:8888/", wait_until="networkidle")
        await asyncio.sleep(2)

        # Check filter tabs
        filter_tabs = await page.query_selector_all(".sidebar-filter-btn")
        print(f"Sidebar filter tabs count: {len(filter_tabs)}")
        assert len(filter_tabs) == 3, "Expected 3 filter tabs"

        # Check that no external FB links exist
        fb_links = await page.query_selector_all("a[href*='facebook.com']")
        print(f"External Facebook links found: {len(fb_links)}")
        assert len(fb_links) == 0, "No external Facebook links should exist!"

        # Check that toggle tabs (Option 1 / Option 2) do NOT exist
        mode_tabs = await page.query_selector(".monetize-mode-tabs")
        assert mode_tabs is None, "Option 1 / Option 2 switchable tabs MUST NOT exist!"

        # 2. Click Criteria filter tab
        print("\n2. Testing Filter: 🎯 Criteria (8)...")
        await page.click("#filterCriteriaPages")
        await asyncio.sleep(1)
        criteria_items = await page.query_selector_all(".page-list-item[data-page-id]")
        print(f"Filtered criteria pages count: {len(criteria_items)}")
        assert len(criteria_items) == 8, f"Expected 8 criteria pages, got {len(criteria_items)}"

        # 3. Select Fresh Hive Network (Criteria Area Page)
        print("\n3. Testing Criteria Page: Fresh Hive Network...")
        # Find Fresh Hive Network item and click
        fresh_item = await page.query_selector(".page-list-item[data-page-name*='fresh']")
        assert fresh_item is not None, "Fresh Hive Network not found in sidebar"
        await fresh_item.click()
        await asyncio.sleep(1.5)

        # Verify Box C shows Criteria Area ONLY
        badge_text = await page.inner_text("#badgeMonetizeAuto")
        print(f"Monetization Badge: {badge_text}")
        assert "criteria area" in badge_text.lower(), "Should have Criteria Area badge"

        waitlist_title = await page.inner_text(".waitlist-title")
        print(f"Waitlist Title: {waitlist_title}")
        assert "4 of 6 criteria met" in waitlist_title.lower(), "Should show 4 of 6 criteria met"

        # Verify 6 eligibility cards exist
        eligibility_cards = await page.query_selector_all(".eligibility-card-fb")
        print(f"Eligibility cards count: {len(eligibility_cards)}")
        assert len(eligibility_cards) == 6, "Expected 6 eligibility cards"

        # Verify How it works card exists
        how_works = await page.query_selector(".how-it-works-card")
        assert how_works is not None, "How content monetization works card must be visible"

        # Verify Invite-Only Overview is NOT present
        overview_card = await page.query_selector(".monetize-overview-card")
        assert overview_card is None, "Invite-Only Overview must NOT be visible on Criteria Page!"

        # Test Discovery & Views tab in Box B
        print("\n4. Testing Box B: Discovery & Views tab...")
        await page.click("button.aud-tab-btn[data-tab='discovery']")
        await asyncio.sleep(1)

        discovery_tile = await page.query_selector(".discovery-tile")
        assert discovery_tile is not None, "Discovery insights should be rendered"
        donut_text = await page.inner_text(".donut-inner-hole")
        print(f"Donut Center Value: {donut_text}")
        assert "97.8%" in donut_text, "Donut center should show 97.8% non-followers"

        # Capture Screenshot 1: Fresh Hive Network (Criteria Area & Discovery tab)
        fresh_screen_path = os.path.join(ARTIFACTS_DIR, "fresh_hive_criteria_verified.png")
        await page.screenshot(path=fresh_screen_path, full_page=True)
        print(f"Captured Fresh Hive screenshot: {fresh_screen_path}")

        # 4. Test Invite filter tab
        print("\n5. Testing Filter: 📨 Invite (7)...")
        await page.click("#filterInvitePages")
        await asyncio.sleep(1)
        invite_items = await page.query_selector_all(".page-list-item[data-page-id]")
        print(f"Filtered invite pages count: {len(invite_items)}")
        assert len(invite_items) == 7, f"Expected 7 invite pages, got {len(invite_items)}"

        # 5. Select Lopez Edward (Invite-Only Page)
        print("\n6. Testing Invite Page: Lopez Edward...")
        lopez_item = await page.query_selector(".page-list-item[data-page-name*='lopez']")
        assert lopez_item is not None, "Lopez Edward not found in sidebar"
        await lopez_item.click()
        await asyncio.sleep(1.5)

        # Verify Box C shows Invite-Only Overview ONLY (Screenshot 1 Match)
        badge_text_lopez = await page.inner_text("#badgeMonetizeAuto")
        print(f"Monetization Badge for Lopez: {badge_text_lopez}")
        assert "invite-only" in badge_text_lopez.lower(), "Should have Invite-Only badge"

        # Check Overview Card (Screenshot 1 Match)
        overview_card_lopez = await page.query_selector(".monetize-overview-card")
        assert overview_card_lopez is not None, "Overview card must be present on Invite Page!"

        overview_header = await page.inner_text(".monetize-overview-header h4")
        print(f"Overview Header: {overview_header}")
        assert "Not yet eligible" in overview_header, "Expected 'Not yet eligible'"

        tools = await page.query_selector_all(".monetize-tool-item")
        print(f"Overview tools count: {len(tools)}")
        assert len(tools) == 2, "Expected 2 tools in Overview (Content monetization & Subscriptions)"

        tool1_status = await tools[0].inner_text()
        print(f"Tool 1: {tool1_status.replace(chr(10), ' | ')}")
        assert "Invite only" in tool1_status, "Tool 1 should be Invite only"

        tool2_status = await tools[1].inner_text()
        print(f"Tool 2: {tool2_status.replace(chr(10), ' | ')}")
        assert "1 of 3 criteria met" in tool2_status, "Tool 2 should be 1 of 3 criteria met"

        # Check Support Card (Screenshot 1 Match)
        support_card = await page.query_selector(".support-card-fb")
        assert support_card is not None, "Support card must be present"

        # Check Beta Card and Velocity Booster
        booster_card = await page.query_selector(".invite-booster-card")
        assert booster_card is not None, "Algorithm booster card must be present"

        # Verify Criteria Area waitlist is NOT present
        waitlist_card_lopez = await page.query_selector(".waitlist-card-fb")
        assert waitlist_card_lopez is None, "Criteria Area waitlist must NOT be visible on Invite-Only Page!"

        # Capture Screenshot 2: Lopez Edward (Invite-Only Screenshot 1 Match)
        lopez_screen_path = os.path.join(ARTIFACTS_DIR, "lopez_edward_invite_verified.png")
        await page.screenshot(path=lopez_screen_path, full_page=True)
        print(f"Captured Lopez Edward screenshot: {lopez_screen_path}")

        # 6. Test In-App Modals
        print("\n7. Testing In-App Help Modal...")
        await page.click(".btn-support-visit")
        await asyncio.sleep(1)
        help_modal = await page.query_selector("#helpModal")
        help_display = await page.evaluate("() => document.getElementById('helpModal').style.display")
        assert help_display == "flex", "Help modal should be visible"
        print("Help modal successfully opened in-app!")
        
        # Close Help modal
        await page.click("#btnCloseHelpModal")
        await asyncio.sleep(0.5)

        print("\n8. Testing In-App Video Details Modal...")
        detail_btns = await page.query_selector_all(".btn-video-inspect")
        if len(detail_btns) > 0:
            await detail_btns[0].click()
            await asyncio.sleep(1)
            video_modal = await page.query_selector("#videoModal")
            video_display = await page.evaluate("() => document.getElementById('videoModal').style.display")
            assert video_display == "flex", "Video modal should be visible"
            print("Video details modal successfully opened in-app!")
            await page.click("#btnCloseVideoModal")
            await asyncio.sleep(0.5)

        # 7. Test Mobile Viewport (Responsive check)
        print("\n9. Testing Mobile Viewport (iPhone 14 / 390x844)...")
        await page.set_viewport_size({"width": 390, "height": 844})
        await asyncio.sleep(1)
        mobile_screen_path = os.path.join(ARTIFACTS_DIR, "mobile_verified_view.png")
        await page.screenshot(path=mobile_screen_path)
        print(f"Captured Mobile screenshot: {mobile_screen_path}")

        print("\nALL VERIFICATIONS PASSED 100%!")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(verify_dashboard())
