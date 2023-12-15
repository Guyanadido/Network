from django.contrib.auth import authenticate, login, logout
from django.core.serializers import serialize
from django.db import IntegrityError
from django.db.models import Prefetch
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from datetime import datetime
import json
from django.core.paginator import Paginator


from .models import User, Post, Comments, Likes, Flollow


def index(request):
    return render(request, "network/index.html")


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


def new_post(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            # extract info sent by the browser
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({"error": "Invalid json data in the request body"})

            content = data.get('content')
            user = request.user
            timestamp = datetime.now()

            # check post validity
            valid = user and content
            if not valid:
                return JsonResponse({
                    'error': 'content not valid'
                })
            else:
                Post.objects.create(user=user, content=content, date=timestamp)
                return JsonResponse({
                    'success': 'posts added successfully'
                })
        else:
            return JsonResponse({
                'error': 'request not valid'
            })
    else:
        return HttpResponseRedirect(reverse(login))


def posts(request):
    posts = Post.objects.select_related("user").all().order_by("-date")
    if request.user.is_authenticated:
        signedUser = request.user
        likedPosts = list(signedUser.user_likes.values_list('post', flat=True))
    else:
        likedPosts = []
    page = Paginator(posts, 10)
    num_pages = page.num_pages
    pagelist = request.GET.get('page')
    if int(pagelist) not in range(1, num_pages+1):
        return JsonResponse({
            "error": "page doesn't exist",
        })
    page = page.get_page(pagelist)
    serialized_posts = [post.to_json() for post in page]

    response_data = {
        'posts': serialized_posts,
        'num_pages': num_pages,
        'current_page': pagelist,
        'liked_posts': likedPosts,
    }

    return JsonResponse(response_data, safe=False)


def user(request, username):
    if request.user.is_authenticated:
        user = User.objects.get(username=username)
        signedUser = request.user
        likedPosts = list(signedUser.user_likes.values_list('post', flat=True))

        # checking if the signeduser can follow the profileOwner
        followStatus = [True, True]
        if user == request.user:
            followStatus[0] = False

        followStatus[1] = not (request.user.follows.filter(
            followedUser=user).exists())

        follows = user.follows.count()
        followers = user.followers.count()
        userPost = user.posts.all()
        return JsonResponse({'liked_posts': likedPosts,
                             'follows': follows,
                             'followers': followers,
                             'followStatus': followStatus,
                             'posts': {'posts': [{
                                 'id': post.id,
                                 'content': post.content,
                                 'date': post.date,
                                 'user': {
                                     'username': post.user.username,
                                     'email': post.user.email,
                                 }
                             } for post in userPost]}
                             })
    else:
        return JsonResponse({
            'loggedout': 'please login first'
        })


def handleFollow(request):
    if request.user.is_authenticated:
        signedUser = request.user
        data = json.loads(request.body)
        username = data.get('username')
        followstatus = data.get('followstatus')
        profileOwner = User.objects.get(username=username)

        if not followstatus:
            Flollow.objects.get(followingUser=signedUser,
                                followedUser=profileOwner).delete()
            return JsonResponse({
                'sucess': f'you unfollowed {username}'
            })
        else:
            exist = Flollow.objects.filter(followingUser=signedUser,
                                           followedUser=profileOwner).exists()
            if exist:
                return JsonResponse({
                    'error': f'you already follow {username}'
                })
            newfollower = Flollow.objects.create(
                followingUser=signedUser, followedUser=profileOwner)
            newfollower.save()
            return JsonResponse({
                'sucess': f'you followed {username}'
            })
    else:
        return JsonResponse({
            'loggedout': 'please login first'
        })


def following(request):
    if request.user.is_authenticated:
        signedUser = request.user
        follows = Flollow.objects.filter(followingUser=signedUser)
        signedUser = request.user
        likedPosts = list(signedUser.user_likes.values_list('post', flat=True))

        # fetch all posts of user follows
        allFollowedUsers = [follow.followedUser for follow in follows]
        allPosts = Post.objects.filter(
            user__in=allFollowedUsers).prefetch_related('user').order_by('-date')

        # preparing json data to return
        return JsonResponse({
            'liked_posts': likedPosts,
            'posts': [{
                'id': post.id,
                'content': post.content,
                'date': post.date,
                'user': {
                    'username': post.user.username,
                    'email': post.user.email
                }
            } for post in allPosts]
        })
    else:
        return JsonResponse({
            'loggedout': 'please login first'
        })


def Edit(request):
    if request.user.is_authenticated:
        if request.method == 'PUT':
            try:
                body = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({
                    'error': 'body contain not valid json'
                })
            postId = body['postId']
            toBeEditedPost = Post.objects.get(pk=postId)
            if toBeEditedPost:
                toBeEditedPost.content = body['newPost']
                toBeEditedPost.save()
                return JsonResponse({
                    'success': 'post sucessfully updated'
                }, status=200)
            else:
                JsonResponse({
                    'error': 'post not found'
                }, status=404)
        else:
            return JsonResponse({
                'error': 'inapproprate request'
            }, status=304)
    else:
        return JsonResponse({
            'loggedout': 'please login first'
        })


def addLike(request):
    if request.user.is_authenticated:
        if request.method == 'PUT':
            # retriving the liking and liked users
            signdUser = request.user
            body = json.loads(request.body)
            postId = int(body['postId'])

            # making sure if the record doesnt exist
            post = Post.objects.get(pk=postId)
            exist = Likes.objects.filter(post=post, user=signdUser)
            exist
            # adding the record if it doesn't and removing if it does
            if exist:
                exist.delete()
            else:
                newLike = Likes(post=post, user=signdUser)
                newLike.save()
            return JsonResponse({
                'success': 'request successfully completed'
            }, status=200)
        else:
            return JsonResponse({
                'error': 'inapproprate request'
            }, status=304)
    else:
        return JsonResponse({
            'loggedout': 'please login first'
        })
