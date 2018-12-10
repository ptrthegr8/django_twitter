from django.db import models
from django.contrib.auth.models import User


class TwitterUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    following = models.ManyToManyField(
        'self', symmetrical=False, blank=True
    )
    creation_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username


class Tweet(models.Model):
    user = models.ForeignKey(TwitterUser, on_delete=models.CASCADE)
    text = models.CharField(max_length=140)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text


class Notification(models.Model):
    user = models.ForeignKey(
        TwitterUser, on_delete=models.CASCADE
    )
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.tweet.text
