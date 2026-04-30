from django.db import models

from apps.commandes.models import Commande
# Create your models here.

from apps.cores.utils import *
from apps.cores.enums import *
from apps.utilisateurs.models import *
from apps.catalogue.models import *

class Livraison(models.Model):
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

    adresse = models.CharField(
        max_length=255,
    )
    quartier = models.CharField(
        max_length=255,
    )
    telphone_client=models.CharField(max_length=15)

    status = models.CharField(
        max_length=20,
        choices=StatutLivraisonEnum.choices,
        default=StatutLivraisonEnum.EN_ATTENTE
    )

    commande = models.OneToOneField(
        Commande,
        on_delete=models.CASCADE,
        related_name='livraison'
    )

    livreur = models.ForeignKey(
        Livreur,
        on_delete=models.SET_NULL,
        related_name='livraisons',
        null=True,
        blank=True
    )





    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = generer_reference(PREFIXES['livraison'])
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Livraison"
        verbose_name_plural = "Livraisons"
