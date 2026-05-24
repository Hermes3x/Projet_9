from django import forms
from .models import Ticket, Review
from django.contrib.auth import get_user_model


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ["title", "description", "image"]
        labels = {
            "title": "Titre",
            "description": "Description",
            "image": "Image",
        }

class ReviewForm(forms.ModelForm):
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
    username = forms.CharField(label="Nom d'utilisateur", max_length=150)