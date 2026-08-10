import json

from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from urllib3 import request
from django.core.paginator import Paginator

from .models import User, Post, Follow


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


def posts(request):
    #Get all posts
    if request.method == "GET":
        posts = Post.objects.all().order_by("-timestamp")
        posts_data = []
        post_paginator = Paginator(posts, 10) #10 posts per 1 page
        current_page = request.GET.get("page")
        posts_page = post_paginator.get_page(current_page)

        for post in posts_page:
            posts_data.append({
                "id": post.id,
                "user": post.user.username,
                "content": post.content,
                "timestamp": post.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "likes_count": post.likes_count,
                "liked_by_user": request.user in post.likes.all(),
                "is_owner": request.user == post.user,
                "is_authenticated": request.user.is_authenticated
            })

        return JsonResponse({
            "posts": posts_data, 
            "current_page": posts_page.number, 
            "num_pages": post_paginator.num_pages, 
            "has_next": posts_page.has_next(), 
            "has_previous": posts_page.has_previous()
        })
    #Create a new post
    elif request.method == "POST":

        if not request.user.is_authenticated:
            return JsonResponse({"error": "Login required"}, status=401)

        data = json.loads(request.body)
        content = data.get("content", "").strip()

        if not content:
            return JsonResponse({"error": "Post content cannot be empty."}, status=400)
        
        post = Post.objects.create(user=request.user, content=content)

        return JsonResponse({
            "message": "Post created.",
            "post_id": post.id
        }, status=201)
    
    else:
        return JsonResponse({"error": "GET/POST request required."}, status=405)


def profile(request, username):
    profile_user = User.objects.get(username=username)

    posts = profile_user.posts.all().order_by("-timestamp")
    post_paginator = Paginator(posts, 10)
    current_page = request.GET.get("page")
    posts_page = post_paginator.get_page(current_page)

    followers_count = profile_user.followers.count()
    following_count = profile_user.following.count()

    #Follow/Unfollow status
    is_following = False
    if request.user.is_authenticated:
        is_following = Follow.objects.filter(follower=request.user, following=profile_user).exists()

    return render(request, "network/profile.html", {
        "profile_user": profile_user, 
        "posts": posts_page,
        "followers_count": followers_count, 
        "following_count": following_count,
        "is_following": is_following
    })


@login_required
def follow(request, username):
    profile_user = User.objects.get(username=username)
    
    if request.user != profile_user:
        Follow.objects.get_or_create(follower=request.user, following=profile_user)

    return redirect("profile", username=username)


@login_required
def unfollow(request, username):
    profile_user = User.objects.get(username=username)

    if request.user != profile_user:
        Follow.objects.filter(follower=request.user, following=profile_user).delete()

    return redirect("profile", username=username)


#need refatoring(posts and following_posts)
@login_required        
def following_posts(request):

    following_users = Follow.objects.filter(follower=request.user).values_list("following", flat=True)
    posts = Post.objects.filter(user__in=following_users).order_by("-timestamp")
    posts_data = []
    
    post_paginator = Paginator(posts, 10)
    current_page = request.GET.get("page")
    posts_page = post_paginator.get_page(current_page)

    for post in posts_page: 
        posts_data.append({
            "id": post.id,
            "user": post.user.username,
            "content": post.content,
            "timestamp": post.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "likes_count": post.likes_count,
            "liked_by_user": request.user in post.likes.all(),
            "is_authenticated": request.user.is_authenticated,
            "is_owner": request.user == post.user
        })

    return JsonResponse({
        "posts": posts_data,
        "has_previous": posts_page.has_previous(),
        "has_next": posts_page.has_next(),
        "current_page": posts_page.number,
        "num_pages": post_paginator.num_pages
    })


@login_required
def following_page(request):
    return render(request, "network/following.html")



@login_required
def edit_post(request, post_id):

    if request.method != "PUT":
        return JsonResponse({"error": "PUT request required."}, status=405)
    
    post = get_object_or_404(Post, id=post_id)

    if request.user != post.user:
        return JsonResponse({"error": "You are not authorized"}, status=403)
        
    data = json.loads(request.body)
    content = data.get("content", "").strip()

    if not content: 
        return JsonResponse({"error": "Post content cannot be empty."}, status=400)

    post.content = content
    post.save()

    return JsonResponse({"message": "Post updated."})


@login_required
def like_post(request, post_id):

    if request.method != "PUT":
        return JsonResponse({"error": "PUT request required."}, status=405)

    post = get_object_or_404(Post, id=post_id)

    #Toggle like or unlike
    if request.user in post.likes.all():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)

    return JsonResponse({
        "likes_count": post.likes.count(),
        "liked_by_user": request.user in post.likes.all()
        })  