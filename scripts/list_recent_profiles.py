import json
import os

with open(r'C:\Users\Win\AppData\Local\CentBrowser\User Data\Local State', 'r', encoding='utf-8') as f:
    ls = json.load(f)

cache = ls.get('profile', {}).get('info_cache', {})
print(f'Total profiles in CentBrowser: {len(cache)}')

# Print highest numbered profiles
sorted_by_num = sorted(cache.items(), key=lambda x: int(x[0].replace('Profile ', '')) if 'Profile ' in x[0] and x[0].replace('Profile ', '').isdigit() else 0, reverse=True)
for p_key, p_info in sorted_by_num[:30]:
    name = p_info.get('name')
    gaia = p_info.get('gaia_name')
    uname = p_info.get('user_name')
    print(f'{p_key}: name="{name}", gaia="{gaia}", email="{uname}"')
