from sd_project import models
from django.http import JsonResponse, QueryDict
from sd_project.rd_session import sessions
from django.utils import timezone
from sd_project import restful
from sd_project.restful import FormParser


def authorize(func):
    def _func(self, request):
        au = None
        # if request.method == "POST":
        #     au = request.POST.get("authorization")
        if request.method in {"POST", "GET"}:
            au = au or request.COOKIES.get("sessionID") or request.GET.get("authorization") or \
             request.POST.get("authorization")
        else:
            form = FormParser(request)
            au = form.get("authorization")
            setattr(request, "form", form)
        user_id = sessions.get(au)
        if user_id is not None:
            try:
                user = models.User.objects.get(id=user_id)
                setattr(request, "user", user)
                return func(self, request)
            except models.User.DoesNotExist:
                pass

        return JsonResponse({
            "reason": "authorize failed"
        }, status=401)

    return _func


class UserAPI(restful.RESTFul):
    def post(self, request):
        username = request.POST.get("username")
        password = request.POST.get("password")
        email = request.POST.get("email")

        tags = []
        if len(username) > 64:
            tags.append("username")
        if len(password) > 256:
            tags.append("password")
        if len(email) > 256:
            tags.append("email")
        if tags:
            return JsonResponse({
                "reason": "{} is too long".format(",".join(tags)),
                "tags": tags
            }, status=400)

        try:
            models.User.objects.filter(username=username).get()
        except models.User.DoesNotExist:
            new_user = models.User(username=username, password=password, email=email)
            new_user.save()
            return JsonResponse({}, status=200)
        except models.User.MultipleObjectsReturned:
            pass

        return JsonResponse({
            "reason": "Username already exist"
        }, status=409)


class UserInfoAPI(restful.RESTFul):
    @authorize
    def get(self, request):
        get_id = request.GET.get("id") or request.user.id
        try:
            user = models.UserInfo.objects.get(user_id=get_id)
        except models.UserInfo.DoesNotExist:
            return JsonResponse({
                "reason": "User's info does not exist"
            }, status=400)

        return JsonResponse({
            "sex": user.sex,
            "college": user.college,
            "nickname": user.nickname,
            "age": user.age,
            "user_id": user.user_id,
        }, status=200)

    @authorize
    def post(self, request):
        try:
            models.UserInfo.objects.get(user_id=request.user.id)
            return JsonResponse({
                "reason": "The user's info already exist"
            }, status=400)
        except models.UserInfo.DoesNotExist:
            nickname = request.POST.get("nickname")
            sex = request.POST.get("sex")
            if sex == "male":
                sex = "m"
            else:
                sex = "f"
            age = request.POST.get("age")
            college = request.POST.get("college")

            register_time = timezone.now()
            last_login_time = timezone.now()

            user_info = models.UserInfo(
                user_id=request.user.id,
                nickname=nickname,
                sex=sex,
                age=age,
                college=college,
                register_time=register_time,
                last_login_time=last_login_time
            )
            user_info.save()

            return JsonResponse({}, status=200)

    @authorize
    def put(self, request):
        form = FormParser(request)
        changed = []
        not_allowed = []
        userinfo = models.UserInfo.objects.get(user_id=request.user.id)

        def try_to_int(x):
            try:
                return int(x)
            except ValueError:
                return 0

        change = {
            "nickname": [None, lambda x: len(x) < 64],
            "sex": [None, lambda x: x in ("male", "female")],
            "age": [None, try_to_int],
            "college": [None, lambda x: len(x) < 64]
        }
        for key in change.keys():
            val = form.get(key)
            if val:
                if change[key][1](val):
                    change[key][0] = val
                else:
                    not_allowed.append(key)
        if not_allowed:
            return JsonResponse({
                "not_allowed": not_allowed
            }, 400)
        for key, val in change.items():
            if val[0] is not None:
                userinfo.__setattr__(key, val[0])
                changed.append(key)

        userinfo.save()
        return JsonResponse({"changed": changed}, status=200)


userAPI = UserAPI()
user_info_API = UserInfoAPI()


def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if username is None or password is None:
            return JsonResponse({
                "reason": "Need username and password",
            }, status=400)

        try:
            result = models.User.objects.get(username=username, password=password)
        except models.User.DoesNotExist:
            return JsonResponse({
                "reason": "Username or password wrong!",
            }, status=400)

        uuid = sessions.create_session(_id=result.id)
        resp = JsonResponse({
            "authorization": uuid
        }, status=200)
        resp.set_cookie("sessionID", uuid)
        return resp

    else:
        return JsonResponse({}, status=405)