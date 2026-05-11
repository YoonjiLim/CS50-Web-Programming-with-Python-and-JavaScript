from django.contrib import admin
from .models import User, Post, Follow

# Register your models here.
admin.site.register(User)

class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "content", "timestamp")
    search_fields = ("content", "user__username")
admin.site.register(Post, PostAdmin)

class FollowAdmin(admin.ModelAdmin):
    list_display = ("follower", "following")
admin.site.register(Follow, FollowAdmin)