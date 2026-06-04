# utilisateurs/views/auth.py
import random
import string
from datetime import timedelta

from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from utilisateurs.models import Utilisateur, CodeOTP
from utilisateurs.serializers.auth import (
    ConnexionSerializer,
    ProfilSerializer,
    ChangerMotDePasseSerializer,
    MotDePasseOublieSerializer,
    ReinitialiserMotDePasseSerializer,
)


def generer_tokens(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


def generer_code_otp(longueur=6):
    return ''.join(random.choices(string.digits, k=longueur))


class ConnexionView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ConnexionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        tokens = generer_tokens(user)
        profil = ProfilSerializer(user)

        return Response({
            'message': 'Connexion réussie.',
            'tokens': tokens,
            'utilisateur': profil.data,
        }, status=status.HTTP_200_OK)


class DeconnexionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'detail': 'Le refresh token est requis.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Déconnexion réussie.'}, status=status.HTTP_200_OK)
        except TokenError:
            return Response({'detail': 'Token invalide ou déjà révoqué.'}, status=status.HTTP_400_BAD_REQUEST)


class ProfilView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = ProfilSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = ProfilSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'message': 'Profil mis à jour avec succès.',
            'utilisateur': serializer.data,
        })


class ChangerMotDePasseView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangerMotDePasseSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        request.user.set_password(serializer.validated_data['nouveau_mot_de_passe'])
        request.user.save()

        return Response({'message': 'Mot de passe changé avec succès.'}, status=status.HTTP_200_OK)


class MotDePasseOublieView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = MotDePasseOublieSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        user = Utilisateur.objects.get(email=email)

        # Invalider les anciens codes OTP
        CodeOTP.objects.filter(utilisateur=user, usage='reinitialisation').update(est_utilise=True)

        code = generer_code_otp()
        expiration = timezone.now() + timedelta(minutes=15)

        CodeOTP.objects.create(
            utilisateur=user,
            code=code,
            usage='reinitialisation',
            expire_a=expiration,
        )

        # Envoi de l'email
        html_message = render_to_string('emails/otp-request-password.html', {
            'user': user,
            'code': code,
            'expiration_minutes': 15,
        })
        send_mail(
            subject='Réinitialisation de votre mot de passe',
            message=f'Votre code OTP est : {code}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=html_message,
        )

        return Response({'message': 'Un code OTP a été envoyé à votre adresse email.'}, status=status.HTTP_200_OK)


class ReinitialiserMotDePasseView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ReinitialiserMotDePasseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        code_otp = serializer.validated_data['code_otp']
        nouveau_mdp = serializer.validated_data['nouveau_mot_de_passe']

        try:
            user = Utilisateur.objects.get(email=email)
        except Utilisateur.DoesNotExist:
            return Response({'detail': 'Utilisateur introuvable.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            otp = CodeOTP.objects.get(
                utilisateur=user,
                code=code_otp,
                usage='reinitialisation',
                est_utilise=False,
            )
        except CodeOTP.DoesNotExist:
            return Response({'detail': 'Code OTP invalide.'}, status=status.HTTP_400_BAD_REQUEST)

        if otp.expire_a < timezone.now():
            return Response({'detail': 'Ce code OTP a expiré.'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(nouveau_mdp)
        user.save()

        otp.est_utilise = True
        otp.save()

        # Email de confirmation
        html_message = render_to_string('emails/succes-reset-password.html', {'user': user})
        send_mail(
            subject='Mot de passe réinitialisé avec succès',
            message='Votre mot de passe a été réinitialisé avec succès.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=html_message,
        )

        return Response({'message': 'Mot de passe réinitialisé avec succès.'}, status=status.HTTP_200_OK)
