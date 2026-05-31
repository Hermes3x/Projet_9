"""
Formulaires de l'application blog : création de tickets, de critiques,
et suivi d'utilisateurs.
"""

from django import forms
from django.contrib.auth import get_user_model

from .models import Ticket, Review


class TicketForm(forms.ModelForm):
    """
    Formulaire de création / modification d'un ticket.

    Expose uniquement les champs renseignables par l'utilisateur.
    Les champs 'user' et 'time_created' sont gérés dans la vue.
    """

    class Meta:
        model = Ticket
        fields = ["title", "description", "image"]
        labels = {
            "title": "Titre",
            "description": "Description",
            "image": "Image",
        }


class ReviewForm(forms.ModelForm):
    """
    Formulaire de création / modification d'une critique.

    Le champ 'rating' est rendu dans le template via un widget
    étoiles personnalisé (voir _review_form_fields.html).
    Les champs 'ticket' et 'user' sont gérés dans la vue.
    """

    class Meta:
        model = Review
        fields = ["headline", "body", "rating"]
        labels = {
            "headline": "Titre",
            "rating": "Note",
            "body": "Commentaire",
        }


User = get_user_model()


class FollowUserForm(forms.Form):
    """
    Formulaire simple pour suivre un utilisateur via son nom d'utilisateur.

    La validation de l'existence de l'utilisateur est effectuée dans la vue,
    car elle nécessite un accès à la base de données.
    """

    username = forms.CharField(label="Nom d'utilisateur", max_length=150)
