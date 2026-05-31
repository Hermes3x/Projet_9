"""
Modèle utilisateur personnalisé pour l'application LITReview.

On étend AbstractUser (fourni par Django) plutôt que d'utiliser User directement,
ce qui permet d'ajouter des champs sans réécrire toute la logique d'authentification
(mots de passe, sessions, permissions…).

Le modèle est déclaré dans settings.py via AUTH_USER_MODEL = 'authentication.User'.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Utilisateur de l'application LITReview.

    Hérite de tous les champs standard Django (username, email,
    password, first_name, last_name…) et ajoute deux champs
    prévus pour de futures évolutions du projet :
    - profile_photo : photo de profil de l'utilisateur
    - role          : distinction créateur / abonné
    """

    CREATOR = 'CREATOR'
    SUBSCRIBER = 'SUBSCRIBER'

    ROLE_CHOICES = (
        (CREATOR, 'Créateur'),
        (SUBSCRIBER, 'Abonné'),
    )

    # Photo de profil optionnelle (non exposée dans l'UI de cette version)
    profile_photo = models.ImageField(
        verbose_name='Photo de profil',
        blank=True,
        null=True,
    )

    # Rôle de l'utilisateur — prévu pour différencier créateurs et abonnés,
    # non exploité dans la logique métier de cette version
    role = models.CharField(
        max_length=30,
        choices=ROLE_CHOICES,
        verbose_name='Rôle',
        default=SUBSCRIBER,
    )
