from django.urls import path
from .views import *

urlpatterns=[
    path('inscription/', InscriptionView.as_view(), name='inscription'),
    path('verification-otp/', VerificationOTPView.as_view(), name='verification-otp'),
]