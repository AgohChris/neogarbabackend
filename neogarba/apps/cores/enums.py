from django.db import models


class RoleEnum(models.TextChoices):
    CLIENT = 'CLIENT', 'Client'
    SERVEUR = 'SERVEUR', 'Serveur'
    LIVREUR = 'LIVREUR', 'Livreur'
    VENDEUR = 'VENDEUR', 'Vendeur'
    ADMINISTRATEUR = 'ADMINISTRATEUR', 'Administrateur'


class StatutCommandeEnum(models.TextChoices):
    RECUE = 'RECUE', 'Reçue'
    EN_PREPARATION = 'EN_PREPARATION', 'En préparation'
    PRETE = 'PRETE', 'Prête'
    LIVRAISON_EN_COURS = 'LIVRAISON_EN_COURS', 'Livraison en cours'
    LIVREE = 'LIVREE', 'Livrée'
    RECUPEREE = 'RECUPEREE', 'Récupérée'


class ModeRecuperationEnum(models.TextChoices):
    LIVRAISON_DOMICILE = 'LIVRAISON_DOMICILE', 'Livraison à domicile'
    RETRAIT_SUR_PLACE = 'RETRAIT_SUR_PLACE', 'Retrait sur place'


class MoyenPaiementEnum(models.TextChoices):
    WAVE = 'WAVE', 'Wave'
    ORANGE_MONEY = 'ORANGE_MONEY', 'Orange Money'


class StatutPaiementEnum(models.TextChoices):
    EN_ATTENTE = 'EN_ATTENTE', 'En attente'
    REUSSI = 'REUSSI', 'Réussi'
    ECHOUE = 'ECHOUE', 'Échoué'


class StatutLivraisonEnum(models.TextChoices):
    EN_ATTENTE = 'EN_ATTENTE', 'En attente'
    EN_COURS = 'EN_COURS', 'En cours'
    LIVREE = 'LIVREE', 'Livrée'
    ECHOUEE = 'ECHOUEE', 'Échouée'


class DisponibiliteEnum(models.TextChoices):
    DISPONIBLE = 'DISPONIBLE', 'Disponible'
    STOCK_LIMITE = 'STOCK_LIMITE', 'Stock limité'
    EPUISE = 'EPUISE', 'Épuisé'


class TypeOptionEnum(models.TextChoices):
    QUANTITE_ATTIEKE = 'QUANTITE_ATTIEKE', 'Quantité attiéké'
    TYPE_POISSON = 'TYPE_POISSON', 'Type de poisson'
    ACCOMPAGNEMENT = 'ACCOMPAGNEMENT', 'Accompagnement'
    BOISSON = 'BOISSON', 'Boisson'
