from django.db import models

# Create your models here.


from django.db import models
from django.contrib.auth.models import AbstractUser

from apps.cores.utils import generer_uuid7, generer_reference, PREFIXES
from apps.cores.enums import RoleEnum


class Utilisateur(AbstractUser):
    id = models.UUIDField(
        primary_key=True,
        default=generer_uuid7,
        editable=False
    )

    reference = models.CharField(
        max_length=30,
        unique=True,
        editable=False,
        help_text="Reference metier (ex: USR-20260420-A1B2C3D4E5)"
    )

    telephone = models.CharField(
        max_length=20,
        help_text="Numero de telephone (ex: 0778748602)"
    )

    role = models.CharField(
        max_length=20,
        choices=RoleEnum.choices,
        default=RoleEnum.CLIENT
    )

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = generer_reference(PREFIXES['utilisateur'])
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"

    def __str__(self):
        return f"{self.last_name} {self.first_name} ({self.role})"
