from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from .models import CategorieMenu, Plat, OptionPersonnalisation
from .serializers import (
    CategorieMenuSerializer,
    PlatListeSerializer,
    PlatDetailSerializer,
    PlatCreerModifierSerializer,
    MajStockSerializer,
    OptionPersonnalisationSerializer,
)
from .permissions import EstVendeur


#  CATÉGORIES

class CategorieMenuView(APIView):
    """
    GET  → liste toutes les catégories (tout le monde)
    POST → crée une catégorie (vendeur seulement)
    """
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [EstVendeur()]

    def get(self, request):
        categories = CategorieMenu.objects.all()
        serializer = CategorieMenuSerializer(categories, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CategorieMenuSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategorieMenuDetailView(APIView):
    """
    GET    → détail d'une catégorie (tout le monde)
    PUT    → modifier une catégorie (vendeur)
    DELETE → supprimer une catégorie (vendeur)
    """
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [EstVendeur()]

    def get_object(self, id):
        try:
            return CategorieMenu.objects.get(id=id)
        except CategorieMenu.DoesNotExist:
            return None

    def get(self, request, id):
        categorie = self.get_object(id)
        if not categorie:
            return Response({'erreur': 'Catégorie introuvable'}, status=status.HTTP_404_NOT_FOUND)
        serializer = CategorieMenuSerializer(categorie)
        return Response(serializer.data)

    def put(self, request, id):
        categorie = self.get_object(id)
        if not categorie:
            return Response({'erreur': 'Catégorie introuvable'}, status=status.HTTP_404_NOT_FOUND)
        serializer = CategorieMenuSerializer(categorie, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        categorie = self.get_object(id)
        if not categorie:
            return Response({'erreur': 'Catégorie introuvable'}, status=status.HTTP_404_NOT_FOUND)
        try:
            categorie.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception:
            return Response(
                {'erreur': 'Impossible de supprimer cette catégorie car elle contient des plats'},
                status=status.HTTP_400_BAD_REQUEST
            )


# PLATS

class PlatView(APIView):
    """
    GET  → liste les plats avec filtres optionnels (tout le monde)
    POST → crée un plat (vendeur)
    """
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [EstVendeur()]

    def get(self, request):
        plats = Plat.objects.all()

        # Filtre par catégorie
        categorie_id = request.query_params.get('categorie')
        if categorie_id:
            plats = plats.filter(categorie__id=categorie_id)

        # Filtre par disponibilité
        disponibilite = request.query_params.get('disponibilite')
        if disponibilite:
            plats = plats.filter(disponibilite=disponibilite)

        serializer = PlatListeSerializer(plats, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PlatCreerModifierSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PlatDetailView(APIView):
    """
    GET    → détail d'un plat avec ses options (tout le monde)
    PUT    → modifier un plat (vendeur)
    DELETE → supprimer un plat (vendeur)
    """
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [EstVendeur()]

    def get_object(self, id):
        try:
            return Plat.objects.get(id=id)
        except Plat.DoesNotExist:
            return None

    def get(self, request, id):
        plat = self.get_object(id)
        if not plat:
            return Response({'erreur': 'Plat introuvable'}, status=status.HTTP_404_NOT_FOUND)
        serializer = PlatDetailSerializer(plat)
        return Response(serializer.data)

    def put(self, request, id):
        plat = self.get_object(id)
        if not plat:
            return Response({'erreur': 'Plat introuvable'}, status=status.HTTP_404_NOT_FOUND)
        serializer = PlatCreerModifierSerializer(plat, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        plat = self.get_object(id)
        if not plat:
            return Response({'erreur': 'Plat introuvable'}, status=status.HTTP_404_NOT_FOUND)
        try:
            plat.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception:
            return Response(
                {'erreur': 'Impossible de supprimer ce plat car il est dans une commande'},
                status=status.HTTP_400_BAD_REQUEST
            )


class MajStockView(APIView):
    """
    PUT → mettre à jour le stock et la disponibilité (vendeur)
    """
    permission_classes = [EstVendeur]

    def get_object(self, id):
        try:
            return Plat.objects.get(id=id)
        except Plat.DoesNotExist:
            return None

    def put(self, request, id):
        plat = self.get_object(id)
        if not plat:
            return Response({'erreur': 'Plat introuvable'}, status=status.HTTP_404_NOT_FOUND)
        serializer = MajStockSerializer(plat, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ─── OPTIONS ──────────────────────────────────────────────

class OptionView(APIView):
    """
    GET  → liste les options d'un plat (tout le monde)
    POST → ajouter une option à un plat (vendeur)
    """
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [EstVendeur()]

    def get(self, request, id):
        plat = Plat.objects.filter(id=id).first()
        if not plat:
            return Response({'erreur': 'Plat introuvable'}, status=status.HTTP_404_NOT_FOUND)
        options = plat.options.all()
        serializer = OptionPersonnalisationSerializer(options, many=True)
        return Response(serializer.data)

    def post(self, request, id):
        plat = Plat.objects.filter(id=id).first()
        if not plat:
            return Response({'erreur': 'Plat introuvable'}, status=status.HTTP_404_NOT_FOUND)
        serializer = OptionPersonnalisationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(plat=plat)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OptionDetailView(APIView):
    """
    PUT    → modifier une option (vendeur)
    DELETE → supprimer une option (vendeur)
    """
    permission_classes = [EstVendeur]

    def get_object(self, id):
        try:
            return OptionPersonnalisation.objects.get(id=id)
        except OptionPersonnalisation.DoesNotExist:
            return None

    def put(self, request, id):
        option = self.get_object(id)
        if not option:
            return Response({'erreur': 'Option introuvable'}, status=status.HTTP_404_NOT_FOUND)
        serializer = OptionPersonnalisationSerializer(option, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        option = self.get_object(id)
        if not option:
            return Response({'erreur': 'Option introuvable'}, status=status.HTTP_404_NOT_FOUND)
        option.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
