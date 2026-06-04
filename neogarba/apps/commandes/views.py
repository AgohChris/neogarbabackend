from django.shortcuts import render

# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from apps.commandes.models import Commande, LigneCommande
from apps.commandes.models import Panier, LignePanier
from apps.commandes.serializers import (
    CommandeSerializer,
    CommandeListeSerializer,
    CreerCommandeSerializer,
    MajStatutSerializer,
)
from apps.commandes.permissions import EstServeur, EstClient


class ListerMesCommandesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        commandes = Commande.objects.filter(
            client=request.user
        ).order_by('-date_commande')

        serializer = CommandeListeSerializer(commandes, many=True)
        return Response(serializer.data)


class DetailCommandeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        commande = get_object_or_404(Commande, id=id)

        if commande.client != request.user and request.user.role != 'SERVEUR':
            return Response(
                {'detail': 'Accès refusé.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = CommandeSerializer(commande)
        return Response(serializer.data)

class CommandesEntrantesView(APIView):
    permission_classes = [IsAuthenticated, EstServeur]

    def get(self, request):
        commandes = Commande.objects.filter(
            statut='RECUE'
        ).order_by('date_commande')  

        serializer = CommandeListeSerializer(commandes, many=True)
        return Response(serializer.data)


class ToutesCommandesView(APIView):
    permission_classes = [IsAuthenticated, EstServeur]

    def get(self, request):
        qs = Commande.objects.all().order_by('-date_commande')

       
        statut = request.query_params.get('statut')
        if statut:
            qs = qs.filter(statut=statut)

        serializer = CommandeListeSerializer(qs, many=True)
        return Response(serializer.data)

class MajStatutCommandeView(APIView):
    permission_classes = [IsAuthenticated, EstServeur]

    def put(self, request, id):
        commande = get_object_or_404(Commande, id=id)

        serializer = MajStatutSerializer(
            data=request.data,
            context={'statut_actuel': commande.statut}
        )
        serializer.is_valid(raise_exception=True)

        commande.statut = serializer.validated_data['statut']
        commande.save()

        return Response(CommandeSerializer(commande).data)

class CreerCommandeView(APIView):
    permission_classes = [IsAuthenticated, EstClient]

    def post(self, request):
        serializer = CreerCommandeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        panier = get_object_or_404(Panier, client=request.user)

        if not panier.paniers.exists():
            return Response(
                {'detail': 'Votre panier est vide.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        montant_total = sum(
            ligne.get_sous_total() for ligne in panier.paniers.all()
        )

        commande = Commande.objects.create(
            client=request.user,
            montant_total=montant_total,
            mode_recuperation=serializer.validated_data['mode_recuperation'],
            note=serializer.validated_data.get('note', ''),
        )

        for ligne in panier.paniers.select_related('plat').all():
            LigneCommande.objects.create(
                commande=commande,
                plat=ligne.plat,
                quantite=ligne.quantite,
                instructions=ligne.instruction,
            )

        panier.paniers.all().delete()

        return Response(
            CommandeSerializer(commande).data,
            status=status.HTTP_201_CREATED
        )
