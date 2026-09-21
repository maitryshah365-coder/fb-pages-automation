import json

with open('docs/data/pages_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

pages = data.get('pages', [])
print(f'Total pages: {len(pages)}')

scores = []
for p in pages:
    pid = str(p.get('id'))
    name = p.get('name')
    followers = int(p.get('followers') or 0)
    views = int(p.get('total_views') or 0)
    reels = len(p.get('videos', []))
    
    # Followers pct (target 5000)
    f_pct = min(100, round((followers / 5000) * 100))
    f_met = followers >= 5000
    
    # Views pct (target 60000)
    v_pct = min(100, round((views / 60000) * 100))
    v_met = views >= 60000
    
    # Reels pct (target 5)
    r_pct = min(100, round((reels / 5) * 100))
    r_met = reels >= 5
    
    criteria_met = (1 if f_met else 0) + (1 if v_met else 0) + (1 if r_met else 0)
    
    # Stars (target 500)
    stars_pct = min(100, round((followers / 500) * 100))
    stars_met = followers >= 500
    
    # Overall score (40% followers, 40% views, 20% reels)
    overall = round((f_pct * 0.4) + (v_pct * 0.4) + (r_pct * 0.2))
    if pid == '818808074651170': # Roberts Richard
        overall = 100 # Confirmed setup available
        
    scores.append({
        'name': name,
        'pid': pid,
        'followers': followers,
        'f_pct': f_pct,
        'views': views,
        'v_pct': v_pct,
        'reels': reels,
        'criteria_met': criteria_met,
        'overall': overall,
        'stars_met': stars_met,
        'stars_pct': stars_pct
    })

scores.sort(key=lambda x: x['overall'], reverse=True)

print('--- TOP 12 OVERALL SCORES ---')
for s in scores[:12]:
    print(f"{s['overall']:3d}% | {s['criteria_met']}/3 Met | {s['name'][:24]:24s} | Fol: {s['followers']:6d} ({s['f_pct']:3d}%) | Views: {s['views']:9,d} ({s['v_pct']:3d}%) | Reels: {s['reels']:3d}")

c_100 = len([s for s in scores if s['overall'] >= 100])
c_75 = len([s for s in scores if 75 <= s['overall'] < 100])
c_50 = len([s for s in scores if 50 <= s['overall'] < 75])
c_low = len([s for s in scores if s['overall'] < 50])
stars_ready = len([s for s in scores if s['stars_met']])

print(f'\nBreakdown: 100% Ready: {c_100} | 75-99%: {c_75} | 50-74%: {c_50} | <50%: {c_low} | Stars Ready: {stars_ready}')
