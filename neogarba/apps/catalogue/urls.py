from django.urls import path
from .views import (
    CategorieMenuView,
    CategorieMenuDetailView,
    PlatView,
    PlatDetailView,
    MajStockView,
    OptionView,
    OptionDetailView,
)

urlpatterns = [
    # Catégories
    path('liste/categories/', CategorieMenuView.as_view()),
    path('details/categories/<uuid:id>/', CategorieMenuDetailView.as_view()),
    path('create/categories/', CategorieMenuView.as_view()),
    path('modifier/categories/<uuid:id>/', CategorieMenuDetailView.as_view()),
    path('delete/categories/<uuid:id>/', CategorieMenuDetailView.as_view()),

    # Plats
    path('plats/', PlatView.as_view()),
    path('plats/<uuid:id>/', PlatDetailView.as_view()),
    path('plats/<uuid:id>/stock/', MajStockView.as_view()),

    # Options
    path('plats/<uuid:id>/options/', OptionView.as_view()),
    path('options/<uuid:id>/', OptionDetailView.as_view()),
]