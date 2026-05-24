from django.urls import path
from .views import CreerPaiementView, DetailPaiementView, HistoriquePaiementsView

urlpatterns = [
    # Mapped to: /api/paiements/ or /api/paiements
    path('', CreerPaiementView.as_view(), name='creer-paiement'),

    # Mapped to: /api/paiements/historique/ or /api/paiements/historique
    path('historique/', HistoriquePaiementsView.as_view(), name='historique-paiements'),

    # Mapped to: /api/paiements/{pk}/ or /api/paiements/{pk}
    path('<uuid:pk>/', DetailPaiementView.as_view(), name='detail-paiement'),
]
