from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import datetime

from apps.cores.enums import StatutPaiementEnum, RoleEnum
from apps.cores.utils import envoyer_email
from apps.commandes.models import Commande
from .models import Paiement
from .serializers import CreerPaiementSerializer, PaiementSerializer, PaiementHistoriqueSerializer
from .permissions import EstAdministrateur


class CreerPaiementView(APIView):
    """
    POST /api/paiements/
    Payer une commande.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = CreerPaiementSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        commande_id = serializer.validated_data['commande_id']
        moyen = serializer.validated_data['moyen']

        # 1. Verifier que la commande existe et appartient au client connecte
        commande = get_object_or_404(Commande, id=commande_id)
        if commande.client_id != request.user.id:
            return Response(
                {"detail": "Cette commande ne vous appartient pas."},
                status=status.HTTP_403_FORBIDDEN
            )

        # 2. Verifier que la commande n'est pas deja payee (pas de paiement REUSSI existant)
        deja_payee = Paiement.objects.filter(
            commande=commande,
            statut=StatutPaiementEnum.REUSSI
        ).exists()
        if deja_payee:
            return Response(
                {"detail": "Cette commande a déjà été payée."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 3. Creer le paiement avec statut EN_ATTENTE
        paiement = Paiement.objects.create(
            montant=commande.montant_total,
            moyen=moyen,
            commande=commande,
            statut=StatutPaiementEnum.EN_ATTENTE
        )

        try:
            # 4. Simuler le paiement (succeeds directly)
            paiement.statut = StatutPaiementEnum.REUSSI
            paiement.save()

            # 5. Si reussi : envoyer email de confirmation
            contexte = {
                "paiement": paiement,
                "commande": commande
            }
            if request.user.email:
                envoyer_email(
                    sujet="Confirmation de paiement de votre commande",
                    template_name="emails/paiement-reussi.html",
                    contexte=contexte,
                    destinataire=request.user.email
                )
        except Exception as e:
            # 6. Si echoue : envoyer email d'echec
            paiement.statut = StatutPaiementEnum.ECHOUE
            paiement.save()

            contexte = {
                "paiement": paiement,
                "commande": commande
            }
            if request.user.email:
                envoyer_email(
                    sujet="Échec du paiement de votre commande",
                    template_name="emails/paiement-echoue.html",
                    contexte=contexte,
                    destinataire=request.user.email
                )

        # 7. Retourner le paiement
        output_serializer = PaiementSerializer(paiement)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class DetailPaiementView(APIView):
    """
    GET /api/paiements/{id}/
    Voir le statut d'un paiement.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, *args, **kwargs):
        paiement = get_object_or_404(Paiement, id=pk)

        # Verifier que c'est bien le paiement du client connecte (ou d'un administrateur)
        est_admin = (
            request.user.role == RoleEnum.ADMINISTRATEUR or
            request.user.is_staff or
            request.user.is_superuser
        )
        if not est_admin and paiement.commande.client_id != request.user.id:
            return Response(
                {"detail": "Vous n'êtes pas autorisé à voir ce paiement."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = PaiementSerializer(paiement)
        return Response(serializer.data, status=status.HTTP_200_OK)


class HistoriquePaiementsView(APIView):
    """
    GET /api/paiements/historique/
    Historique des transactions (admin seulement).
    """
    permission_classes = [IsAuthenticated, EstAdministrateur]

    def get(self, request, *args, **kwargs):
        queryset = Paiement.objects.all()

        # Filtre statut
        statut = request.query_params.get('statut')
        if statut:
            queryset = queryset.filter(statut=statut)

        # Filtre moyen
        moyen = request.query_params.get('moyen')
        if moyen:
            queryset = queryset.filter(moyen=moyen)

        # Filtre debut (date commande)
        debut = request.query_params.get('debut')
        if debut:
            try:
                debut_date = datetime.strptime(debut, '%Y-%m-%d')
                # Make naive datetime aware if settings use timezone aware datetimes
                from django.conf import settings
                if settings.USE_TZ:
                    from django.utils.timezone import make_aware
                    debut_date = make_aware(debut_date)
                queryset = queryset.filter(commande__date_commande__gte=debut_date)
            except ValueError:
                pass  # Ignore invalid date formats

        serializer = PaiementHistoriqueSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
