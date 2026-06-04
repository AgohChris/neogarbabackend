from rest_framework import serializers
from apps.commandes.models import Commande, LigneCommande
from apps.cores.enums import StatutCommandeEnum, ModeRecuperationEnum

#Mon premier serializer LigneCommandeSerializer 

class LigneCommandeSerializer(serializers.ModelSerializer):
    nom_plat = serializers.CharField(source='plat.nom', read_only=True)
    sous_total = serializers.SerializerMethodField()

    class Meta:
        model = LigneCommande
        fields = ['id', 'nom_plat', 'quantite', 'sous_total', 'instructions']

    def get_sous_total(self, obj):
        return obj.quantite * obj.plat.prix
#Mon deuxieme serializer CommandeSrializer

class CommandeSerializer(serializers.ModelSerializer):
    lignes = LigneCommandeSerializer(many=True, read_only=True)

    class Meta:
        model = Commande
        fields = [
            'id', 'reference', 'statut', 'montant_total',
            'mode_recuperation', 'note', 'date_commande', 'lignes'
        ]  

#Mon Troisième serializer CommandeListeSerializer
          
class CommandeListeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Commande
        fields = ['id', 'reference', 'statut', 'montant_total', 'date_commande']

#Mon Quatrième serializer CreerCommandeSerializer

class CreerCommandeSerializer(serializers.Serializer):
    mode_recuperation = serializers.ChoiceField(
        choices=ModeRecuperationEnum.choices
    )
    adresse_livraison_id = serializers.UUIDField(required=False, allow_null=True)
    note = serializers.CharField(required=False, allow_blank=True, default='')

    def validate(self, data):
        if data['mode_recuperation'] == 'LIVRAISON_DOMICILE' and not data.get('adresse_livraison_id'):
            raise serializers.ValidationError(
                {"adresse_livraison_id": "Adresse obligatoire pour une livraison à domicile."}
            )
        return data


TRANSITIONS_AUTORISEES = {
    'RECUE':              ['EN_PREPARATION'],
    'EN_PREPARATION':     ['PRETE'],
    'PRETE':              ['LIVRAISON_EN_COURS', 'RECUPEREE'],
    'LIVRAISON_EN_COURS': ['LIVREE'],
}

#Mon Quatrième serializer MajStatutSerializer

class MajStatutSerializer(serializers.Serializer):
    statut = serializers.ChoiceField(choices=StatutCommandeEnum.choices)

    def validate_statut(self, nouveau_statut):
        statut_actuel  = self.context.get('statut_actuel')
        transitions_ok = TRANSITIONS_AUTORISEES.get(statut_actuel, [])

        if nouveau_statut not in transitions_ok:
            raise serializers.ValidationError(
                f"Transition invalide : '{statut_actuel}' → '{nouveau_statut}'. "
                f"Autorisées depuis '{statut_actuel}' : {transitions_ok}"
            )
        return nouveau_statut        