import json

import requests


def get_image_tags(img_url, endpoint, key):
    headers = {'Ocp-Apim-Subscription-Key': key}
    url = {"url": img_url}
    resp = requests.post(url="https://api.cognitive.azure.cn/vision/v1.0/tag",
                  data=json.dumps(url),
                  headers=headers)

    tags = []

    for i in json.loads(resp.content.decode())["tags"]:
        tags.append(i["name"])

    return tags

key = "6a6576876831497bbdf6539c13c9a378"
url = "https://resource.cdn.azure.cn/marketing-resource/css/images/cognitive-services-computer-vision-read01.jpg"

print(get_image_tags(img_url=url, key=key, endpoint=''))