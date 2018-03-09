import json

import requests

authorization = "a5f0d2e4-10be-11e8-ad82-9801a7dc7761"
# "{'college': 'SDU', 'sex': 'm', 'user_id': 5, 'age': 11, 'nickname': 'boss'}"

# with requests.session() as session:
#     resp = session.post('http://120.79.40.86:8000/users/login', data={
#         "username": "JF",
#         "password": "13525566656jing",
#     })

with requests.session() as session:
    resp = session.post('http://localhost:8000/images', data={
        "img_format": "png",
        "authorization": authorization
    })

d = json.loads(resp.content.decode())
post_dict = d["form_item"]
#

file = open("kk.jpg", "rb")
with requests.session() as session:
    ali_resp = session.post("http://sd-project-test.oss-cn-shenzhen.aliyuncs.com", data=post_dict, files={"file": file})

print(ali_resp.status_code, ali_resp.content)
#

print(dir(resp.request))
print(resp.request.body)
print(resp.status_code)
print(d)


resp = requests.put("http://localhost:8000/images", data={
    "authorization": authorization,
    "image_id": d['image_id'],
    "status_code": ali_resp.status_code,

})

print(resp.content)

#
#
# try:
#     print(json.loads(resp.content.decode()))
# except json.JSONDecodeError:
#     print(resp.content)

# import socket
#
# a = socket.socket()
#
# a.connect(("119.28.21.242", 8808))
#
# with open("temp.zip", "wb") as file:
#     while True:
#         data = a.recv(1024)
#         print(data, end="")
#         if data == b"":
#             break
#         file.write(data)
