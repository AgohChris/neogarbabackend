

# Create your tests here.
from rest_framework.test import APITestCase
from rest_framework import status
from django.utils import timezone
from apps.utilisateurs.models import Utilisateur
from apps.catalogue.models import CategorieMenu, Plat
from apps.commandes.models import Commande, LigneCommande
from apps.paiements.models import Paiement


class TableauDeBordTestCase(APITestCase):

    def setUp(self):
        # Créer un administrateur
        self.admin = Utilisateur.objects.create_user(
            username='admin_test',
            email='admin@test.com',
            password='test1234',
            telephone='0700000000',
            role='ADMINISTRATEUR'
        )
        # Créer un client
        self.client_user = Utilisateur.objects.create_user(
            username='client_test',
            email='client@test.com',
            password='test1234',
            telephone='0700000001',
            role='CLIENT'
        )
        # Créer une catégorie et un plat
        self.categorie = CategorieMenu.objects.create(nom='Garba Classique')
        self.plat = Plat.objects.create(
            nom='Garba Thon Rouge',
            prix=500,
            categorie=self.categorie,
            disponibilite='DISPONIBLE',
            quantite_stock=50
        )

    # test resume
    
    def test_resume_accessible_admin(self):
        """L'admin peut accéder au résumé"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/tableau-de-bord/resume/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_resume_refuse_client(self):
        """Un client ne peut PAS accéder au résumé → 403"""
        self.client.force_authenticate(user=self.client_user)
        response = self.client.get('/api/tableau-de-bord/resume/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_resume_refuse_non_connecte(self):
        """Un utilisateur non connecté ne peut PAS accéder → 401"""
        response = self.client.get('/api/tableau-de-bord/resume/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_resume_contient_bonnes_cles(self):
        """Le résumé contient les bonnes clés"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/tableau-de-bord/resume/')
        self.assertIn('commandes_du_jour', response.data)
        self.assertIn('chiffre_affaires_du_jour', response.data)
        self.assertIn('total_clients', response.data)
        self.assertIn('commandes_en_attente', response.data)

    # test ventes

    def test_ventes_par_jour(self):
        """L'admin peut voir les ventes du jour"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/tableau-de-bord/ventes/?periode=jour')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('chiffre_affaires', response.data)

    def test_ventes_par_semaine(self):
        """L'admin peut voir les ventes de la semaine"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/tableau-de-bord/ventes/?periode=semaine')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_ventes_par_mois(self):
        """L'admin peut voir les ventes du mois"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/tableau-de-bord/ventes/?periode=mois')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # test plats populaires

    def test_plats_populaires_accessible_admin(self):
        """L'admin peut voir les plats populaires"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/tableau-de-bord/plats-populaires/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_plats_populaires_refuse_client(self):
        """Un client ne peut PAS voir les plats populaires → 403"""
        self.client.force_authenticate(user=self.client_user)
        response = self.client.get('/api/tableau-de-bord/plats-populaires/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # test commandes par statuts

    def test_commandes_par_statut_accessible_admin(self):
        """L'admin peut voir les commandes par statut"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/tableau-de-bord/commandes-par-statut/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_commandes_par_statut_refuse_client(self):
        """Un client ne peut PAS voir les commandes par statut → 403"""
        self.client.force_authenticate(user=self.client_user)
        response = self.client.get('/api/tableau-de-bord/commandes-par-statut/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
