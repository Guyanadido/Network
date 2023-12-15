
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("newPost", views.new_post, name="newPost"),
    path("posts", views.posts, name="posts"),
    path("user/<str:username>", views.user, name="user"),
    path("handleFollow", views.handleFollow, name="handleFollow"),
    path("following", views.following, name="following"),
    path("Edit", views.Edit, name="edit"),
    path("addLike", views.addLike, name="addLike"),
]
