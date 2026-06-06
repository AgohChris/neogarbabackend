from rest_framework import serializers
from .models import CategorieMenu, Plat, OptionPersonnalisation


# Serializer pour les catégories (CRUD complet)
class CategorieMenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategorieMenu
        fields = ['id', 'reference', 'nom', 'image']
        read_only_fields = ['id', 'reference']


# Serializer pour les options d'un plat (CRUD complet)
class OptionPersonnalisationSerializer(serializers.ModelSerializer):
    class Meta:
        model = OptionPersonnalisation
        fields = ['id', 'reference', 'type', 'prix_supplement', 'disponible', 'plat']
        read_only_fields = ['id', 'reference']


# Version légère pour la liste des plats
class PlatListeSerializer(serializers.ModelSerializer):
    categorie = CategorieMenuSerializer(read_only=True)

    class Meta:
        model = Plat
        fields = ['reference', 'nom', 'prix', 'disponibilite', 'categorie', 'image']


# Version complète avec les options incluses
class PlatDetailSerializer(serializers.ModelSerializer):
    options = OptionPersonnalisationSerializer(many=True, read_only=True)
    categorie = CategorieMenuSerializer(read_only=True)

    class Meta:
        model = Plat
        fields = ['id', 'reference', 'nom', 'prix', 'description',
                  'image', 'disponibilite', 'quantite_stock', 'categorie', 'options']
        read_only_fields = ['id', 'reference']


# Pour créer ou modifier un plat
class PlatCreerModifierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plat
        fields = ['nom', 'prix', 'description', 'image', 'categorie', 'disponibilite', 'quantite_stock']


# Pour mettre à jour uniquement le stock et la disponibilité
class MajStockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plat
        fields = ['quantite_stock', 'disponibilite']