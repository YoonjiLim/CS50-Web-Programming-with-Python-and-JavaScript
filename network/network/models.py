from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q, F


class User(AbstractUser):
    pass

class Post(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name="posts"
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(
        User, 
        related_name="liked_posts",
        blank=True
    )

    def __str__(self):
        return f"{self.user} - {self.content[:30]}"
    
    @property
    def likes_count(self):
        return self.likes.count()
    

class Follow(models.Model):
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following"
    )
    following = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name="followers"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["follower", "following"],
                name="follow_constraint"
            ),
            models.CheckConstraint(
                check=~Q(follower=F("following")),
                name="prevent_self_follow"
            )
        ]
    
    def __str__(self):
        return f"{self.follower} follows {self.following}"