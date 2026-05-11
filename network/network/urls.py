
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("posts", views.posts, name="posts"),
    path("editpost/<int:post_id>", views.edit_post, name="edit_post"),
    path("likepost/<int:post_id>/like", views.like_post, name="like_post"),
    path("profile/<str:username>", views.profile, name="profile"),
    path("follow/<str:username>", views.follow_user, name="follow_user"),
    path("following", views.following_posts, name="following_posts")
]