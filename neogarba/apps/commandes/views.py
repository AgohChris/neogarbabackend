from django.shortcuts import render
from rest_framework.pagination import PageNumberPagination

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
from apps.commandes.permissions import HasRole
from apps.cores.enums import RoleEnum


class ListerMesCommandesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        commandes = Commande.objects.filter(
            client=request.user
        ).order_by('-date_commande')

        paginator = PageNumberPagination()
        paginator.page_size = 20
        result = paginator.paginate_queryset(commandes, request)
        serializer = CommandeListeSerializer(result, many=True)
        return paginator.get_paginated_response(serializer.data)


class DetailCommandeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        commande = get_object_or_404(Commande, id=id)

        if commande.client != request.user and request.user.role != RoleEnum.SERVEUR:
            return Response(
                {'detail': 'Accès refusé.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = CommandeSerializer(commande)
        return Response(serializer.data)

class CommandesEntrantesView(APIView):
    permission_classes = [IsAuthenticated, HasRole.for_role(RoleEnum.SERVEUR)]

    def get(self, request):
        commandes = Commande.objects.filter(
            statut='RECUE'
        ).order_by('date_commande')

        paginator = PageNumberPagination()
        paginator.page_size = 20
        result = paginator.paginate_queryset(commandes, request)
        serializer = CommandeListeSerializer(result, many=True)
        return paginator.get_paginated_response(serializer.data)


class ToutesCommandesView(APIView):
    permission_classes = [IsAuthenticated, HasRole.for_role(RoleEnum.SERVEUR)]

    def get(self, request):
        qs = Commande.objects.all().order_by('-date_commande')

        statut = request.query_params.get('statut')
        if statut:
            qs = qs.filter(statut=statut)

        paginator = PageNumberPagination()
        paginator.page_size = 20
        result = paginator.paginate_queryset(qs, request)
        serializer = CommandeListeSerializer(result, many=True)
        return paginator.get_paginated_response(serializer.data)

class MajStatutCommandeView(APIView):
    permission_classes = [IsAuthenticated, HasRole.for_role(RoleEnum.SERVEUR)]

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
    permission_classes = [IsAuthenticated, HasRole.for_role(RoleEnum.CLIENT)]

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
            adresse_livraison_id=serializer.validated_data.get('adresse_livraison_id'),
)

        for ligne in panier.paniers.select_related('plat').all():
            LigneCommande.objects.create(
                commande=commande,
                plat=ligne.plat,
                quantite=ligne.quantite,
                prix_unitaire=ligne.prix_unitaire,
                instructions=ligne.instruction,
            )

        panier.paniers.all().delete()

        return Response(
            CommandeSerializer(commande).data,
            status=status.HTTP_201_CREATED
        )



#Le livreur doit avoir  toutrd les infos sur la livraison et cela doit se faire en reliant l'adresse de commande au livreur
#pour que la livraison soit effective