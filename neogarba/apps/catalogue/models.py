
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


