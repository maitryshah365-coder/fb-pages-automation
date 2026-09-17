import requests, json

tok = "EAAW5PzO6l2ABO9ZB4jTjWbXm7ZBF1k0ZCzZAZA088ZCSXAZBxwZCMn2P6V3ZCR2o4ZBf66GkSZAZBWGj6G8ZAPyZCG1lJYZC38wAZCR6X9o6ZCR8z4QZB6ZCOkZBt0r6rZBP4yV4fMZAO2ZCZBR40Jd27z4ZC0wZB6w4z4ZBy58ZA0Vb"
# Let's get real token from pages_data.json
with open('docs/data/pages_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Horizon Nest Daily (page 4): 956622247541040
p4 = next(p for p in data['pages'] if str(p['id']) == '956622247541040')
tok = p4['access_token']
vid = "968893462900592"

# 1. Standard fields
r1 = requests.get(f"https://graph.facebook.com/v20.0/{vid}", params={
    "fields": "id,views,length,published,status,video_insights",
    "access_token": tok
}).json()
print("Direct video fields:", json.dumps(r1, indent=2))

# 2. Insights
r2 = requests.get(f"https://graph.facebook.com/v20.0/{vid}/video_insights", params={
    "access_token": tok
}).json()
print("Video insights:", json.dumps(r2, indent=2))

# 3. Post insights if post id exists
r3 = requests.get(f"https://graph.facebook.com/v20.0/{vid}/insights", params={
    "metric": "post_video_views,post_video_views_organic,post_impressions",
    "access_token": tok
}).json()
print("Post insights:", json.dumps(r3, indent=2))
