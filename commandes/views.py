from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from apps.catalogue.models import Plat
from apps.catalogue.models import DisponibiliteEnum
from apps.commandes.models import Panier, LignePanier
from apps.commandes.serializers import (
    PanierSerializer,
    AjouterAuPanierSerializer,
    LignePanierSerializer,
)


class VoirPanierView(APIView):
    """GET /api/panier/ — retourne le panier du client connecté avec toutes ses lignes et le total"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            panier = request.user.panier
        except Panier.DoesNotExist:
            return Response(
                {"detail": "Aucun panier trouvé pour cet utilisateur."},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = PanierSerializer(panier)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AjouterAuPanierView(APIView):
    """POST /api/panier/ajouter/ — ajoute un plat au panier"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AjouterAuPanierSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        plat_id = serializer.validated_data['plat_id']
        quantite = serializer.validated_data['quantite']
        instruction = serializer.validated_data.get('instruction', '')

        # Vérifier que le plat existe
        try:
            plat = Plat.objects.get(id=plat_id)
        except Plat.DoesNotExist:
            return Response(
                {"detail": "Plat introuvable."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Vérifier que le plat n'est pas épuisé
        if plat.disponibilite == DisponibiliteEnum.EPUISE:
            return Response(
                {"detail": "Ce plat est épuisé."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Vérifier que la quantité demandée ne dépasse pas le stock
        if quantite > plat.quantite_stock:
            return Response(
                {"detail": f"Stock insuffisant. Seulement {plat.quantite_stock} disponible(s)."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Récupérer le panier du client
        try:
            panier = request.user.panier
        except Panier.DoesNotExist:
            return Response(
                {"detail": "Aucun panier trouvé pour cet utilisateur."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Si le plat est déjà dans le panier, on ajoute la quantité
        ligne_existante = panier.paniers.filter(plat=plat).first()
        if ligne_existante:
            nouvelle_quantite = ligne_existante.quantite + quantite
            if nouvelle_quantite > plat.quantite_stock:
                return Response(
                    {"detail": f"Stock insuffisant. Seulement {plat.quantite_stock} disponible(s)."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            ligne_existante.quantite = nouvelle_quantite
            ligne_existante.save()
            ligne = ligne_existante
        else:
            # Créer une nouvelle ligne — prix_unitaire copié depuis Plat.prix
            ligne = LignePanier.objects.create(
                panier=panier,
                plat=plat,
                quantite=quantite,
                prix_unitaire=plat.prix,
                instruction=instruction,
            )

        return Response(LignePanierSerializer(ligne).data, status=status.HTTP_201_CREATED)


class ModifierLignePanierView(APIView):
    """PUT /api/panier/modifier/lignes/{id}/ — modifie la quantité d'une ligne"""
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        try:
            panier = request.user.panier
        except Panier.DoesNotExist:
            return Response(
                {"detail": "Aucun panier trouvé."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Vérifier que la ligne appartient bien au panier du client connecté
        try:
            ligne = panier.paniers.get(id=pk)
        except LignePanier.DoesNotExist:
            return Response(
                {"detail": "Ligne introuvable dans votre panier."},
                status=status.HTTP_404_NOT_FOUND
            )

        quantite = request.data.get('quantite')
        if quantite is None:
            return Response(
                {"detail": "Le champ 'quantite' est requis."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            quantite = int(quantite)
        except (ValueError, TypeError):
            return Response(
                {"detail": "La quantité doit être un entier."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if quantite < 1:
            return Response(
                {"detail": "La quantité doit être au moins 1."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Vérifier stock
        if quantite > ligne.plat.quantite_stock:
            return Response(
                {"detail": f"Stock insuffisant. Seulement {ligne.plat.quantite_stock} disponible(s)."},
                status=status.HTTP_400_BAD_REQUEST
            )

        ligne.quantite = quantite
        ligne.save()
        return Response(LignePanierSerializer(ligne).data, status=status.HTTP_200_OK)


class SupprimerLignePanierView(APIView):
    """DELETE /api/panier/delete/lignes/{id}/ — supprime une ligne du panier"""
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            panier = request.user.panier
        except Panier.DoesNotExist:
            return Response(
                {"detail": "Aucun panier trouvé."},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            ligne = panier.paniers.get(id=pk)
        except LignePanier.DoesNotExist:
            return Response(
                {"detail": "Ligne introuvable dans votre panier."},
                status=status.HTTP_404_NOT_FOUND
            )

        ligne.delete()
        return Response(
            {"detail": "Ligne supprimée avec succès."},
            status=status.HTTP_200_OK
        )


class ViderPanierView(APIView):
    """DELETE /api/panier/vider/ — supprime toutes les lignes du panier"""
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        try:
            panier = request.user.panier
        except Panier.DoesNotExist:
            return Response(
                {"detail": "Aucun panier trouvé."},
                status=status.HTTP_404_NOT_FOUND
            )

        panier.paniers.all().delete()
        return Response(
            {"detail": "Panier vidé avec succès."},
            status=status.HTTP_200_OK
        )