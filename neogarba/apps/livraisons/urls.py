from django.urls import path
from .views import (
    CreerLivraisonView,
    AssignerLivreurView,
    MesLivraisonsView,
    DetailLivraisonView,
    MajStatutLivraisonView,
    LivreursDisponiblesView
)

urlpatterns = [
    # Static endpoints (must be declared first to prevent UUID conflict)
    path('', CreerLivraisonView.as_view(), name='creer-livraison'),
    path('mes-livraisons/', MesLivraisonsView.as_view(), name='mes-livraisons'),
    path('livreurs-disponibles/', LivreursDisponiblesView.as_view(), name='livreurs-disponibles'),

    # Dynamic UUID endpoints
    path('<uuid:pk>/', DetailLivraisonView.as_view(), name='detail-livraison'),
    path('<uuid:pk>/assigner/', AssignerLivreurView.as_view(), name='assigner-livreur'),
    path('<uuid:pk>/statut/', MajStatutLivraisonView.as_view(), name='maj-statut-livraison'),
]
