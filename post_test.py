import json

import requests

authorization = "c6d859fe-f4fe-11e7-8bca-e43a6e0c0416"
"{'college': 'SDU', 'sex': 'm', 'user_id': 5, 'age': 11, 'nickname': 'boss'}"

with requests.session() as session:
    resp = session.get('http://localhost:8000/users/info', params={
        "authorization": authorization,
        "nickname": "qqq",
        "id": "3"
    })
print(dir(resp.request))
print(resp.request.body)
print(resp.status_code)
print(json.loads(resp.content.decode()))