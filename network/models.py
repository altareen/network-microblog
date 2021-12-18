from django.contrib.auth.models import AbstractUser
from django.db import models


class Person(models.Model):
    user_id = models.IntegerField(default=0)


class User(AbstractUser):
    followers = models.IntegerField(default=0)
    following = models.ManyToManyField(Person, blank=True, related_name="individual")


class Post(models.Model):
    content = models.TextField()
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="individual")
    timestamp = models.DateTimeField()
    likes = models.ManyToManyField(User, blank=True, related_name="desirable")


