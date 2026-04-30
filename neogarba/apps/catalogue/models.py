
from django.db import models
from apps.cores.utils import *
from apps.cores.enums import *

# Create your models here.

class CategorieMenu(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=generer_uuid7,
        editable=False,
    )

    reference = models.CharField(
        max_length=255,
        unique=True,
        editable=False,
    )

    nom = models.CharField(max_length=150)
    image = models.ImageField(upload_to="categories/", null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = generer_reference(PREFIXES['categorie'])
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Categorie"
        verbose_name_plural = "Categories"


class Plat(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=generer_uuid7,
        editable=False,
    )

    reference = models.CharField(
        max_length=30,
        unique=True,
        editable=False
    )

    nom = models.CharField(max_length=255)
    prix = models.PositiveIntegerField()
    description = models.TextField(
        blank=True, default=''
    )

    image = models.ImageField(upload_to="plats/",
                              null=True, blank=True)


    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = generer_reference(PREFIXES['plat'])
        super().save(*args, **kwargs)

    disponibilite = models.CharField(
        max_length=20,
        choices=DisponibiliteEnum.choices,
        default=DisponibiliteEnum.DISPONIBLE
    )

    quantite_stock = models.PositiveIntegerField(default=0)

    categorie = models.ForeignKey(
        CategorieMenu,
        on_delete=models.PROTECT,
        related_name='plats',
    )

    class Meta:
        verbose_name = "Plat"
        verbose_name_plural = "Plats"




class OptionPersonnalisation(models.Model):
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

    type = models.CharField(
        max_length=30,
        choices=TypeOptionEnum.choices
    )
    prix_supplement = models.PositiveIntegerField(
        default =0
    )

    disponible = models.BooleanField(
        default=True
    )

    plat = models.ForeignKey(
        Plat,
        on_delete=models.CASCADE,
        related_name='options',
    )

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = generer_reference(PREFIXES['option'])
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Option Personnalisation"
        verbose_name_plural = "Option Personnalisations"



