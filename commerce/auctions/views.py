from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from auctions.forms import ListingForm
from .models import Bid, Listing, User, Comment, Category
from decimal import Decimal


def index(request):
    listings = Listing.objects.filter(is_active=True)

    for listing in listings:
        highest_bid = listing.bids.order_by("-amount").first()
        listing.current_price = highest_bid.amount if highest_bid else listing.starting_bid
    
    return render(request, "auctions/index.html", {
        "listings": listings
    })


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
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


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
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def listing_detail(request, listing_id):
    error = None
    listing = get_object_or_404(Listing, pk=listing_id)
    
    is_watchlisted = False
    if request.user.is_authenticated:
        is_watchlisted = request.user.watchlist.filter(pk=listing.pk).exists()

    highest_bid = listing.bids.order_by("-amount").first()
    current_price = highest_bid.amount if highest_bid else listing.starting_bid
    highest_bidder = highest_bid.bidder if highest_bid else None

    #POST
    if request.method == "POST":
        action = request.POST.get("action")

        if action == "bid":
            if not request.user.is_authenticated: 
                return redirect("login")
            
            bid_raw = request.POST.get("bid")
            
            try:
                bid_amount = Decimal(bid_raw)
            except (TypeError, ValueError):
                error = "Invalid bid amount."
            else:
                if request.user == listing.owner:
                    error = "You cannot bid on your own listing."
                elif not listing.is_active:
                    error = "Auction is closed."
                elif bid_amount <= current_price:
                    error = f"Your bid must be higher than the ${current_price}."
                else:
                    Bid.objects.create(
                        listing=listing,
                        bidder=request.user,
                        amount=bid_amount
                    )
                    return redirect("listing_detail", listing_id=listing.id)
        
        elif action == "watchlist":

            if not request.user.is_authenticated:
                return redirect("login")
            
            if request.user.watchlist.filter(pk=listing.pk).exists():
                request.user.watchlist.remove(listing)
            else:
                request.user.watchlist.add(listing)

            return redirect("listing_detail", listing_id=listing.id)
        
        elif action == "comment":

            if not request.user.is_authenticated:
                return redirect("login")
            
            content = request.POST.get("comment")

            if content: 
                Comment.objects.create(
                    listing=listing,
                    author=request.user,
                    content=content
                )
            
            return redirect("listing_detail", listing_id=listing.id)
        
        elif action == "close":

            if (
                not request.user.is_authenticated
                or request.user != listing.owner
                or not listing.is_active
            ):
                return redirect("listing_detail", listing_id=listing.id)

            if highest_bid:
                listing.winner = highest_bid.bidder

            listing.is_active = False
            listing.save(update_fields=["winner", "is_active"])

            return redirect("listing_detail", listing_id=listing.id)
        
    #GET
    comments = listing.comments.all().order_by("-created_at")

    winner = listing.winner
    is_winner = False
    if (
        request.user.is_authenticated
        and not listing.is_active
        and listing.winner == request.user
    ):
        is_winner = True

    return render(request, "auctions/listing.html",{
        "listing": listing,
        "current_price": current_price,
        "error": error,
        "comments": comments,
        "is_winner": is_winner,
        "winner": winner,
        "is_watchlisted": is_watchlisted,
        "highest_bidder": highest_bidder
    }) 


@login_required
def create_listing(request):
    if request.method == "POST":
        form = ListingForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.owner = request.user
            listing.save()
            return redirect("listing_detail", listing_id=listing.id)
        
    else:
        form = ListingForm()

    return render(request, "auctions/create_listing.html", {
        "form": form
    })


@login_required
def watchlist(request):
    listings = request.user.watchlist.all()
    
    return render(request, "auctions/watchlist.html", {
        "listings": listings
    })


def categories(request):
    categories = Category.objects.all()

    return render(request, "auctions/categories.html", {
        "categories": categories
    })


def category_listings(request, category_id):
    category = get_object_or_404(Category, pk=category_id)

    listings = Listing.objects.filter(
        category=category,
        is_active=True
    )

    return render(request, "auctions/category_listings.html", {
        "category": category,
        "listings": listings
    })