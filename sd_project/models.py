from django.db import models


class User(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=64, unique=True)
    password = models.CharField(max_length=256)
    email = models.CharField(max_length=256)
    verified = models.BooleanField(default=False)


class UserInfo(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField()

    nickname = models.CharField(max_length=64)
    sex = models.CharField(max_length=4)
    age = models.IntegerField()
    college = models.CharField(max_length=64)

    register_time = models.DateTimeField()
    last_login_time = models.DateTimeField()


class ImageStorage(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField(null=False)

    verified = models.BooleanField(default=False)
    oss_key = models.CharField(max_length=512, null=False)
    create_time = models.DateTimeField()