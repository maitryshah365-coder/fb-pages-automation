import json
import requests
from concurrent.futures import ThreadPoolExecutor

def test_all():
    with open('docs/data/pages_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    pages = data.get('pages', [])
    print(f"Loaded {len(pages)} pages. Testing live Meta Graph API for each page token...")

    def check_page(p):
        pid = str(p.get('id'))
        name = p.get('name')
        account = p.get('account')
        token = p.get('access_token')
        
        if not token:
            return {
                'id': pid,
                'name': name,
                'account': account,
                'status': 'NO_TOKEN',
                'error': 'Missing access token'
            }
        
        try:
            url = f"https://graph.facebook.com/v21.0/{pid}?fields=id,name&access_token={token}"
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                js = res.json()
                return {
                    'id': pid,
                    'name': name,
                    'account': account,
                    'status': 'ACTIVE',
                    'meta_name': js.get('name')
                }
            else:
                js = res.json()
                err = js.get('error', {}).get('message', res.text)
                code = js.get('error', {}).get('code')
                return {
                    'id': pid,
                    'name': name,
                    'account': account,
                    'status': 'FAILED',
                    'error': f"Code {code}: {err}"
                }
        except Exception as e:
            return {
                'id': pid,
                'name': name,
                'account': account,
                'status': 'EXCEPTION',
                'error': str(e)
            }

    with ThreadPoolExecutor(max_workers=20) as executor:
        results = list(executor.map(check_page, pages))

    # Aggregate by fleet
    fleet_summary = {}
    failed_pages = []

    for r in results:
        acc = r['account']
        if acc not in fleet_summary:
            fleet_summary[acc] = {'total': 0, 'active': 0, 'failed': 0}
        fleet_summary[acc]['total'] += 1
        if r['status'] == 'ACTIVE':
            fleet_summary[acc]['active'] += 1
        else:
            fleet_summary[acc]['failed'] += 1
            failed_pages.append(r)

    print("\n" + "="*70)
    print("LIVE META GRAPH API TOKEN AUDIT (ALL 10 FLEETS / 128 PAGES)")
    print("="*70)
    with open('token_audit_report.json', 'w', encoding='utf-8') as out:
        json.dump({'summary': fleet_summary, 'failed': failed_pages}, out, indent=2)

    for fleet, counts in fleet_summary.items():
        status_sym = "[OK]" if counts['failed'] == 0 else "[FAIL]"
        print(f"{status_sym} {fleet}: {counts['active']}/{counts['total']} Active (Failed: {counts['failed']})")

    print("="*70)
    total_active = sum(c['active'] for c in fleet_summary.values())
    total_all = sum(c['total'] for c in fleet_summary.values())
    print(f"TOTAL OVERALL HEALTH: {total_active}/{total_all} TOKENS ACTIVE ({total_active/total_all*100:.1f}%)")
    
    if failed_pages:
        print("\nFAILED PAGES:")
        for fp in failed_pages:
            print(f"- {fp['name']} ({fp['id']}) in {fp['account']}: {fp['error']}")
    else:
        print("\nSUCCESS: ZERO FAILED TOKENS! ALL 128 TOKENS ARE 100% OPERATIONAL!")
    print("="*70)

if __name__ == '__main__':
    test_all()
