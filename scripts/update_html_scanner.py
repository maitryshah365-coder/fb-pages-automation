import re

def update_html(path):
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()

    # Update buttons
    old_btns = r'''<button type="button" onclick="copyBookmarkletCode\(\)"[\s\S]*?<span>📋 Copy Code</span>[\s\S]*?</button>'''
    new_btns = '''<button type="button" onclick="copyConsoleScript()" style="background: linear-gradient(135deg, #059669, #10b981); border: 1px solid rgba(52,211,153,0.4); color: #fff; font-weight: 800; font-size: 12px; padding: 8px 12px; border-radius: 8px; cursor: pointer; display: inline-flex; align-items: center; gap: 5px; box-shadow: 0 4px 12px rgba(16,185,129,0.3);" title="Facebook par F12 Console me paste karne ke liye code copy karein">
              <span>💻 Copy F12 Console Code (Fastest)</span>
            </button>
            <button type="button" onclick="copyBookmarkletCode()" style="background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.15); color: #e2e8f0; font-weight: 700; font-size: 12px; padding: 8px 12px; border-radius: 8px; cursor: pointer; display: inline-flex; align-items: center; gap: 5px;">
              <span>📋 Copy Bookmarklet</span>
            </button>'''

    html = re.sub(old_btns, lambda m: new_btns, html)

    # Update modal content with both methods
    modal_body_pattern = r'<div class="modal-body" style="padding: 20px; font-size: 13px; line-height: 1.6; color: #cbd5e1;">[\s\S]*?</div>\s*</div>\s*</div>'
    new_modal_body = '''<div class="modal-body" style="padding: 20px; font-size: 13px; line-height: 1.6; color: #cbd5e1;">
        <div style="margin-bottom: 16px;">
          <strong style="color: #60a5fa;">Facebook Real Monetization Scanner</strong> live Facebook screen aur professional dashboard se 100% real status read karta hai. Aap ise 2 aasan tareeqo se chala sakte hain:
        </div>
        
        <div style="display: flex; flex-direction: column; gap: 12px; margin-bottom: 20px;">
          <!-- Tareeka 1: F12 Console (Fastest) -->
          <div style="background: rgba(34,197,94,0.08); border: 1px solid rgba(34,197,94,0.25); border-radius: 10px; padding: 12px;">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;">
              <strong style="color: #4ade80; font-size: 14px;">⚡ Tareeka 1: F12 Console (Sabse Fast & 100% Guaranteed)</strong>
              <span style="background: #22c55e; color: #052e16; font-size: 10px; font-weight: 900; padding: 2px 6px; border-radius: 4px;">RECOMMENDED</span>
            </div>
            <ol style="margin: 0; padding-left: 18px; display: flex; flex-direction: column; gap: 4px; color: #e2e8f0;">
              <li>Upar diye gaye green button <strong>"💻 Copy F12 Console Code"</strong> par click karein.</li>
              <li>Facebook par jaiye aur keyboard par <code style="color:#facc15; font-weight:bold;">F12</code> dabayein (ya Right-click &gt; Inspect).</li>
              <li>Upar <strong>Console</strong> tab par click karein.</li>
              <li>Code paste karein (<code style="color:#facc15; font-weight:bold;">Ctrl + V</code>) aur <code style="color:#facc15; font-weight:bold;">Enter</code> daba dein!</li>
            </ol>
            <div style="margin-top: 6px; font-size: 11.5px; color: #94a3b8;">Facebook screen par turant dark Scanner window khul jayega!</div>
          </div>

          <!-- Tareeka 2: Bookmarklet -->
          <div style="background: rgba(59,130,246,0.08); border: 1px solid rgba(59,130,246,0.25); border-radius: 10px; padding: 12px;">
            <strong style="color: #60a5fa; font-size: 14px; display: block; margin-bottom: 6px;">⭐ Tareeka 2: Chrome Bookmarks Bar</strong>
            <ol style="margin: 0; padding-left: 18px; display: flex; flex-direction: column; gap: 4px; color: #e2e8f0;">
              <li>Blue button <strong>"⚡ Scan FB Tools"</strong> ko mouse se pakad kar apne Chrome Bookmarks bar me drop karein.</li>
              <li>Facebook par kisi bhi page par hote hue bookmarks me <strong>"⚡ Scan FB Tools"</strong> par click karein.</li>
            </ol>
          </div>
        </div>

        <button type="button" class="btn-primary-action" onclick="closeScannerGuideModal()" style="width: 100%; justify-content: center; padding: 10px; border-radius: 8px;">
          Samajh Gaya (Close)
        </button>
      </div>
    </div>
  </div>'''

    html = re.sub(modal_body_pattern, lambda m: new_modal_body, html)

    # Bump version to 8.9.6
    html = html.replace('js/gold_app.js?v=8.9.5', 'js/gold_app.js?v=8.9.6')

    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print("Updated", path)

update_html('docs/index.html')
update_html('web/index.html')
