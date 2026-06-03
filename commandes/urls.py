from django.urls import path
from .views import (
    VoirPanierView,
    AjouterAuPanierView,
    ModifierLignePanierView,
    SupprimerLignePanierView,
    ViderPanierView,
)

urlpatterns = [
    path('panier/', VoirPanierView.as_view(), name='voir-panier'),
    path('panier/ajouter/', AjouterAuPanierView.as_view(), name='ajouter-panier'),
    path('panier/modifier/lignes/<uuid:pk>/', ModifierLignePanierView.as_view(), name='modifier-ligne-panier'),
    path('panier/delete/lignes/<uuid:pk>/', SupprimerLignePanierView.as_view(), name='supprimer-ligne-panier'),
    path('panier/vider/', ViderPanierView.as_view(), name='vider-panier'),
]