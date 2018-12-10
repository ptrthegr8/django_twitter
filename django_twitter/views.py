import re

from django.http import HttpResponseRedirect
from django.shortcuts import render, reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

from django_twitter.models import Tweet, TwitterUser, Notification
from django_twitter.forms import LoginForm, SignupForm, TweetForm


@login_required()
def homepage(request):
    html = 'homepage.html'
    data = Tweet.objects.all()
    return render(request, html, {'data': data})


def login_user(request):
    next_page = request.GET.get('next')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = authenticate(
                username=data['username'],
                password=data['password']
            )
            if user is not None:
                login(request, user)
                if next_page:
                    return HttpResponseRedirect(next_page)
                else:
                    return HttpResponseRedirect(reverse('homepage'))
    else:
        form = LoginForm()
        return render(request, 'login.html', {'form': form, 'next': next_page})


def logout_user(request):
    logout(request)
    return HttpResponseRedirect(reverse('homepage'))


def signup_user(request):
    html = 'signup.html'
    form = SignupForm(None or request.POST)

    if form.is_valid():
        data = form.cleaned_data
        user = User.objects.create_user(
            data['username'],
            data['email'],
            data['password']
        )
        TwitterUser.objects.create(user=user)
        login(request, user)
        return HttpResponseRedirect(reverse('homepage'))
    return render(request, html, {'form': form})


def tweet_add(request):
    html = 'tweet-form.html'
    if request.method == 'POST':
        form = TweetForm(request.user, request.POST)
        if form.is_valid():
            data = form.cleaned_data
            Tweet.objects.create(
                user=TwitterUser.objects.filter(user_id=data['user']).first(),
                text=data['text']
            )
            if '@' in data['text']:
                users = re.findall(r'@(\w+)', data['text'])
                for user in users:
                    Notification.objects.create(
                        user=TwitterUser.objects.get(user__username=user),
                    )

            return HttpResponseRedirect(reverse('homepage'))
    else:
        form = TweetForm(user=request.user)
    return render(request, html, {'form': form})


def user_profile(request, username):
    html = 'user-profile.html'
    targeted_user = User.objects.filter(username=username).first()
    targeted_twitter_user = TwitterUser.objects.get(user_id=targeted_user.id)
    current_twitter_user = TwitterUser.objects.get(user_id=request.user.id)
    data = {
        'user': targeted_twitter_user,
        'tweets': list(Tweet.objects.filter(user_id=targeted_user.id)),
        'tweet_count': Tweet.objects.filter(user_id=targeted_user.id).count,
        'follow_count': targeted_twitter_user.following.all().count,
        'following': list(str(x) for x in current_twitter_user.following.all()),
        'is_following': (
            True if targeted_twitter_user
            in current_twitter_user.following.all() else False
        )
    }
    if request.method == "POST":
        if targeted_twitter_user != current_twitter_user:
            if request.POST.get('follow'):
                current_twitter_user.following.add(
                    targeted_twitter_user
                )
            elif request.POST.get('unfollow'):
                current_twitter_user.following.remove(
                    targeted_twitter_user
                )
        return HttpResponseRedirect('/{}/'.format(username))

    return render(request, html, {'data': data})


def tweet_details(request, tweet_id):
    html = 'tweet-details.html'
    data = Tweet.objects.get(pk=tweet_id)
    return render(request, html, {'data': data})
