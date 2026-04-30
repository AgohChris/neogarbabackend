from django.db import models

# Create your models here.


from apps.cores.utils import *
from apps.cores.enums import *
from apps.utilisateurs.models import *
from apps.catalogue.models import *

class Panier(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=generer_uuid7,
        editable=False
    )

    reference = models.CharField(
        max_length=30,
        unique=True,
        editable=False
    )



    date_creation = models.DateTimeField(auto_now_add=True)
    date_mises_a_jour = models.DateTimeField(auto_now=True)

    client = models.OneToOneField(
        Client,
        on_delete=models.CASCADE,
        related_name='panier',
    )

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = generer_reference(PREFIXES['panier'])
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Panier"
        verbose_name_plural = "Paniers"



    # def get_montant_total(self):
    #     return sum(li.get_sous_total())


class LignePanier(models.Model):
    id = models.UUIDField(
            primary_key=True,
            default=generer_uuid7,
            editable=False
        )

    reference = models.CharField(
            max_length=30,
            unique=True,
            editable=False
        )

    quantite = models.PositiveIntegerField(default=1)

    prix_unitaire = models.PositiveIntegerField()

    instruction = models.TextField(
            blank=True, default=''
        )

    panier= models.ForeignKey(
        Panier,
        on_delete=models.CASCADE,
        related_name='paniers',
    )
    plat = models.ForeignKey(
        Plat,
        on_delete=models.CASCADE,
        related_name='ligne_paniers',
    )

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = generer_reference(PREFIXES['ligne_panier'])
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "LignePanier"
        verbose_name_plural = "Ligne de Panier"

    def get_sous_total(self):
        return self.quantite * self.prix_unitaire




class Commande(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=generer_uuid7,
        editable=False
    )

    reference = models.CharField(
        max_length=30,
        unique=True,
        editable=False
    )


    date_commande = models.DateTimeField(auto_now_add=True)

    montant_total=models.PositiveIntegerField()

    statut = models.CharField(
        max_length=20,
        choices=StatutCommandeEnum.choices,
        default=StatutCommandeEnum.RECUE
    )

    mode_recuperation = models.CharField(
        max_length=50,
        choices=ModeRecuperationEnum.choices
    )

    heure_retrait = models.CharField(
        max_length=50, blank=True, default=''
    )

    delai_estime = models.PositiveIntegerField(
        default=0
    )

    note = models.TextField(blank=True, default='')

    client=models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='commandes',
    )

    serveur=models.ForeignKey(
        Serveur,
        on_delete=models.CASCADE,
        related_name='commandes_preparees'
    )




    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = generer_reference(PREFIXES['commande'])
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "commande"
        verbose_name_plural = "commandes"




class LigneCommande(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=generer_uuid7,
        editable=False
    )

    reference = models.CharField(
        max_length=30,
        unique=True,
        editable=False
    )

    quantite = models.PositiveIntegerField()
    instructions = models.TextField(
        blank=True, default=''
    )

    commande = models.ForeignKey(
        Commande,
        on_delete=models.CASCADE,
        related_name='lignes'
    )


    plat = models.ForeignKey(
        Plat,
        on_delete=models.PROTECT,
        related_name='lignes_commande'
    )

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = generer_reference(PREFIXES['commande'])
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Ligne Commande"
        verbose_name_plural = "Lignes Commandes"
