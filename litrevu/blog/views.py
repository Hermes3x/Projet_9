from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from .forms import TicketForm, ReviewForm, FollowUserForm
from .models import Ticket, Review, UserFollows


@login_required
def home(request):
    return render(request, 'blog/home.html')


@login_required
def review_create(request):
    if request.method == "POST":
        ticket_form = TicketForm(request.POST, request.FILES)
        review_form = ReviewForm(request.POST)
        if ticket_form.is_valid() and review_form.is_valid():
            ticket = ticket_form.save(commit=False)
            ticket.user = request.user
            ticket.save()

            review = review_form.save(commit=False)
            review.ticket = ticket
            review.user = request.user
            review.save()

            return redirect('home')
    else:
        ticket_form = TicketForm()
        review_form = ReviewForm()

    context = {
        "ticket_form": ticket_form,
        "review_form": review_form,
    }
    return render(request, "blog/review_create.html", context)


@login_required
def review_reply(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    if request.method == "POST":
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():

            review = review_form.save(commit=False)
            review.ticket = ticket
            review.user = request.user
            review.save()

            return redirect('home')
    else:
        review_form = ReviewForm()

    context = {
        "ticket": ticket,
        "review_form": review_form,
    }
    return render(request, "blog/review_reply.html", context)


@login_required
def review_update(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    ticket = review.ticket  # ticket lié

    if request.method == "POST":
        review_form = ReviewForm(request.POST, instance=review)
        if review_form.is_valid():
            review_form.save()
            return redirect('posts_list')
    else:
        review_form = ReviewForm(instance=review)

    context = {
        "ticket": ticket,
        "review_form": review_form,
        "review": review,
    }
    return render(request, "blog/review_update.html", context)


@login_required
@require_POST
def review_delete(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    review.delete()
    return redirect('posts_list')


@login_required
def ticket_create(request):
    if request.method == "POST":
        form = TicketForm(request.POST, request.FILES)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            return redirect('home')
    else:
        form = TicketForm()
    return render(request, 'blog/ticket_form.html', {"form": form})


@login_required
def ticket_update(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id, user=request.user)
    if request.method == "POST":
        form = TicketForm(request.POST, request.FILES, instance=ticket)
        if form.is_valid():
            form.save()  # user ne change pas, instance déjà liée
            return redirect('home')
    else:
        form = TicketForm(instance=ticket)
    return render(request, 'blog/ticket_form.html', {"form": form})


@login_required
def posts_list(request):
    tickets = Ticket.objects.filter(user=request.user)
    reviews = Review.objects.filter(user=request.user)
    context = {
        "tickets": tickets,
        "reviews": reviews,
    }
    return render(request, "blog/posts_list.html", context)


@login_required
@require_POST
def ticket_delete(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id, user=request.user)
    ticket.delete()
    return redirect('posts_list')


User = get_user_model()


@login_required
def subscriptions(request):
    following_relations = UserFollows.objects.filter(user=request.user)
    following = [rel.followed_user for rel in following_relations]

    followers_relations = UserFollows.objects.filter(followed_user=request.user)
    followers = [rel.user for rel in followers_relations]

    form = FollowUserForm()

    context = {
        "following": following,
        "followers": followers,
        "form": form,
    }
    return render(request, "blog/subscriptions.html", context)


@login_required
def follow_user(request):
    if request.method == "POST":
        form = FollowUserForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]

            try:
                to_follow = User.objects.get(username=username)
            except User.DoesNotExist:
                messages.error(request, "Cet utilisateur n'existe pas.")
                return redirect('subscriptions')

            if to_follow == request.user:
                messages.error(request, "Vous ne pouvez pas vous suivre vous-même.")
                return redirect('subscriptions')

            UserFollows.objects.get_or_create(
                user=request.user,
                followed_user=to_follow,
            )
            messages.success(request, f"Vous suivez maintenant {to_follow.username}.")
            return redirect('subscriptions')

    return redirect('subscriptions')


@login_required
@require_POST
def unsubscribe(request, user_id):
    to_unfollow = get_object_or_404(User, id=user_id)
    UserFollows.objects.filter(
        user=request.user,
        followed_user=to_unfollow
    ).delete()
    return redirect('subscriptions')


@login_required
def feed(request):

    followed_users = []
    following_relations = UserFollows.objects.filter(user=request.user)
    for relation in following_relations:
        followed_user = relation.followed_user
        followed_users.append(followed_user)

    my_tickets = []
    tickets = Ticket.objects.filter(user=request.user)
    for ticket in tickets:
        ticket.content_type = "TICKET"
        my_tickets.append(ticket)

    my_review = []
    reviews = Review.objects.filter(user=request.user)
    for review in reviews:
        review.content_type = "REVIEW"
        my_review.append(review)

    all_followed_tickets = []
    for user in followed_users:
        followed_user_tickets = Ticket.objects.filter(user=user)
        for ticket in followed_user_tickets:
            ticket.content_type = "TICKET"
            all_followed_tickets.append(ticket)

    all_followed_reviews = []
    for user in followed_users:
        followed_user_review = Review.objects.filter(user=user)
        for review in followed_user_review:
            review.content_type = "REVIEW"
            all_followed_reviews.append(review)

    my_tickets_reviews = []
    reviews = Review.objects.filter(ticket__in=my_tickets).exclude(user=request.user, user__in=followed_users)
    for review in reviews:
        review.content_type = "REVIEW"
        my_tickets_reviews.append(review)

    feed_content = my_tickets + my_review + all_followed_tickets + all_followed_reviews + my_tickets_reviews
    posts = sorted(feed_content, key=lambda obj: obj.time_created, reverse=True)

    context = {"posts": posts}

    return render(request, "blog/feed.html", context)
