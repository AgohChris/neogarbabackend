from rest_framework import serializers
from apps.commandes.models import Panier, LignePanier



class LignePanierSerializer(serializers.ModelSerializer):
    nom_plat = serializers.CharField(source='plat.nom', read_only=True)
    sous_total = serializers.SerializerMethodField()

    class Meta:
        model = LignePanier
        fields = [
            'id', 'reference', 'nom_plat',
            'quantite', 'prix_unitaire', 'instruction', 'sous_total'
        ]

    def get_sous_total(self, obj):
        return obj.get_sous_total()


class PanierSerializer(serializers.ModelSerializer):
    lignes = LignePanierSerializer(source='paniers', many=True, read_only=True)
    montant_total = serializers.SerializerMethodField()

    class Meta:
        model = Panier
        fields = ['id', 'reference', 'date_creation', 'date_mises_a_jour', 'lignes', 'montant_total']

    def get_montant_total(self, obj):
        return sum(ligne.get_sous_total() for ligne in obj.paniers.all())


class AjouterAuPanierSerializer(serializers.Serializer):
    plat_id = serializers.UUIDField()
    quantite = serializers.IntegerField(min_value=1, default=1)
    instruction = serializers.CharField(required=False, allow_blank=True, default='')