# utilisateurs/tests/test_auth.py
import os

from django.urls import reverse
from django.utils import timezone

from rest_framework.test import APITestCase
from rest_framework import status

from utilisateurs.models import Utilisateur, CodeOTP

TEST_EMAIL = os.environ['TEST_USER_EMAIL']
TEST_PASSWORD = os.environ['TEST_USER_PASSWORD']
TEST_NEW_PASSWORD = os.environ['TEST_USER_NEW_PASSWORD']
TEST_OTP_CODE = os.environ['TEST_OTP_CODE']
TEST_OTP_CODE_EXPIRED = os.environ['TEST_OTP_CODE_EXPIRED']
TEST_WRONG_PASSWORD = os.environ['TEST_WRONG_PASSWORD']


def creer_utilisateur(email=TEST_EMAIL, password=TEST_PASSWORD, **kwargs):
    user = Utilisateur.objects.create_user(
        email=email,
        password=password,
        first_name='Jean',
        last_name='Dupont',
        **kwargs
    )
    return user


class ConnexionTests(APITestCase):

    def setUp(self):
        self.url = reverse('auth-connexion')
        self.user = creer_utilisateur()

    def test_connexion_reussie(self):
        data = {'email': TEST_EMAIL, 'password': TEST_PASSWORD}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])

    def test_connexion_mot_de_passe_incorrect(self):
        data = {'email': TEST_EMAIL, 'password': TEST_WRONG_PASSWORD}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_connexion_compte_inactif(self):
        self.user.is_active = False
        self.user.save()
        data = {'email': TEST_EMAIL, 'password': TEST_PASSWORD}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class DeconnexionTests(APITestCase):

    def setUp(self):
        self.user = creer_utilisateur()
        self.client.force_authenticate(user=self.user)
        self.url = reverse('auth-deconnexion')

    def _get_refresh_token(self):
        from rest_framework_simplejwt.tokens import RefreshToken
        return str(RefreshToken.for_user(self.user))

    def test_deconnexion_reussie(self):
        refresh = self._get_refresh_token()
        response = self.client.post(self.url, {'refresh': refresh})
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ProfilTests(APITestCase):

    def setUp(self):
        self.user = creer_utilisateur()
        self.url_detail = reverse('auth-profil')
        self.url_modifier = reverse('auth-modifier-profil')

    def test_consulter_profil(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user.email)

    def test_modifier_profil(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.url_modifier, {'first_name': 'Pierre'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['utilisateur']['first_name'], 'Pierre')

    def test_profil_sans_token(self):
        response = self.client.get(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ChangerMotDePasseTests(APITestCase):

    def setUp(self):
        self.user = creer_utilisateur()
        self.client.force_authenticate(user=self.user)
        self.url = reverse('auth-changer-mdp')

    def test_changer_mot_de_passe_reussi(self):
        data = {
            'ancien_mot_de_passe': TEST_PASSWORD,
            'nouveau_mot_de_passe': TEST_NEW_PASSWORD,
            'confirmer_mot_de_passe': TEST_NEW_PASSWORD,
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_ancien_mot_de_passe_incorrect(self):
        data = {
            'ancien_mot_de_passe': TEST_WRONG_PASSWORD,
            'nouveau_mot_de_passe': TEST_NEW_PASSWORD,
            'confirmer_mot_de_passe': TEST_NEW_PASSWORD,
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ReinitialiserMotDePasseTests(APITestCase):

    def setUp(self):
        self.user = creer_utilisateur()
        self.url_demande = reverse('auth-mdp-oublie')
        self.url_reinit = reverse('auth-reinitialiser-mdp')

    def test_demande_reinitialisation(self):
        response = self.client.post(self.url_demande, {'email': self.user.email})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_reinitialisation_complete(self):
        code = CodeOTP.objects.create(
            utilisateur=self.user,
            code=TEST_OTP_CODE,
            usage='reinitialisation',
            expire_a=timezone.now() + timezone.timedelta(minutes=15),
        )
        data = {
            'email': self.user.email,
            'code_otp': TEST_OTP_CODE,
            'nouveau_mot_de_passe': TEST_NEW_PASSWORD,
            'confirmer_mot_de_passe': TEST_NEW_PASSWORD,
        }
        response = self.client.post(self.url_reinit, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_reinitialisation_code_expire(self):
        code = CodeOTP.objects.create(
            utilisateur=self.user,
            code=TEST_OTP_CODE_EXPIRED,
            usage='reinitialisation',
            expire_a=timezone.now() - timezone.timedelta(minutes=1),
        )
        data = {
            'email': self.user.email,
            'code_otp': TEST_OTP_CODE_EXPIRED,
            'nouveau_mot_de_passe': TEST_NEW_PASSWORD,
            'confirmer_mot_de_passe': TEST_NEW_PASSWORD,
        }
        response = self.client.post(self.url_reinit, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
