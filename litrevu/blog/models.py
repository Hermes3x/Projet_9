"""
Modèles de l'application blog : Ticket, Review, UserFollows.

- Ticket    : demande de critique publiée par un utilisateur
- Review    : critique rédigée en réponse à un ticket
- UserFollows : relation d'abonnement entre deux utilisateurs
"""

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Ticket(models.Model):
    """
    Billet de demande de critique.

    Un utilisateur crée un ticket pour solliciter l'avis d'autres
    utilisateurs sur un livre ou un article. D'autres utilisateurs
    peuvent ensuite y répondre par une Review.
    """

    title = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    # Image de couverture optionnelle (stockée dans MEDIA_ROOT)
    image = models.ImageField(null=True, blank=True)
    # Auteur du ticket — suppression en cascade si l'utilisateur est supprimé
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tickets',
    )
    # Date de création renseignée automatiquement à la sauvegarde
    time_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Review(models.Model):
    """
    Critique rédigée en réponse à un Ticket.

    Contient un titre (headline), un corps de texte (body),
    et une note de 0 à 5.
    """

    # Ticket auquel cette critique répond — suppression en cascade
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    # Note entre 0 et 5 (validée côté base de données et côté formulaire)
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)],
    )
    headline = models.CharField(max_length=128)
    # Corps de la critique (max 8192 caractères, conforme au cahier des charges)
    body = models.CharField(max_length=8192, blank=True)
    # Auteur de la critique
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    time_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.headline} - {self.rating}/5'


class UserFollows(models.Model):
    """
    Relation d'abonnement entre deux utilisateurs.

    'user' suit 'followed_user'. La contrainte unique_together
    empêche de créer deux fois le même abonnement.
    """

    # L'utilisateur qui s'abonne
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='following',
    )
    # L'utilisateur suivi
    followed_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='followers',
    )

    class Meta:
        # Un utilisateur ne peut pas suivre deux fois la même personne
        unique_together = ('user', 'followed_user')

    def __str__(self):
        return f'{self.user} suit {self.followed_user}'
