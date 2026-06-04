from django.urls import path
from apps.commandes.views import (
    CreerCommandeView,
    ListerMesCommandesView,
    DetailCommandeView,
    CommandesEntrantesView,
    ToutesCommandesView,
    MajStatutCommandeView,
)

urlpatterns = [
    path('passer/commandes/', CreerCommandeView.as_view()),
    path('liste/commandes/', ListerMesCommandesView.as_view()),
    path('details/commandes/<str:id>/', DetailCommandeView.as_view()),
    path('commandes/entrantes/', CommandesEntrantesView.as_view()),
    path('commandes/toutes/', ToutesCommandesView.as_view()),
    path('commandes/<str:id>/statut/', MajStatutCommandeView.as_view()),
]