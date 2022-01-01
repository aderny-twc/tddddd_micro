import requests


params = dict(q="Sausages", format="json")
parsed = requests.get('http://api.duckduckgo.com', params=params).json()

result = parsed["RelatedTopics"]

for r in result:
    if 'Text' in r:
        print(r['FirstURL'] + ' - ' + r['Text'])
