from datetime import timedelta

from django.core.mail import send_mail
from django.shortcuts import render

from django.utils import timezone
from django.utils.html import strip_tags
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.cores.utils import envoyer_email
from django.template.loader import render_to_string
from .models import Utilisateur, CodeOTP
from .serializers import *
import secrets
import string


# Create your views here.


def genrer_codeOTP():
    code = ''
    for i in range(6):
        chiffre = secrets.choice(string.digits)
        code = code + chiffre
    return code

def EnvoieCodeOTP(utilsateur, template_email='emails/code-otp-inscription.html'):

    code = genrer_codeOTP()
    CodeOTP.objects.create(
        utilisateur=utilsateur,
        code=code,
        date_expiration=timezone.now() + timedelta(days=1),
    )

    contexte = {
        'prenom':utilsateur.first_name,
        'code':code,
        'durée_validate':5,
    }

    html_message = render_to_string(template_email, contexte)
    message_complet = strip_tags(html_message)

    send_mail(
        subject='neogarba : Votre code de vérification',
        message=message_complet,
        from_email=None,
        recipient_list=[utilsateur.email],
        html_message=html_message,
    )

    return code



class InscriptionView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = InscriptionSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({
                'erreurs': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        client = serializer.save()

        EnvoieCodeOTP(
            utilsateur=client,
            template_email='emails/code-otp-inscription.html',
            sujet='Votre code de vérification neogarba'
        )

        return Response({
            'message':'Compte créer avec succès. Un code de vérification à été envoyer à votre adresse email',
            'email': client.email,
        }, status=status.HTTP_201_CREATED
        )
