from django.contrib import admin
from django_twitter.models import Tweet, Notification, TwitterUser

admin.site.register(Tweet)
admin.site.register(Notification)
admin.site.register(TwitterUser)
