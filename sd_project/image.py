import json
import threading

import requests
from django.conf import settings
from sd_project import sd_oss
from sd_project import restful
from django.http import JsonResponse
from sd_project.auth import authorize
from sd_project.models import ImageStorage, ImageTag
import time
from django.utils import timezone
from sd_project.rd_session import sessions
import logging

_id = settings.OSS_KEY
_key = settings.OSS_SECRET
_bucket_name = settings.OSS_IMAGE_BUCKET_NAME
_endpoint = settings.OSS_ENDPOINT

oss = sd_oss.OSS(_id, _key, bucket_name=_bucket_name, endpoint=_endpoint)


class ImageSimilar:
    instance = None
    lock = threading.RLock()

    def __init__(self):
        self.img_tags = []
        for i in ImageTag.objects.all():
            self.img_tags.append({
                "id": i.id,
                "image_store_id": i.image_store_id,
                "tags": set(json.loads(i.tags))
            })

    @staticmethod
    def update(tag):
        if ImageSimilar.instance is None:
            ImageSimilar.instance = ImageSimilar()
        self = ImageSimilar.instance

        i = tag
        similar_count = 0
        max_num = 0
        max_ins = None
        this_tag_dict = {
            "id": i.id,
            "image_store_id": i.image_store_id,
            "tags": set(json.loads(i.tags)),
            "similar": 0
        }
        ImageSimilar.lock.acquire()
        for i in self.img_tags:
            print(i["tags"], this_tag_dict['tags'])
            i["similar"] = len(this_tag_dict['tags'] & i["tags"])
            if i["similar"] >= 2:
                similar_count += 1
            if i["similar"] >= max_num:
                max_num = i["similar"]
                max_ins = i
            print(i["similar"])
        self.img_tags.append(this_tag_dict)
        ImageSimilar.lock.release()

        if similar_count == 0:
            return JsonResponse({
                "expires": 6000,
                "result": None}, status=200)

        try:
            image = ImageStorage.objects.get(id=max_ins['image_store_id'])
        except ImageStorage.DoesNotExist:
            return JsonResponse({
                "reason": "server error"
            }, status=500)
        url, _ = get_url(image.id, image.oss_key)
        return JsonResponse({
            "expires": 6000,
            "result": {
                "similar_num": similar_count,
                "similarest_photo": url
            }
        }, status=200)


def get_url(img_id, img_key, expires=6000, out_time=300):
    cached_url = sessions.get_signed_url(img_id)
    now = int(time.time())
    if cached_url is not None:
        cached_url = cached_url.decode()
        logging.error(cached_url)
        *url, expire_time = cached_url.split(":")
        url = ":".join(url)
        if int(expire_time) - now > out_time:
            return url, expire_time
    signed_url = oss.sign_url("GET", img_key, expires=expires)
    sessions.set_image_session(img_id, signed_url, now + expires)
    return signed_url, now + expires


def get_image_tags(img_url, key):
    headers = {'Ocp-Apim-Subscription-Key': key}
    url = {"url": img_url}
    print(json.dumps(url))
    resp = requests.post(url=settings.AZURE_API_ENDPOINT,
                         data=json.dumps(url),
                         headers=headers)

    tags = []
    for i in json.loads(resp.content.decode())["tags"]:
        tags.append(i["name"])

    return tags


class ImageStore(restful.RESTFul):
    @authorize
    def get(self, request):
        image_id = request.GET.get("image_id")
        if image_id:
            try:
                image = ImageStorage.objects.get(id=image_id)
                signed_url, expire_time = get_url(image.id, image.oss_key, expires=6000)
                return JsonResponse({
                    "signed_url": signed_url,
                    "expire_time": expire_time,
                }, status=200)
            except ImageStorage.DoesNotExist:
                return JsonResponse({
                    "reason": "image_id not found"
                }, status=404)

        user_id = request.GET.get("user_id")
        if user_id:
            if user_id == str(request.user.id):
                image_id_list = ImageStorage.objects.filter(user_id=user_id).filter(verified=True).all()
                image_url_list = []
                for i in image_id_list:
                    url, expire_time = get_url(i.id, i.oss_key)
                    image_url_list.append({
                        "image_id": i.id,
                        "signed_url": url,
                        "expire_time": expire_time
                    })
                return JsonResponse({
                    "image_url_list": image_url_list
                })
            else:
                return JsonResponse({
                    "reason": "You have no access to get the images"
                }, status=403)

        image_id_list = request.GET.get("image_id_list")
        if image_id_list is not None:
            try:
                image_id_list = [int(i) for i in image_id_list.split()]
            except ValueError:
                return JsonResponse({
                    "reason": "The param image_id_list is illegal"
                }, status=400)
            else:
                images = [ImageStorage.objects.filter(id=i).first() for i in image_id_list]
                image_urls = []
                for i in images:
                    if images is None:
                        image_urls.append(None)
                    else:
                        signed_url, expire_time = get_url(i.id, i.oss_key)
                        image_urls.append({
                            "image_id": i.id,
                            "signed_url": signed_url,
                            "expire_time": expire_time
                        })
                return JsonResponse({
                    "image_url_list": image_urls
                }, status=200)
        return JsonResponse({
            "reason": "Must give one argument"
        }, status=400)

    @authorize
    def post(self, request):
        img_format = request.POST.get("img_format")
        if img_format is None:
            return JsonResponse({
                "reason": "img_format is required"
            }, status=403)
        img_format = img_format.lower()
        if img_format not in ("jpg", 'jpeg', "bmp", "png"):
            return JsonResponse({
                "reason": "{} is not allowed".format(img_format)
            }, status=403)

        new_image = ImageStorage(
            user_id=request.user.id,
            verified=False,
            oss_key="UNKNOWN",
            create_time=timezone.now()
        )
        new_image.save()
        filename = "{}.{}".format(new_image.id, img_format)
        new_image.oss_key = filename
        new_image.save()

        policy, signature = oss.policy(600, "", filename, length_range=(0, 1024 ** 3), status=200)
        form = {
            "form_item": {
                "OSSAccessKeyId": settings.OSS_KEY,
                "policy": policy,
                "Signature": signature,
                "key": new_image.oss_key,
                "success_action_status": 200,
            },
            "max_size": 1024 ** 3,
            "host": "{}.{}".format(_bucket_name, _endpoint),
            "method": "post",
            "image_id": new_image.id
        }

        return JsonResponse(form, status=200)

    @authorize
    def put(self, request):
        form = restful.FormParser(request)
        image_id = form.get("image_id")
        status_code = form.get("status_code")
        if image_id is not None:
            try:
                image = ImageStorage.objects.get(id=image_id)
                if image.user_id != request.user.id:
                    return JsonResponse({
                        "reason": "Image's uploader is not you"
                    }, status=403)
                if status_code == "200":
                    image.verified = True
                    image.save()

                    url, _ = get_url(img_id=image_id, img_key=image.oss_key)

                    tags = get_image_tags(url, key=settings.AZURE_KEY)
                    img_tag = ImageTag(image_id, image.id, json.dumps(tags))

                    img_tag.save()

                    return ImageSimilar.update(img_tag)
                elif status_code is None:
                    return JsonResponse({
                        "reason": "status_code is required"
                    }, status=400)
                else:
                    return JsonResponse({}, status=203)

            except ImageStorage.DoesNotExist:
                return JsonResponse({
                    "reason": "Image id: {} not found".format(image_id)
                }, status=404)
        else:
            return JsonResponse({
                "reason": "form_id is required"
            }, status=400)


image_store_API = ImageStore()
