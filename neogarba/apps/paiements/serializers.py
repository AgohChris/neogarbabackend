from rest_framework import serializers
from apps.cores.enums import MoyenPaiementEnum
from .models import Paiement

class CreerPaiementSerializer(serializers.Serializer):
    commande_id = serializers.UUIDField()
    moyen = serializers.ChoiceField(choices=MoyenPaiementEnum.choices)


class PaiementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paiement
        fields = [
            'id',
            'reference',
            'montant',
            'moyen',
            'statut',
            'commande'
        ]
        read_only_fields = ['id', 'reference', 'montant', 'statut']


class PaiementHistoriqueSerializer(serializers.ModelSerializer):
    client_username = serializers.CharField(source='commande.client.username', read_only=True)
    commande_reference = serializers.CharField(source='commande.reference', read_only=True)

    class Meta:
        model = Paiement
        fields = [
            'id',
            'reference',
            'montant',
            'moyen',
            'statut',
            'commande_reference',
            'client_username'
        ]
        read_only_fields = ['id', 'reference', 'montant', 'moyen', 'statut', 'commande_reference', 'client_username']
