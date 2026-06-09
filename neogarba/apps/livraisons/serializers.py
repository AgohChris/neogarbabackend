from rest_framework import serializers
from apps.cores.enums import StatutLivraisonEnum
from apps.utilisateurs.models import Utilisateur, AdresseLivraison
from .models import Livraison

class CreerLivraisonSerializer(serializers.Serializer):
    commande_id = serializers.UUIDField()
    adresse_livraison_id = serializers.UUIDField()


class AssignerLivreurSerializer(serializers.Serializer):
    livreur_id = serializers.UUIDField()


class LivraisonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Livraison
        fields = [
            'id',
            'reference',
            'adresse',
            'quartier',
            'telphone_client',
            'status',
            'commande',
            'livreur'
        ]
        read_only_fields = ['id', 'reference', 'status']


class MajStatutLivraisonSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=StatutLivraisonEnum.choices)

    def validate_status(self, value):
        # We perform transition checks inside the view or here. Let's do it here or in the view.
        # Enforcing transition:
        # EN_ATTENTE -> EN_COURS
        # EN_COURS -> LIVREE or ECHOUEE
        # If we do it inside the serializer, we need context of the instance to know the current status.
        # DRF passes the instance to self.instance when updating.
        instance = self.context.get('instance')
        if instance:
            current = instance.status
            allowed = {
                StatutLivraisonEnum.EN_ATTENTE: [StatutLivraisonEnum.EN_COURS],
                StatutLivraisonEnum.EN_COURS: [StatutLivraisonEnum.LIVREE, StatutLivraisonEnum.ECHOUEE],
                StatutLivraisonEnum.LIVREE: [],
                StatutLivraisonEnum.ECHOUEE: []
            }
            if value not in allowed.get(current, []):
                raise serializers.ValidationError(
                    f"Transition de statut invalide : de {current} à {value}."
                )
        return value


class LivreurDisponibleSerializer(serializers.ModelSerializer):
    nom = serializers.CharField(source='last_name')
    prenom = serializers.CharField(source='first_name')

    class Meta:
        model = Utilisateur
        fields = ['id', 'reference', 'nom', 'prenom', 'telephone']
