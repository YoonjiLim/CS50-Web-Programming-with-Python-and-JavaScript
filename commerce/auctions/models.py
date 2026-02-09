from django.contrib.auth.models import AbstractUser
from django.db import models

    
class User(AbstractUser):
    #A user can watch multiple listings
    #A listing can be watched by multiple users
    watchlist = models.ManyToManyField(
        "Listing",
        blank=True,
        related_name="watchers"
    )

class Listing(models.Model):
    #Each listing can have multiple bids and comments
    title = models.CharField(max_length=80)
    description = models.TextField()
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.URLField(blank=True)
    category = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    owner = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name="listings"
    )

    def __str__(self):
        return self.title


class Bid(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    bidder = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name="bids"
    )
    
    #Listing on which the bid was placed
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name="bids"
    )

    def __str__(self):
        return f"{self.amount} by {self.bidder}"

class Comment(models.Model):
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE, 
        related_name="comments"
    )

    #Listing to which the comment belongs
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name="comments"
    )

    def __str__(self):
        return f"Comment by {self.author} on {self.listing}"
