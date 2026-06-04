from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from apps.cores.enums import StatutCommandeEnum, StatutLivraisonEnum, ModeRecuperationEnum, RoleEnum
from apps.cores.utils import envoyer_email
from apps.commandes.models import Commande
from apps.utilisateurs.models import Utilisateur, AdresseLivraison, Livreur
from .models import Livraison
from .permissions import EstLivreur, EstServeur
from .serializers import (
    CreerLivraisonSerializer,
    AssignerLivreurSerializer,
    LivraisonSerializer,
    MajStatutLivraisonSerializer,
    LivreurDisponibleSerializer
)

class CreerLivraisonView(APIView):
    """
    POST /api/livraisons/
    Créer une livraison pour une commande (serveur seulement).
    """
    permission_classes = [IsAuthenticated, EstServeur]

    def post(self, request, *args, **kwargs):
        serializer = CreerLivraisonSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        commande_id = serializer.validated_data['commande_id']
        adresse_livraison_id = serializer.validated_data['adresse_livraison_id']

        commande = get_object_or_404(Commande, id=commande_id)

        # 1. Verifier que la commande est PRETE
        if commande.statut != StatutCommandeEnum.PRETE:
            return Response(
                {"detail": "La commande doit être au statut PRETE pour pouvoir créer une livraison."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 2. Verifier que le mode est LIVRAISON_DOMICILE
        if commande.mode_recuperation != ModeRecuperationEnum.LIVRAISON_DOMICILE:
            return Response(
                {"detail": "Le mode de récupération de la commande doit être LIVRAISON_DOMICILE."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 3. Verifier qu'il n'y a pas deja une livraison pour cette commande
        deja_existe = Livraison.objects.filter(commande=commande).exists()
        if deja_existe:
            return Response(
                {"detail": "Une livraison existe déjà pour cette commande."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 4. Copier l'adresse et le telephone du client dans la livraison (champs figes)
        adresse_livraison = get_object_or_404(AdresseLivraison, id=adresse_livraison_id, client=commande.client)
        
        # 5. Creer la livraison avec statut EN_ATTENTE
        livraison = Livraison.objects.create(
            commande=commande,
            adresse=adresse_livraison.adresse_complete,
            quartier=adresse_livraison.quartier,
            telphone_client=commande.client.telephone,
            status=StatutLivraisonEnum.EN_ATTENTE
        )

        # 6. Retourner la livraison
        output_serializer = LivraisonSerializer(livraison)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class AssignerLivreurView(APIView):
    """
    PUT /api/livraisons/{id}/assigner/
    Assigner un livreur à la livraison (serveur seulement).
    """
    permission_classes = [IsAuthenticated, EstServeur]

    def put(self, request, pk, *args, **kwargs):
        livraison = get_object_or_404(Livraison, id=pk)

        serializer = AssignerLivreurSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        livreur_id = serializer.validated_data['livreur_id']

        # 1. Verifier que le livreur existe et est actif
        livreur = get_object_or_404(Livreur, id=livreur_id)
        if not livreur.is_active:
            return Response(
                {"detail": "Le livreur spécifié n'est pas actif."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 2. Assigner le livreur a la livraison
        livraison.livreur = livreur
        livraison.save()

        # 3. Mettre a jour le statut de la commande a LIVRAISON_EN_COURS
        commande = livraison.commande
        commande.statut = StatutCommandeEnum.LIVRAISON_EN_COURS
        commande.save()

        # 4. Envoyer email au client avec template livreur-assigne.html
        contexte = {
            "commande": commande,
            "livreur": livreur,
            "livraison": livraison
        }
        if commande.client.email:
            envoyer_email(
                sujet="Votre livreur est en route !",
                template_name="emails/livreur-assigne.html",
                contexte=contexte,
                destinataire=commande.client.email
            )

        # 5. Retourner la livraison
        output_serializer = LivraisonSerializer(livraison)
        return Response(output_serializer.data, status=status.HTTP_200_OK)


class MesLivraisonsView(APIView):
    """
    GET /api/livraisons/mes-livraisons/
    Voir ses livraisons assignees (livreur seulement).
    """
    permission_classes = [IsAuthenticated, EstLivreur]

    def get(self, request, *args, **kwargs):
        livraisons = Livraison.objects.filter(livreur=request.user)
        serializer = LivraisonSerializer(livraisons, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DetailLivraisonView(APIView):
    """
    GET /api/livraisons/{id}/
    Detail d'une livraison.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, *args, **kwargs):
        livraison = get_object_or_404(Livraison, id=pk)
        
        # Verify access: Server, Admin, assigned Livreur, or the Client who ordered
        est_autorise = (
            request.user.role in [RoleEnum.SERVEUR, RoleEnum.ADMINISTRATEUR] or
            request.user.is_staff or
            request.user.is_superuser or
            (livraison.livreur_id == request.user.id) or
            (livraison.commande.client_id == request.user.id)
        )
        if not est_autorise:
            return Response(
                {"detail": "Vous n'êtes pas autorisé à accéder à cette livraison."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = LivraisonSerializer(livraison)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MajStatutLivraisonView(APIView):
    """
    PUT /api/livraisons/{id}/statut/
    Mettre a jour le statut (livreur seulement).
    """
    permission_classes = [IsAuthenticated, EstLivreur]

    def put(self, request, pk, *args, **kwargs):
        livraison = get_object_or_404(Livraison, id=pk)

        # 0. Check ownership: Only the assigned livreur can update
        if livraison.livreur_id != request.user.id:
            return Response(
                {"detail": "Vous n'êtes pas le livreur assigné à cette livraison."},
                status=status.HTTP_403_FORBIDDEN
            )

        # 1. Verifier les transitions autorisees via Serializer validation
        serializer = MajStatutLivraisonSerializer(
            data=request.data,
            context={'instance': livraison}
        )
        serializer.is_valid(raise_exception=True)

        new_status = serializer.validated_data['status']
        livraison.status = new_status
        livraison.save()

        # 2. Si LIVREE : mettre aussi le statut de la commande a LIVREE + envoyer email
        if new_status == StatutLivraisonEnum.LIVREE:
            commande = livraison.commande
            commande.statut = StatutCommandeEnum.LIVREE
            commande.save()

            contexte = {
                "commande": commande,
                "livraison": livraison
            }
            if commande.client.email:
                envoyer_email(
                    sujet="Votre commande a été livrée !",
                    template_name="emails/livraison-effectuee.html",
                    contexte=contexte,
                    destinataire=commande.client.email
                )

        # 3. Retourner la livraison
        output_serializer = LivraisonSerializer(livraison)
        return Response(output_serializer.data, status=status.HTTP_200_OK)


class LivreursDisponiblesView(APIView):
    """
    GET /api/livraisons/livreurs-disponibles/
    Lister les livreurs actifs (serveur seulement).
    """
    permission_classes = [IsAuthenticated, EstServeur]

    def get(self, request, *args, **kwargs):
        livreurs = Utilisateur.objects.filter(role=RoleEnum.LIVREUR, is_active=True)
        serializer = LivreurDisponibleSerializer(livreurs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
