from django.utils import timezone
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
        help_text="Reference metier"
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



class Client(Utilisateur):
    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"

    def save(self, *args, **kwargs):
        self.role = RoleEnum.CLIENT
        super().save(*args, **kwargs)



class Serveur(Utilisateur):
    class Meta:
        verbose_name = "Serveur"
        verbose_name_plural = "Serveurs"

    def save(self, *args, **kwargs):
        self.role = RoleEnum.SERVEUR
        super().save(*args, **kwargs)



class Livreur(Utilisateur):
    class Meta:
        verbose_name = "Livreur"
        verbose_name_plural = "Livreurs"

    def save(self, *args, **kwargs):
        self.role = RoleEnum.LIVREUR
        super().save(*args, **kwargs)

class Vendeur(Utilisateur):
    class Meta:
        verbose_name = "Vendeur"
        verbose_name_plural = "Vendeurs"

    def save(self, *args, **kwargs):
        self.role = RoleEnum.VENDEUR
        super().save(*args, **kwargs)

class Administrateur(Utilisateur):
    class Meta:
        verbose_name = "Administrateur"
        verbose_name_plural = "Administrateurs"

    def save(self, *args, **kwargs):
        self.role = RoleEnum.ADMINISTRATEUR
        super().save(*args, **kwargs)


class AdresseLivraison(models.Model):
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

    libelle = models.CharField(max_length=50)

    adresse_complete = models.CharField(max_length=255)

    quartier = models.CharField(max_length=100)

    est_par_defaut = models.BooleanField(default=False)

    client = models.ForeignKey(Client,
                               on_delete=models.CASCADE,
                               related_name='adresse'
                               )

    class Meta:
        verbose_name = "Adresse de Livraison"
        verbose_name_plural = "Adresses de Livraisons"

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = generer_reference(PREFIXES['adresse'])
        super().save(*args, **kwargs)


class CodeOTP(models.Model):
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

    utilisateur = models.ForeignKey(Utilisateur,
                                   on_delete=models.CASCADE,
                                   related_name='code_otp',
                                   )
    code = models.CharField(max_length=6)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_expiration = models.DateTimeField()
    est_utilise = models.BooleanField(default=False)


    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = generer_reference(PREFIXES['codeotp'])
        super().save(*args, **kwargs)


    def est_expire(self):
        return timezone.now() > self.date_expiration

    def est_valide(self):
        return not self.est_utilise and not self.est_expire()


    class Meta:
        verbose_name = "Code OTP"
        verbose_name_plural = "Codes OTP"
