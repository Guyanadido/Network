from django.contrib.auth.models import AbstractUser
from django.db import models
import datetime


class User(AbstractUser):
    def __str__(self):
        return f"{self.username}"

    def natural_key(self):
        return (self.username, self.email)


class Post(models.Model):
    user = models.ForeignKey(
        User, null=False, blank=False, on_delete=models.CASCADE, related_name="posts")
    content = models.TextField()
    date = models.DateField(default=datetime.datetime.now())

    def to_json(self):
        data = {
            'id': self.id,
            'content': self.content,
            'date': self.date,
            'user': {
                'id': self.user.id,
                'username': self.user.username,
                'email': self.user.email,
            }
        }

        return data

    def __str__(self):
        return f"{self.user} posted, '{self.content}'"


class Comments(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_comments")
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField()
    TimeStamp = models.DateTimeField(auto_now_add=True)


class Likes(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_likes")
    TimeStamp = models.DateTimeField(auto_now_add=True)


class Flollow(models.Model):
    followingUser = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="follows")
    followedUser = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="followers")

    class Meta:
        unique_together = ("followingUser", "followedUser")

    def __str__(self):
        return f"{self.followingUser} follows {self.followedUser}"
