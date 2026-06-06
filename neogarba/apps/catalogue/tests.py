from rest_framework.test import APITestCase
from rest_framework import status
from apps.utilisateurs.models import Utilisateur
from apps.catalogue.models import CategorieMenu, Plat, OptionPersonnalisation


class CatalogueTestCase(APITestCase):

    def setUp(self):
        # Créer un vendeur
        self.vendeur = Utilisateur.objects.create_user(
            username='vendeur_test',
            email='vendeur@test.com',
            password='test1234',
            telephone='0700000001',
            role='VENDEUR'
        )
        # Créer un client
        self.client_user = Utilisateur.objects.create_user(
            username='client_test',
            email='client@test.com',
            password='test1234',
            telephone='0700000002',
            role='CLIENT'
        )
        # Créer une catégorie de test
        self.categorie = CategorieMenu.objects.create(
            nom='Garba Classique'
        )
        # Créer un plat de test
        self.plat = Plat.objects.create(
            nom='Garba Thon Rouge',
            prix=500,
            description='Le classique',
            categorie=self.categorie,
            disponibilite='DISPONIBLE',
            quantite_stock=50
        )
        # Créer une option de test
        self.option = OptionPersonnalisation.objects.create(
            type='ACCOMPAGNEMENT', 
            prix_supplement=0,
            disponible=True,
            plat=self.plat
        )

    # ─── TESTS CATÉGORIES ─────────────────────────────────

    def test_lister_categories(self):
        """Tout le monde peut lister les catégories"""
        response = self.client.get('/api/catalogue/liste/categories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_creer_categorie_vendeur(self):
        """Le vendeur peut créer une catégorie"""
        self.client.force_authenticate(user=self.vendeur)
        data = {'nom': 'Nouvelle Catégorie'}
        response = self.client.post('/api/catalogue/create/categories/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_creer_categorie_client_refuse(self):
        """Un client ne peut PAS créer une catégorie → 403"""
        self.client.force_authenticate(user=self.client_user)
        data = {'nom': 'Catégorie Interdite'}
        response = self.client.post('/api/catalogue/create/categories/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_supprimer_categorie_avec_plats(self):
        """Supprimer une catégorie qui contient des plats doit retourner une erreur"""
        self.client.force_authenticate(user=self.vendeur)
        response = self.client.delete(f'/api/catalogue/delete/categories/{self.categorie.id}/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ─── TESTS PLATS ──────────────────────────────────────

    def test_lister_plats(self):
        """Tout le monde peut lister les plats"""
        response = self.client.get('/api/catalogue/plats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_filtrer_plats_par_categorie(self):
        """Filtrer les plats par catégorie"""
        response = self.client.get(f'/api/catalogue/plats/?categorie={self.categorie.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_filtrer_plats_par_disponibilite(self):
        """Filtrer les plats par disponibilité"""
        response = self.client.get('/api/catalogue/plats/?disponibilite=DISPONIBLE')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_detail_plat_avec_options(self):
        """Le détail d'un plat inclut ses options"""
        response = self.client.get(f'/api/catalogue/plats/{self.plat.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('options', response.data)

    def test_creer_plat_vendeur(self):
        """Le vendeur peut créer un plat"""
        self.client.force_authenticate(user=self.vendeur)
        data = {
            'nom': 'Garba Thon Blanc',
            'prix': 600,
            'description': 'Avec thon blanc',
            'categorie': self.categorie.id,
            'disponibilite': 'DISPONIBLE',
            'quantite_stock': 30
        }
        response = self.client.post('/api/catalogue/plats/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_modifier_plat(self):
        """Le vendeur peut modifier un plat"""
        self.client.force_authenticate(user=self.vendeur)
        data = {
            'nom': 'Garba Modifié',
            'prix': 700,
            'description': 'Modifié',
            'categorie': self.categorie.id,
            'disponibilite': 'DISPONIBLE',
            'quantite_stock': 20
        }
        response = self.client.put(f'/api/catalogue/plats/{self.plat.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_supprimer_plat(self):
        """Le vendeur peut supprimer un plat sans commande"""
        plat_sans_commande = Plat.objects.create(
            nom='Plat à supprimer',
            prix=300,
            categorie=self.categorie,
            disponibilite='DISPONIBLE',
            quantite_stock=10
        )
        self.client.force_authenticate(user=self.vendeur)
        response = self.client.delete(f'/api/catalogue/plats/{plat_sans_commande.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_mettre_a_jour_stock(self):
        """Le vendeur peut mettre à jour le stock d'un plat"""
        self.client.force_authenticate(user=self.vendeur)
        data = {
            'quantite_stock': 100,
            'disponibilite': 'DISPONIBLE'
        }
        response = self.client.put(f'/api/catalogue/plats/{self.plat.id}/stock/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # ─── TESTS OPTIONS ────────────────────────────────────

    def test_ajouter_option(self):
        """Le vendeur peut ajouter une option à un plat"""
        self.client.force_authenticate(user=self.vendeur)
        data = {
            'type': 'BOISSON',  
            'prix_supplement': 0,
            'disponible': True,
            'plat': self.plat.id
        }
        response = self.client.post(f'/api/catalogue/plats/{self.plat.id}/options/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_modifier_option(self):
        """Le vendeur peut modifier une option"""
        self.client.force_authenticate(user=self.vendeur)
        data = {
            'type': 'TYPE_POISSON',  
            'prix_supplement': 50,
            'disponible': True,
            'plat': self.plat.id
        }
        response = self.client.put(f'/api/catalogue/options/{self.option.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_supprimer_option(self):
        """Le vendeur peut supprimer une option"""
        self.client.force_authenticate(user=self.vendeur)
        response = self.client.delete(f'/api/catalogue/options/{self.option.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)