from django.http import HttpResponseRedirect
from django.shortcuts import render, reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

from django_twitter.models import Tweet, TwitterUser
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
            return HttpResponseRedirect(reverse('homepage'))
    else:
        form = TweetForm(user=request.user)
    return render(request, html, {'form': form})


def user_profile(request, username):
    html = 'user-profile.html'
    targeted_user = User.objects.filter(username=username).first()
    targeted_twitter_user = TwitterUser.objects.get(user_id=targeted_user.id)
    current_user = TwitterUser.objects.get(user_id=request.user.id)
    data = {
        'user': targeted_twitter_user,
        'tweets': list(Tweet.objects.filter(user_id=targeted_user.id)),
        'tweet_count': len(
            list(Tweet.objects.filter(user_id=targeted_user.id))
        ),
        'follow_count': len(list(targeted_twitter_user.follows.all())),
        'followers': list(str(x) for x in targeted_twitter_user.follows.all()),
        'is_following': (
            True if str(request.user) in list(str(x)
                                              for x in current_user.follows.all()) else False
        )
    }
    print(data)
    print(request.user)
    if request.method == "POST":
        if request.POST.get('follow'):
            current_user.follows.add(
                targeted_twitter_user.id
            )
        elif request.POST.get('unfollow'):
            current_user.follows.remove(
                targeted_twitter_user
            )

    return render(request, html, {'data': data})


def tweet_details(request, tweet_id):
    html = 'tweet-details.html'
    data = Tweet.objects.get(pk=tweet_id)
    return render(request, html, {'data': data})
