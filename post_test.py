import json

import requests

authorization = "b8914424-07ff-11e8-8dd2-9801a7dc7761"
"{'college': 'SDU', 'sex': 'm', 'user_id': 5, 'age': 11, 'nickname': 'boss'}"

with requests.session() as session:
    resp = session.get('http://localhost:8000/images', params={
        "authorization": authorization,
        "user_id": "3"
    })

# post_dict = {
#     'Signature': '6E9RBl4ycZeeRkIrCvNJfbopA0w=', 'OSSAccessKeyId': 'LTAIaNUnqzQf5kdD',
#     'policy': 'eyJjb25kaXRpb25zIjogW1siZXEiLCAiJGtleSIsICIxMi5qcGVnIl0sIFsiY29udGVudC1sZW5ndGgtcmFuZ2UiLCAwLCAxMDczNzQxODI0XSwgWyJlcSIsICIkc3VjY2Vzc19hY3Rpb25fc3RhdHVzIiwgIjIwMCJdXSwgImV4cGlyYXRpb24iOiAiMjAxOC0wMi0wMlQxMzoyMjoyNS45NDE4NDJaIn0=',
#     'success_action_status': 200, 'key': '12.jpeg'
# }
#
# with requests.session() as session:
#     ali_resp = session.post("http://sd-project-test.oss-cn-shenzhen.aliyuncs.com", data=post_dict, files={"file": b"fucker"})

# print(ali_resp.status_code, ali_resp.content)


print(dir(resp.request))
print(resp.request.body)
print(resp.status_code)
print(json.loads(resp.content.decode()))


