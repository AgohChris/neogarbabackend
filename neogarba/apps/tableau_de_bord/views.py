from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Sum, Count

from apps.commandes.models import Commande, LigneCommande
from apps.utilisateurs.models import Utilisateur
from .permissions import EstAdministrateur


# Resume du jour

class ResumeView(APIView):
    """
    Retourne les stats générales du jour en un seul appel.
    Accessible uniquement à l'administrateur.
    """
    permission_classes = [IsAuthenticated, EstAdministrateur]

    def get(self, request):
        aujourd_hui = timezone.now().date()

        # Nombre de commandes du jour
        commandes_du_jour = Commande.objects.filter(
            date_commande__date=aujourd_hui
        ).count()

        # Chiffre d'affaires du jour (seulement les paiements REUSSI)
        chiffre_affaires = Commande.objects.filter(
            date_commande__date=aujourd_hui,
            paiement__statut='REUSSI'
        ).aggregate(total=Sum('montant_total'))['total'] or 0

        # Nombre total de clients inscrits
        total_clients = Utilisateur.objects.filter(
            role='CLIENT'
        ).count()

        # Commandes en attente (statut REÇUE)
        commandes_en_attente = Commande.objects.filter(
            statut='RECUE'
        ).count()

        return Response({
            'commandes_du_jour': commandes_du_jour,
            'chiffre_affaires_du_jour': chiffre_affaires,
            'total_clients': total_clients,
            'commandes_en_attente': commandes_en_attente,
        })


# Ventes par periode

class VentesView(APIView):
    """
    Retourne le chiffre d'affaires filtré par période.
    Paramètres : ?periode=jour ou ?periode=semaine ou ?periode=mois
    """
    permission_classes = [IsAuthenticated, EstAdministrateur]

    def get(self, request):
        aujourd_hui = timezone.now().date()
        periode = request.query_params.get('periode', 'jour')

        if periode == 'semaine':
            debut = aujourd_hui - timezone.timedelta(days=7)
        elif periode == 'mois':
            debut = aujourd_hui - timezone.timedelta(days=30)
        else:
            debut = aujourd_hui

        chiffre_affaires = Commande.objects.filter(
            date_commande__date__gte=debut,
            paiement__statut='REUSSI'
        ).aggregate(total=Sum('montant_total'))['total'] or 0

        return Response({
            'periode': periode,
            'chiffre_affaires': chiffre_affaires,
            'du': str(debut),
            'au': str(aujourd_hui),
        })


# plat populaires

class PlatsPopulairesView(APIView):
    """
    Retourne le top 10 des plats les plus commandés.
    Utilise LigneCommande pour compter les quantités.
    """
    permission_classes = [IsAuthenticated, EstAdministrateur]

    def get(self, request):
        top_plats = LigneCommande.objects.values(
            'plat__nom',
            'plat__prix',
        ).annotate(
            total_commandes=Sum('quantite')
        ).order_by('-total_commandes')[:10]

        return Response(list(top_plats))


# commandes par statuts

class CommandesParStatutView(APIView):
    """
    Retourne le nombre de commandes par statut.
    Ex: REÇUE: 5, EN_PREPARATION: 3, PRÊTE: 2
    """
    permission_classes = [IsAuthenticated, EstAdministrateur]

    def get(self, request):
        resultats = Commande.objects.values('statut').annotate(
            total=Count('id')
        ).order_by('statut')

        data = {item['statut']: item['total'] for item in resultats}

        return Response(data)