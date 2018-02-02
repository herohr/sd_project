from sd_project.restful import FormParser
from sd_project.rd_session import sessions
from sd_project import models
from django.http import JsonResponse

def authorize(func):
    def _func(self, request):
        au = None
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