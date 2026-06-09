from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.core import mail

from apps.cores.enums import StatutCommandeEnum, StatutLivraisonEnum, ModeRecuperationEnum, RoleEnum
from apps.commandes.models import Commande
from apps.utilisateurs.models import Client, Serveur, Livreur, Utilisateur, AdresseLivraison
from .models import Livraison

class LivraisonsAPITestCase(APITestCase):
    def setUp(self):
        # 1. Create client user
        self.client_user = Client.objects.create_user(
            username="client1",
            email="client1@example.com",
            password="password123",
            telephone="0102030405"
        )
        
        # 2. Create another client (for ownership tests)
        self.other_client = Client.objects.create_user(
            username="client2",
            email="client2@example.com",
            password="password123",
            telephone="0203040506"
        )

        # 3. Create AdresseLivraison for client1
        self.adresse_livraison = AdresseLivraison.objects.create(
            libelle="Maison",
            adresse_complete="Riviera 3 Villa 45",
            quartier="Cocody",
            client=self.client_user
        )

        # 4. Create server user
        self.serveur_user = Serveur.objects.create_user(
            username="serveur1",
            email="serveur1@example.com",
            password="password123",
            telephone="0304050607"
        )

        # 5. Create livreur user
        self.livreur_user = Livreur.objects.create_user(
            username="livreur1",
            email="livreur1@example.com",
            password="password123",
            telephone="0405060708"
        )

        # 6. Create another active livreur
        self.livreur_user_2 = Livreur.objects.create_user(
            username="livreur2",
            email="livreur2@example.com",
            password="password123",
            telephone="0506070809"
        )

        # 7. Create a prete command for client1 with LIVRAISON_DOMICILE (valid)
        self.commande_prete = Commande.objects.create(
            client=self.client_user,
            serveur=self.serveur_user,
            montant_total=1300,
            statut=StatutCommandeEnum.PRETE,
            mode_recuperation=ModeRecuperationEnum.LIVRAISON_DOMICILE
        )

        # 8. Create a not prete command (e.g. RECUE)
        self.commande_recue = Commande.objects.create(
            client=self.client_user,
            serveur=self.serveur_user,
            montant_total=1300,
            statut=StatutCommandeEnum.RECUE,
            mode_recuperation=ModeRecuperationEnum.LIVRAISON_DOMICILE
        )

        # 9. Create a prete command with RETRAIT_SUR_PLACE
        self.commande_retrait = Commande.objects.create(
            client=self.client_user,
            serveur=self.serveur_user,
            montant_total=1300,
            statut=StatutCommandeEnum.PRETE,
            mode_recuperation=ModeRecuperationEnum.RETRAIT_SUR_PLACE
        )

    def test_creer_livraison(self):
        self.client.force_authenticate(user=self.serveur_user)
        url = reverse('creer-livraison')
        data = {
            "commande_id": str(self.commande_prete.id),
            "adresse_livraison_id": str(self.adresse_livraison.id)
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], StatutLivraisonEnum.EN_ATTENTE)
        self.assertEqual(response.data['adresse'], self.adresse_livraison.adresse_complete)
        self.assertEqual(response.data['quartier'], self.adresse_livraison.quartier)
        self.assertEqual(response.data['telphone_client'], self.client_user.telephone)

    def test_creer_livraison_commande_pas_prete(self):
        self.client.force_authenticate(user=self.serveur_user)
        url = reverse('creer-livraison')
        data = {
            "commande_id": str(self.commande_recue.id),
            "adresse_livraison_id": str(self.adresse_livraison.id)
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_creer_livraison_retrait_sur_place(self):
        self.client.force_authenticate(user=self.serveur_user)
        url = reverse('creer-livraison')
        data = {
            "commande_id": str(self.commande_retrait.id),
            "adresse_livraison_id": str(self.adresse_livraison.id)
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_assigner_livreur(self):
        # First create delivery
        livraison = Livraison.objects.create(
            commande=self.commande_prete,
            adresse=self.adresse_livraison.adresse_complete,
            quartier=self.adresse_livraison.quartier,
            telphone_client=self.client_user.telephone,
            status=StatutLivraisonEnum.EN_ATTENTE
        )
        
        self.client.force_authenticate(user=self.serveur_user)
        url = reverse('assigner-livreur', kwargs={'pk': livraison.id})
        data = {
            "livreur_id": str(self.livreur_user.id)
        }
        
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(str(response.data['livreur']), str(self.livreur_user.id))
        
        # Verify command status
        self.commande_prete.refresh_from_db()
        self.assertEqual(self.commande_prete.statut, StatutCommandeEnum.LIVRAISON_EN_COURS)

    def test_assigner_livreur_email_envoye(self):
        livraison = Livraison.objects.create(
            commande=self.commande_prete,
            adresse=self.adresse_livraison.adresse_complete,
            quartier=self.adresse_livraison.quartier,
            telphone_client=self.client_user.telephone,
            status=StatutLivraisonEnum.EN_ATTENTE
        )
        
        mail.outbox.clear()
        
        self.client.force_authenticate(user=self.serveur_user)
        url = reverse('assigner-livreur', kwargs={'pk': livraison.id})
        data = {
            "livreur_id": str(self.livreur_user.id)
        }
        
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify email
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.client_user.email])
        self.assertIn("est en route", mail.outbox[0].body)
        self.assertIn(self.livreur_user.first_name, mail.outbox[0].body)

    def test_mes_livraisons_livreur(self):
        # Create deliveries assigned to self.livreur_user
        livraison1 = Livraison.objects.create(
            commande=self.commande_prete,
            adresse=self.adresse_livraison.adresse_complete,
            quartier=self.adresse_livraison.quartier,
            telphone_client=self.client_user.telephone,
            status=StatutLivraisonEnum.EN_ATTENTE,
            livreur=self.livreur_user
        )
        
        self.client.force_authenticate(user=self.livreur_user)
        url = reverse('mes-livraisons')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], str(livraison1.id))

    def test_maj_statut_en_cours(self):
        livraison = Livraison.objects.create(
            commande=self.commande_prete,
            adresse=self.adresse_livraison.adresse_complete,
            quartier=self.adresse_livraison.quartier,
            telphone_client=self.client_user.telephone,
            status=StatutLivraisonEnum.EN_ATTENTE,
            livreur=self.livreur_user
        )
        
        self.client.force_authenticate(user=self.livreur_user)
        url = reverse('maj-statut-livraison', kwargs={'pk': livraison.id})
        data = {
            "status": StatutLivraisonEnum.EN_COURS
        }
        
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], StatutLivraisonEnum.EN_COURS)

    def test_maj_statut_livree(self):
        # Starting status must be EN_COURS for transition to LIVREE to be valid
        livraison = Livraison.objects.create(
            commande=self.commande_prete,
            adresse=self.adresse_livraison.adresse_complete,
            quartier=self.adresse_livraison.quartier,
            telphone_client=self.client_user.telephone,
            status=StatutLivraisonEnum.EN_COURS,
            livreur=self.livreur_user
        )
        
        mail.outbox.clear()
        
        self.client.force_authenticate(user=self.livreur_user)
        url = reverse('maj-statut-livraison', kwargs={'pk': livraison.id})
        data = {
            "status": StatutLivraisonEnum.LIVREE
        }
        
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], StatutLivraisonEnum.LIVREE)
        
        # Verify command status
        self.commande_prete.refresh_from_db()
        self.assertEqual(self.commande_prete.statut, StatutCommandeEnum.LIVREE)
        
        # Verify email
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.client_user.email])
        self.assertIn("a ete livre", mail.outbox[0].body)

    def test_maj_statut_transition_invalide(self):
        # EN_ATTENTE -> LIVREE is invalid
        livraison = Livraison.objects.create(
            commande=self.commande_prete,
            adresse=self.adresse_livraison.adresse_complete,
            quartier=self.adresse_livraison.quartier,
            telphone_client=self.client_user.telephone,
            status=StatutLivraisonEnum.EN_ATTENTE,
            livreur=self.livreur_user
        )
        
        self.client.force_authenticate(user=self.livreur_user)
        url = reverse('maj-statut-livraison', kwargs={'pk': livraison.id})
        data = {
            "status": StatutLivraisonEnum.LIVREE
        }
        
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_maj_non_livreur_refuse(self):
        livraison = Livraison.objects.create(
            commande=self.commande_prete,
            adresse=self.adresse_livraison.adresse_complete,
            quartier=self.adresse_livraison.quartier,
            telphone_client=self.client_user.telephone,
            status=StatutLivraisonEnum.EN_COURS,
            livreur=self.livreur_user
        )
        
        # Authenticate as server instead of assigned livreur
        self.client.force_authenticate(user=self.serveur_user)
        url = reverse('maj-statut-livraison', kwargs={'pk': livraison.id})
        data = {
            "status": StatutLivraisonEnum.LIVREE
        }
        
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_livreurs_disponibles(self):
        # We created two active livreurs in setUp
        self.client.force_authenticate(user=self.serveur_user)
        url = reverse('livreurs-disponibles')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
        # Check matching keys
        self.assertEqual(response.data[0]['nom'], self.livreur_user.last_name)
        self.assertEqual(response.data[0]['prenom'], self.livreur_user.first_name)
        self.assertEqual(response.data[0]['telephone'], self.livreur_user.telephone)
