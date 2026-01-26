from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("search/", views.search, name="search"),
    path("new/", views.new, name="new"),
    path("random/", views.random_page, name="random"),
    path("edit/<str:title>/", views.edit, name="edit"),
    path("<str:title>/", views.entry, name="entry")
]