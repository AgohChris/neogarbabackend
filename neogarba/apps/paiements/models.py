from django.db import models

from apps.commandes.models import Commande
# Create your models here.

from apps.cores.utils import *
from apps.cores.enums import *
from apps.utilisateurs.models import *
from apps.catalogue.models import *

class Paiement(models.Model):
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

    montant = models.PositiveIntegerField()

    moyen = models.CharField(
        max_length=30,
        choices=MoyenPaiementEnum.choices
    )
    statut = models.CharField(
        max_length=30,
        choices=StatutPaiementEnum.choices,
        default=StatutPaiementEnum.EN_ATTENTE
    )

    commande = models.ForeignKey(
        Commande,
        on_delete=models.PROTECT,
        related_name='paiement'
    )





    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = generer_reference(PREFIXES['paiement'])
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Paiement"
        verbose_name_plural = "Paiements"







