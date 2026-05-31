from django.urls import path
from .views import (
    ResumeView,
    VentesView,
    PlatsPopulairesView,
    CommandesParStatutView,
)

urlpatterns = [
    path('resume/', ResumeView.as_view()),
    path('ventes/', VentesView.as_view()),
    path('plats-populaires/', PlatsPopulairesView.as_view()),
    path('commandes-par-statut/', CommandesParStatutView.as_view()),
]