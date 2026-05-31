"""
Vues de l'application blog.

Gère les fonctionnalités principales de LITReview :
- Flux personnalisé (feed)
- Création, modification et suppression de tickets
- Création, modification et suppression de critiques
- Gestion des abonnements (suivre / se désabonner)

Toutes les vues requièrent d'être connecté (@login_required).
"""

from itertools import chain

from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.db.models import CharField, Value, Q
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from .forms import TicketForm, ReviewForm, FollowUserForm
from .models import Ticket, Review, UserFollows


# ---------------------------------------------------------------------------
# Critiques
# ---------------------------------------------------------------------------

@login_required
def review_create(request):
    """
    Crée un ticket et une critique en une seule étape.

    Permet à un utilisateur de publier directement une critique
    sans qu'un ticket existe au préalable.
    Les deux formulaires sont validés ensemble : si l'un est invalide,
    aucun enregistrement n'est sauvegardé.
    """
    if request.method == "POST":
        ticket_form = TicketForm(request.POST, request.FILES)
        review_form = ReviewForm(request.POST)
        if ticket_form.is_valid() and review_form.is_valid():
            # Sauvegarde du ticket en attribuant l'utilisateur courant
            ticket = ticket_form.save(commit=False)
            ticket.user = request.user
            ticket.save()

            # Sauvegarde de la critique liée au ticket qui vient d'être créé
            review = review_form.save(commit=False)
            review.ticket = ticket
            review.user = request.user
            review.save()

            return redirect('feed')
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
    """
    Crée une critique en réponse à un ticket existant.

    Le ticket est récupéré depuis l'URL ; s'il n'existe pas, renvoie 404.
    """
    ticket = get_object_or_404(Ticket, id=ticket_id)

    if request.method == "POST":
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.ticket = ticket
            review.user = request.user
            review.save()
            return redirect('feed')
    else:
        review_form = ReviewForm()

    context = {
        "ticket": ticket,
        "review_form": review_form,
    }
    return render(request, "blog/review_reply.html", context)


@login_required
def review_update(request, review_id):
    """
    Modifie une critique existante.

    La vérification user=request.user dans get_object_or_404 empêche
    un utilisateur de modifier la critique d'un autre (renvoie 404).
    """
    review = get_object_or_404(Review, id=review_id, user=request.user)
    ticket = review.ticket  # ticket lié à la critique

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
@require_POST  # Suppression uniquement via POST (protection CSRF)
def review_delete(request, review_id):
    """
    Supprime une critique.

    Seul l'auteur peut supprimer sa critique (user=request.user).
    @require_POST garantit que la suppression ne peut pas être
    déclenchée par un simple lien GET.
    """
    review = get_object_or_404(Review, id=review_id, user=request.user)
    review.delete()
    return redirect('posts_list')


# ---------------------------------------------------------------------------
# Tickets
# ---------------------------------------------------------------------------

@login_required
def ticket_create(request):
    """
    Crée un nouveau ticket (demande de critique).

    L'utilisateur courant est automatiquement défini comme auteur du ticket.
    """
    if request.method == "POST":
        form = TicketForm(request.POST, request.FILES)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            return redirect('feed')
    else:
        form = TicketForm()

    return render(request, 'blog/ticket_form.html', {"form": form})


@login_required
def ticket_update(request, ticket_id):
    """
    Modifie un ticket existant.

    La vérification user=request.user dans get_object_or_404 empêche
    un utilisateur de modifier le ticket d'un autre (renvoie 404).
    """
    ticket = get_object_or_404(Ticket, id=ticket_id, user=request.user)

    if request.method == "POST":
        form = TicketForm(request.POST, request.FILES, instance=ticket)
        if form.is_valid():
            form.save()  # L'auteur ne change pas : instance déjà liée
            return redirect('feed')
    else:
        form = TicketForm(instance=ticket)

    return render(request, 'blog/ticket_form.html', {"form": form})


@login_required
@require_POST  # Suppression uniquement via POST (protection CSRF)
def ticket_delete(request, ticket_id):
    """
    Supprime un ticket et ses critiques associées (CASCADE en base).

    Seul l'auteur peut supprimer son ticket.
    """
    ticket = get_object_or_404(Ticket, id=ticket_id, user=request.user)
    ticket.delete()
    return redirect('posts_list')


# ---------------------------------------------------------------------------
# Liste des posts de l'utilisateur
# ---------------------------------------------------------------------------

@login_required
def posts_list(request):
    """
    Affiche les tickets et critiques publiés par l'utilisateur connecté,
    triés du plus récent au plus ancien.
    """
    tickets = Ticket.objects.filter(user=request.user).order_by('-time_created')
    reviews = Review.objects.filter(user=request.user).order_by('-time_created')

    context = {
        "tickets": tickets,
        "reviews": reviews,
    }
    return render(request, "blog/posts_list.html", context)


# ---------------------------------------------------------------------------
# Abonnements
# ---------------------------------------------------------------------------

User = get_user_model()


@login_required
def subscriptions(request):
    """
    Affiche la page de gestion des abonnements :
    - liste des utilisateurs suivis (avec option de désabonnement)
    - liste des utilisateurs qui suivent l'utilisateur connecté
    - formulaire pour suivre un nouvel utilisateur
    """
    # Utilisateurs que l'on suit
    following_relations = UserFollows.objects.filter(user=request.user)
    following = [rel.followed_user for rel in following_relations]

    # Utilisateurs qui nous suivent
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
    """
    Traite le formulaire de suivi d'un utilisateur.

    Vérifie que :
    - l'utilisateur cible existe en base
    - l'utilisateur ne tente pas de se suivre lui-même
    get_or_create évite les doublons si l'abonnement existe déjà.
    """
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

            # get_or_create : crée l'abonnement seulement s'il n'existe pas déjà
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
    """
    Se désabonner d'un utilisateur.

    Supprime la relation UserFollows correspondante.
    Si elle n'existe pas, .delete() ne lève pas d'erreur.
    """
    to_unfollow = get_object_or_404(User, id=user_id)
    UserFollows.objects.filter(
        user=request.user,
        followed_user=to_unfollow,
    ).delete()
    return redirect('subscriptions')


# ---------------------------------------------------------------------------
# Flux
# ---------------------------------------------------------------------------

@login_required
def feed(request):
    """
    Construit et affiche le flux personnalisé de l'utilisateur connecté.

    Le flux contient, sans doublon et trié du plus récent au plus ancien :
    - ses propres tickets et critiques
    - les tickets et critiques des utilisateurs qu'il suit
    - les critiques en réponse à ses tickets, même de non-suivis

    On utilise annotate() pour ajouter un champ 'content_type' directement
    dans la requête SQL, ce qui permet au template de distinguer tickets
    et critiques avec {% if post.content_type == 'TICKET' %}.
    Voir l'appendice du cahier des charges pour le pattern recommandé.
    """
    # IDs des utilisateurs suivis (1 seule requête SQL)
    followed_users = UserFollows.objects.filter(
        user=request.user
    ).values_list('followed_user', flat=True)

    # Tickets : les miens + ceux des utilisateurs suivis
    tickets = Ticket.objects.filter(
        Q(user=request.user) | Q(user__in=followed_users)
    ).annotate(content_type=Value('TICKET', CharField()))

    # Critiques : les miennes + celles des suivis + celles sur mes tickets (même de non-suivis)
    # .distinct() évite les doublons quand plusieurs conditions Q matchent le même objet
    reviews = Review.objects.filter(
        Q(user=request.user) |
        Q(user__in=followed_users) |
        Q(ticket__user=request.user)
    ).distinct().annotate(content_type=Value('REVIEW', CharField()))

    # Combinaison des deux querysets et tri antéchronologique
    posts = sorted(
        chain(tickets, reviews),
        key=lambda post: post.time_created,
        reverse=True,
    )

    return render(request, 'blog/feed.html', context={'posts': posts})
