"""
Vues d'authentification : connexion, déconnexion, inscription.

Ces vues sont accessibles sans être connecté. Toute autre page
redirige vers 'login' si l'utilisateur n'est pas authentifié
(via le décorateur @login_required dans les autres apps).
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout

from . import forms


def logout_user(request):
    """Déconnecte l'utilisateur et redirige vers la page de connexion."""
    logout(request)
    return redirect('login')


def login_page(request):
    """
    Affiche et traite le formulaire de connexion.

    En cas de succès : redirige vers le flux (feed).
    En cas d'échec  : réaffiche le formulaire avec un message d'erreur.
    """
    form = forms.LoginForm()
    message = ''

    if request.method == 'POST':
        form = forms.LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
            )
            if user is not None:
                login(request, user)
                return redirect('feed')
            else:
                message = "Identifiants invalides"

    return render(
        request,
        "authentication/login.html",
        context={'form': form, 'message': message},
    )


def signup_page(request):
    """
    Affiche et traite le formulaire d'inscription.

    Après inscription réussie, l'utilisateur est automatiquement
    connecté et redirigé vers son flux.
    """
    form = forms.SignupForm()

    if request.method == 'POST':
        form = forms.SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Connexion automatique après inscription
            login(request, user)
            return redirect('feed')

    return render(request, 'authentication/signup.html', context={'form': form})
