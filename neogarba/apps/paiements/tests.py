from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.utils import timezone
from datetime import datetime, timedelta

from apps.cores.enums import MoyenPaiementEnum, StatutPaiementEnum, ModeRecuperationEnum, RoleEnum
from apps.commandes.models import Commande
from apps.utilisateurs.models import Client, Serveur, Utilisateur
from .models import Paiement

class PaiementsAPITestCase(APITestCase):
    def setUp(self):
        # Create a client user
        self.client_user = Client.objects.create_user(
            username="client1",
            email="client1@example.com",
            password="password123",
            telephone="0102030405"
        )
        
        # Create another client user (for ownership test)
        self.other_client = Client.objects.create_user(
            username="client2",
            email="client2@example.com",
            password="password123",
            telephone="0203040506"
        )

        # Create a serveur (required by Commande)
        self.serveur_user = Serveur.objects.create_user(
            username="serveur1",
            email="serveur1@example.com",
            password="password123",
            telephone="0304050607"
        )

        # Create an admin user
        self.admin_user = Utilisateur.objects.create_user(
            username="admin1",
            email="admin1@example.com",
            password="password123",
            role=RoleEnum.ADMINISTRATEUR,
            is_staff=True
        )

        # Create a command for client1
        self.commande = Commande.objects.create(
            client=self.client_user,
            serveur=self.serveur_user,
            montant_total=1300,
            mode_recuperation=ModeRecuperationEnum.LIVRAISON_DOMICILE
        )
        
        # Create another command for other_client
        self.other_commande = Commande.objects.create(
            client=self.other_client,
            serveur=self.serveur_user,
            montant_total=2500,
            mode_recuperation=ModeRecuperationEnum.RETRAIT_SUR_PLACE
        )

    def test_payer_commande_wave(self):
        self.client.force_authenticate(user=self.client_user)
        url = reverse('creer-paiement')
        data = {
            "commande_id": str(self.commande.id),
            "moyen": MoyenPaiementEnum.WAVE
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['statut'], StatutPaiementEnum.REUSSI)
        self.assertEqual(response.data['montant'], 1300)
        self.assertEqual(response.data['moyen'], MoyenPaiementEnum.WAVE)

    def test_payer_commande_orange_money(self):
        self.client.force_authenticate(user=self.client_user)
        url = reverse('creer-paiement')
        data = {
            "commande_id": str(self.commande.id),
            "moyen": MoyenPaiementEnum.ORANGE_MONEY
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['statut'], StatutPaiementEnum.REUSSI)
        self.assertEqual(response.data['montant'], 1300)
        self.assertEqual(response.data['moyen'], MoyenPaiementEnum.ORANGE_MONEY)

    def test_payer_commande_deja_payee(self):
        self.client.force_authenticate(user=self.client_user)
        url = reverse('creer-paiement')
        data = {
            "commande_id": str(self.commande.id),
            "moyen": MoyenPaiementEnum.WAVE
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Double payment attempt
        response2 = self.client.post(url, data, format='json')
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)

    def test_payer_commande_autre_client(self):
        self.client.force_authenticate(user=self.client_user)
        url = reverse('creer-paiement')
        data = {
            "commande_id": str(self.other_commande.id),
            "moyen": MoyenPaiementEnum.WAVE
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_detail_paiement(self):
        # Create a payment
        paiement = Paiement.objects.create(
            montant=1300,
            moyen=MoyenPaiementEnum.WAVE,
            commande=self.commande,
            statut=StatutPaiementEnum.REUSSI
        )
        self.client.force_authenticate(user=self.client_user)
        url = reverse('detail-paiement', kwargs={'pk': paiement.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['reference'], paiement.reference)

    def test_historique_admin(self):
        p1 = Paiement.objects.create(
            montant=1300,
            moyen=MoyenPaiementEnum.WAVE,
            commande=self.commande,
            statut=StatutPaiementEnum.REUSSI
        )
        p2 = Paiement.objects.create(
            montant=2500,
            moyen=MoyenPaiementEnum.ORANGE_MONEY,
            commande=self.other_commande,
            statut=StatutPaiementEnum.ECHOUE
        )
        
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('historique-paiements')
        
        # Test fetch all
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
        # Test filters
        response_statut = self.client.get(f"{url}?statut={StatutPaiementEnum.REUSSI}")
        self.assertEqual(len(response_statut.data), 1)
        self.assertEqual(response_statut.data[0]['id'], str(p1.id))

    def test_historique_non_admin_refuse(self):
        self.client.force_authenticate(user=self.client_user)
        url = reverse('historique-paiements')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
