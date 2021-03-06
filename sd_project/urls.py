"""sd_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from sd_project import user, image

urlpatterns = [
    path('admin/', admin.site.urls),

    path('users', user.userAPI.router(methods=["POST", ])),
    path('users/login', user.login),
    path('users/info', user.user_info_API.router(methods=["GET", "POST", "PUT"])),

    path("images", image.image_store_API.router(methods=["GET", "POST", "PUT"]))
]
