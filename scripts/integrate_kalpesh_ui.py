import os
import sys

def update_gold_app(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Fix usedIds in enforceStrictFleetSorting
    target_1 = "...FLEET_USA_05_IDS, ...FLEET_UK_01_IDS"
    replacement_1 = "...FLEET_USA_05_IDS, ...FLEET_USA_06_IDS, ...FLEET_UK_01_IDS"
    if target_1 in content:
        content = content.replace(target_1, replacement_1)
        print(f"[{file_path}] 1. Fixed usedIds (prevents 186 duplicate pages)")

    # 2. Add usa6List in renderSidebarPagesList
    target_2_decl = "  const usa5List = [];\n  const uk1List = [];"
    replacement_2_decl = "  const usa5List = [];\n  const usa6List = [];\n  const uk1List = [];"
    if target_2_decl in content:
        content = content.replace(target_2_decl, replacement_2_decl)
        print(f"[{file_path}] 2a. Added usa6List declaration")

    target_2_route = "    else if (FLEET_USA_05_SET.has(pid) || (p.account && p.account.includes(\"Sejal\")) || p.account_owner === \"Sejal Soni\" || p.box_group === \"Sejal Soni\") usa5List.push(p);\n    else if (FLEET_UK_01_SET.has(pid)) uk1List.push(p);"
    replacement_2_route = "    else if (FLEET_USA_05_SET.has(pid) || (p.account && p.account.includes(\"Sejal\")) || p.account_owner === \"Sejal Soni\" || p.box_group === \"Sejal Soni\") usa5List.push(p);\n    else if (FLEET_USA_06_SET.has(pid) || (p.account && p.account.includes(\"Kalpesh\")) || p.account_owner === \"Kalpesh Shah\" || p.box_group === \"Kalpesh Shah\") usa6List.push(p);\n    else if (FLEET_UK_01_SET.has(pid)) uk1List.push(p);"
    if target_2_route in content:
        content = content.replace(target_2_route, replacement_2_route)
        print(f"[{file_path}] 2b. Added usa6List routing")

    target_2_box = "  if (usa5List.length > 0) {\n    html += buildBox(\"sidebar-box-usa5\", \"usa5\", \"🇺🇸\", \"Sejal Soni\", `${usa5List.length} Pages`, usa5List, \"usa5\");\n  }"
    replacement_2_box = "  if (usa5List.length > 0) {\n    html += buildBox(\"sidebar-box-usa5\", \"usa5\", \"🇺🇸\", \"Sejal Soni\", `${usa5List.length} Pages`, usa5List, \"usa5\");\n  }\n  if (usa6List.length > 0) {\n    html += buildBox(\"sidebar-box-usa6\", \"usa6\", \"🇺🇸\", \"Kalpesh Shah\", `${usa6List.length} Pages`, usa6List, \"usa6\");\n  }"
    if target_2_box in content and "Kalpesh Shah" not in content[content.find(target_2_box):content.find(target_2_box)+300]:
        content = content.replace(target_2_box, replacement_2_box)
        print(f"[{file_path}] 2c. Added usa6 buildBox in sidebar")

    # 3. Add Kalpesh Shah to FLEET_SCHEDULE_SLOTS
    target_3 = "  // Sejal Soni - 15 Pages (Google Pixel 9 Pro Anti-Detect Profile - Staggered +20m Slot)\n  { fleetId: \"a5\", name: \"Sejal\", flagSrc: \"icons/us.png\", h: 3, m: 20, label: \"Slot 1\" },\n  { fleetId: \"a5\", name: \"Sejal\", flagSrc: \"icons/us.png\", h: 15, m: 20, label: \"Slot 2\" },\n  { fleetId: \"a5\", name: \"Sejal\", flagSrc: \"icons/us.png\", h: 20, m: 20, label: \"Slot 3\" },\n  { fleetId: \"a5\", name: \"Sejal\", flagSrc: \"icons/us.png\", h: 0, m: 20, label: \"Slot 4\" },"
    replacement_3 = target_3 + "\n\n  // Kalpesh Shah - 15 Pages (USA Account 6 - Staggered +40m Slot)\n  { fleetId: \"a6\", name: \"Kalpesh\", flagSrc: \"icons/us.png\", h: 3, m: 40, label: \"Slot 1\" },\n  { fleetId: \"a6\", name: \"Kalpesh\", flagSrc: \"icons/us.png\", h: 15, m: 40, label: \"Slot 2\" },\n  { fleetId: \"a6\", name: \"Kalpesh\", flagSrc: \"icons/us.png\", h: 20, m: 40, label: \"Slot 3\" },\n  { fleetId: \"a6\", name: \"Kalpesh\", flagSrc: \"icons/us.png\", h: 0, m: 40, label: \"Slot 4\" },"
    if target_3 in content and 'fleetId: "a6"' not in content:
        content = content.replace(target_3, replacement_3)
        print(f"[{file_path}] 3. Added Kalpesh to FLEET_SCHEDULE_SLOTS")

    # 4. Add a6 to updateRadarSlots()
    target_4 = "{ id: \"a5\", matcher: p => FLEET_USA_05_SET.has(String(p.id)) || (p.page_id && FLEET_USA_05_SET.has(String(p.page_id))) || (p.account && p.account.includes(\"Sejal\")) || p.account_owner === \"Sejal Soni\", defaultSlots: 60 },"
    replacement_4 = target_4 + "\n    { id: \"a6\", matcher: p => FLEET_USA_06_SET.has(String(p.id)) || (p.page_id && FLEET_USA_06_SET.has(String(p.page_id))) || (p.account && p.account.includes(\"Kalpesh\")) || p.account_owner === \"Kalpesh Shah\", defaultSlots: 60 },"
    if target_4 in content and 'id: "a6"' not in content:
        content = content.replace(target_4, replacement_4)
        print(f"[{file_path}] 4. Added a6 to updateRadarSlots")

    # 5. Add a6 to fleetIds and fleetFilterMap in tickRadar
    target_5_ids = 'const fleetIds = ["a1", "a2", "a3", "a4", "a5", "uk1", "uk2", "uk3", "uk4", "uk5", "uk6", "uk7"];'
    replacement_5_ids = 'const fleetIds = ["a1", "a2", "a3", "a4", "a5", "a6", "uk1", "uk2", "uk3", "uk4", "uk5", "uk6", "uk7"];'
    if target_5_ids in content:
        content = content.replace(target_5_ids, replacement_5_ids)
        print(f"[{file_path}] 5a. Added a6 to fleetIds")

    target_5_map = 'a5: { name: "USA 05 • Sejal Soni", matcher: p => FLEET_USA_05_SET.has(String(p.id)) || (p.account && p.account.includes("Sejal")) || p.account_owner === "Sejal Soni" },'
    replacement_5_map = target_5_map + '\n    a6: { name: "USA 06 • Kalpesh Shah", matcher: p => FLEET_USA_06_SET.has(String(p.id)) || (p.account && p.account.includes("Kalpesh")) || p.account_owner === "Kalpesh Shah" },'
    if target_5_map in content and 'a6: {' not in content:
        content = content.replace(target_5_map, replacement_5_map)
        print(f"[{file_path}] 5b. Added a6 to fleetFilterMap")

    # 6. Add a6Stock to Drive Hero counters
    target_6_decl = "  let a5Stock = 0;\n  let ukStock = 0;"
    replacement_6_decl = "  let a5Stock = 0;\n  let a6Stock = 0;\n  let ukStock = 0;"
    if target_6_decl in content:
        content = content.replace(target_6_decl, replacement_6_decl)
        print(f"[{file_path}] 6a. Added a6Stock declaration")

    target_6_is = 'const isUSA5 = FLEET_USA_05_SET.has(pid) || (p.account && p.account.includes("Sejal")) || p.account_owner === "Sejal Soni" || p.box_group === "Sejal Soni";'
    replacement_6_is = target_6_is + '\n    const isUSA6 = FLEET_USA_06_SET.has(pid) || (p.account && p.account.includes("Kalpesh")) || p.account_owner === "Kalpesh Shah" || p.box_group === "Kalpesh Shah";'
    if target_6_is in content and 'const isUSA6' not in content:
        content = content.replace(target_6_is, replacement_6_is)
        print(f"[{file_path}] 6b. Added isUSA6 check")

    target_6_sum = "    } else if (isUSA5) {\n      a5Stock += count;\n    } else {\n      ukStock += count;\n    }"
    replacement_6_sum = "    } else if (isUSA5) {\n      a5Stock += count;\n    } else if (isUSA6) {\n      a6Stock += count;\n    } else {\n      ukStock += count;\n    }"
    if target_6_sum in content:
        content = content.replace(target_6_sum, replacement_6_sum)
        print(f"[{file_path}] 6c. Added a6Stock summation")

    target_6_el = '  const elA5 = document.getElementById("driveHeroA5Count");\n  if (elA5) elA5.innerText = `${a5Stock.toLocaleString()} Videos`;'
    replacement_6_el = target_6_el + '\n  const elA6 = document.getElementById("driveHeroA6Count");\n  if (elA6) elA6.innerText = `${a6Stock.toLocaleString()} Videos`;'
    if target_6_el in content and 'driveHeroA6Count' not in content:
        content = content.replace(target_6_el, replacement_6_el)
        print(f"[{file_path}] 6d. Added driveHeroA6Count update")

    # 7. Add isUSA6 and a6 filter in renderDriveInventoryList
    target_7_inv = 'const isUSA5 = (p.account && p.account.includes("Sejal")) || p.account_owner === "Sejal Soni" || p.box_group === "Sejal Soni";'
    replacement_7_inv = target_7_inv + '\n    const isUSA6 = (p.account && p.account.includes("Kalpesh")) || p.account_owner === "Kalpesh Shah" || p.box_group === "Kalpesh Shah" || FLEET_USA_06_SET.has(pid);'
    if target_7_inv in content and 'const isUSA6' not in content[content.find(target_7_inv):content.find(target_7_inv)+200]:
        content = content.replace(target_7_inv, replacement_7_inv)
        print(f"[{file_path}] 7a. Added isUSA6 in renderDriveInventoryList")

    target_7_filt = 'if (currentDriveAccountFilter === "a5" && !isUSA5) return false;'
    replacement_7_filt = target_7_filt + '\n    if (currentDriveAccountFilter === "a6" && !isUSA6) return false;'
    if target_7_filt in content and 'currentDriveAccountFilter === "a6"' not in content:
        content = content.replace(target_7_filt, replacement_7_filt)
        print(f"[{file_path}] 7b. Added a6 filter in renderDriveInventoryList")

    # 8. Post Now Studio additions
    target_8_decl = "  const usa5List = [];\n  const uk1List = [];"
    # Note: target_8_decl occurs twice in gold_app.js: once in renderSidebarPagesList and once in renderStudioFleetList
    # Let's handle renderStudioFleetList routing
    target_8_route = '    else if (FLEET_USA_04_SET.has(pId) || (page.account && page.account.includes("Rohini")) || page.account_owner === "Rohini Dutt" || page.box_group === "Rohini Dutt") usa4List.push(page);\n    else if (FLEET_UK_01_SET.has(pId)) uk1List.push(page);'
    replacement_8_route = '    else if (FLEET_USA_04_SET.has(pId) || (page.account && page.account.includes("Rohini")) || page.account_owner === "Rohini Dutt" || page.box_group === "Rohini Dutt") usa4List.push(page);\n    else if (FLEET_USA_05_SET.has(pId) || (page.account && page.account.includes("Sejal")) || page.account_owner === "Sejal Soni" || page.box_group === "Sejal Soni") usa5List.push(page);\n    else if (FLEET_USA_06_SET.has(pId) || (page.account && page.account.includes("Kalpesh")) || page.account_owner === "Kalpesh Shah" || page.box_group === "Kalpesh Shah") usa6List.push(page);\n    else if (FLEET_UK_01_SET.has(pId)) uk1List.push(page);'
    if target_8_route in content:
        content = content.replace(target_8_route, replacement_8_route)
        print(f"[{file_path}] 8a. Added usa5 and usa6 routing in renderStudioFleetList")

    target_8_box = '  if (usa4List.length > 0) {\n    html += buildStudioBox("account-box-us", "a4", "🇺🇸", "Rohini Dutt (S25)", usa4List.length, usa4List, "usa4");\n  }'
    replacement_8_box = target_8_box + '\n  if (usa5List.length > 0) {\n    html += buildStudioBox("account-box-us", "a5", "🇺🇸", "Sejal Soni (Pixel 9)", usa5List.length, usa5List, "usa5");\n  }\n  if (usa6List.length > 0) {\n    html += buildStudioBox("account-box-us", "a6", "🇺🇸", "Kalpesh Shah", usa6List.length, usa6List, "usa6");\n  }'
    if target_8_box in content and 'Kalpesh Shah' not in content[content.find(target_8_box):content.find(target_8_box)+350]:
        content = content.replace(target_8_box, replacement_8_box)
        print(f"[{file_path}] 8b. Added usa5 and usa6 buildStudioBox")

    target_8_toggle = 'else if (fleetId === "a4") list = FLEET_USA_04_IDS;\n  else if (fleetId === "uk1") list = FLEET_UK_01_IDS;'
    replacement_8_toggle = 'else if (fleetId === "a4") list = FLEET_USA_04_IDS;\n  else if (fleetId === "a5") list = FLEET_USA_05_IDS;\n  else if (fleetId === "a6") list = FLEET_USA_06_IDS;\n  else if (fleetId === "uk1") list = FLEET_UK_01_IDS;'
    if target_8_toggle in content:
        content = content.replace(target_8_toggle, replacement_8_toggle)
        print(f"[{file_path}] 8c. Added a5 and a6 to toggleBoxSelectAll")

    # 9. Health & Audit Center fleetConfigs
    target_9 = '{ tag: "USA 5", owner: "Sejal Soni", set: FLEET_USA_05_SET, startIdx: 142, endIdx: 156, flag: "🇺🇸", flagImg: "icons/us.png", countryGroup: "USA", isDeviceProfile: false },'
    replacement_9 = target_9 + '\n    { tag: "USA 6", owner: "Kalpesh Shah", set: FLEET_USA_06_SET, startIdx: 157, endIdx: 171, flag: "🇺🇸", flagImg: "icons/us.png", countryGroup: "USA", isDeviceProfile: false },'
    if target_9 in content and 'Kalpesh Shah' not in content[content.find(target_9):content.find(target_9)+250]:
        content = content.replace(target_9, replacement_9)
        print(f"[{file_path}] 9a. Added USA 6 to main health audit")

    target_9_mob = '{ tag: "USA 5", owner: "Sejal Soni", set: FLEET_USA_05_SET, startIdx: 142, endIdx: 156, flag: "🇺🇸", countryGroup: "USA" },'
    replacement_9_mob = target_9_mob + '\n      { tag: "USA 6", owner: "Kalpesh Shah", set: FLEET_USA_06_SET, startIdx: 157, endIdx: 171, flag: "🇺🇸", countryGroup: "USA" },'
    if target_9_mob in content and 'Kalpesh Shah' not in content[content.find(target_9_mob):content.find(target_9_mob)+250]:
        content = content.replace(target_9_mob, replacement_9_mob)
        print(f"[{file_path}] 9b. Added USA 6 to mobile health audit")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Successfully saved {file_path}")

def update_index_html(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Update Automation Radar grid card
    target_radar = """          <div class="radar-timeline-card" id="radarCard_a5">
            <div class="radar-card-top"><span><img src="icons/us.png" alt="US" class="app-flag-icon"> #5</span><span>15 Pages</span></div>
            <div class="radar-card-name">Sejal Soni</div>
            <div class="radar-card-time">05:50 AM IST (Slot 4)</div>
            <div class="radar-card-slots" id="radarSlots_a5">0 / 60 Slots</div>
          </div>"""

    replacement_radar = target_radar + """\n\n          <div class="radar-timeline-card" id="radarCard_a6">
            <div class="radar-card-top"><span><img src="icons/us.png" alt="US" class="app-flag-icon"> #6</span><span>15 Pages</span></div>
            <div class="radar-card-name">Kalpesh Shah</div>
            <div class="radar-card-time">09:10 AM IST (Slot 1)</div>
            <div class="radar-card-slots" id="radarSlots_a6">0 / 60 Slots</div>
          </div>"""

    if target_radar in content and 'id="radarCard_a6"' not in content:
        content = content.replace(target_radar, replacement_radar)
        print(f"[{file_path}] 1. Added radarCard_a6 (Kalpesh Shah) to Automation Radar")

    # 2. Update radar slots total
    content = content.replace("0 / 624 Slots", "0 / 684 Slots")
    content = content.replace("across all 101 configured pages", "across all 171 configured pages")
    content = content.replace("<!-- 7-Fleet Staggered Execution Matrix -->", "<!-- 13-Account Staggered Execution Matrix -->")

    # 3. Add Kalpesh Stock strip and button in Drive Data
    target_drive_hero = """          <div class="strip-stat">
            <span class="stat-label"><img src="icons/us.png" alt="US" class="app-flag-icon"> Sejal Stock</span>
            <span class="stat-num" id="driveHeroA5Count" style="color: #a78bfa;">3,131 Videos</span>
          </div>"""

    replacement_drive_hero = target_drive_hero + """\n          <div class="strip-stat">
            <span class="stat-label"><img src="icons/us.png" alt="US" class="app-flag-icon"> Kalpesh Stock</span>
            <span class="stat-num" id="driveHeroA6Count" style="color: #ec4899;">2,062 Videos</span>
          </div>"""

    if target_drive_hero in content and 'id="driveHeroA6Count"' not in content:
        content = content.replace(target_drive_hero, replacement_drive_hero)
        print(f"[{file_path}] 2. Added Kalpesh Stock strip counter")

    target_drive_btn = '<button type="button" class="timeframe-pill" data-filter="a5" id="btnDriveFilterA5"><img src="icons/us.png" alt="US" class="app-flag-icon"> Sejal Soni (15)</button>'
    replacement_drive_btn = target_drive_btn + '\n              <button type="button" class="timeframe-pill" data-filter="a6" id="btnDriveFilterA6"><img src="icons/us.png" alt="US" class="app-flag-icon"> Kalpesh Shah (15)</button>'
    if target_drive_btn in content and 'id="btnDriveFilterA6"' not in content:
        content = content.replace(target_drive_btn, replacement_drive_btn)
        print(f"[{file_path}] 3. Added btnDriveFilterA6 filter button")

    # 4. Update 156 / 158 occurrences to 171
    content = content.replace("All 156 Pages Portfolio", "All 171 Pages Portfolio")
    content = content.replace("156 Facebook Pages", "171 Facebook Pages")
    content = content.replace("156 Pages</span>", "171 Pages</span>")
    content = content.replace("Search across all 156 pages", "Search across all 171 pages")
    content = content.replace("156 / 156 Ready", "171 / 171 Ready")
    content = content.replace("All (156)", "All (171)")
    content = content.replace("158 Active Facebook Pages (632 Daily Slots)", "171 Active Facebook Pages (684 Daily Slots)")
    content = content.replace("across all 156 Facebook Pages", "across all 171 Facebook Pages")
    content = content.replace("156 Pages Monitored", "171 Pages Monitored")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Successfully saved {file_path}")

if __name__ == "__main__":
    for p in ["docs/js/gold_app.js", "web/js/gold_app.js"]:
        update_gold_app(p)
    for p in ["docs/index.html", "web/index.html"]:
        update_index_html(p)
