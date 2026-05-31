# utilisateurs/urls/auth.py
from django.urls import path
from utilisateurs.views.auth import (
    ConnexionView,
    DeconnexionView,
    ProfilView,
    ChangerMotDePasseView,
    MotDePasseOublieView,
    ReinitialiserMotDePasseView,
)

urlpatterns = [
    path('connexion/', ConnexionView.as_view(), name='auth-connexion'),
    path('deconnexion/', DeconnexionView.as_view(), name='auth-deconnexion'),
    path('details/profil/', ProfilView.as_view(), name='auth-profil'),
    path('modifier/profil/', ProfilView.as_view(), name='auth-modifier-profil'),
    path('changer-mot-de-passe/', ChangerMotDePasseView.as_view(), name='auth-changer-mdp'),
    path('mot-de-passe-oublie/', MotDePasseOublieView.as_view(), name='auth-mdp-oublie'),
    path('reinitialiser-mdp/', ReinitialiserMotDePasseView.as_view(), name='auth-reinitialiser-mdp'),
]
