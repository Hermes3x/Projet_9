"""
Formulaires d'authentification : connexion et inscription.
"""

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm


class LoginForm(forms.Form):
    """Formulaire de connexion (username + mot de passe)."""

    username = forms.CharField(max_length=63, label="Nom d'utilisateur")
    password = forms.CharField(max_length=63, widget=forms.PasswordInput, label="Mot de passe")


class SignupForm(UserCreationForm):
    """
    Formulaire d'inscription.

    Étend UserCreationForm (qui gère la double saisie et la validation
    du mot de passe) en y ajoutant les champs propres à notre modèle User.
    """

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ('username', 'email', 'first_name', 'last_name')
