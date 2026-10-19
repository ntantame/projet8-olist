# importation des outils de calcul
from django.db.models import Sum,Count
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

# importation de la table de faits
from warehouse.models import FaitArticleCommande

# exlcusion des commandes annulees ou indisponibles
STATUTS_EXCLUS=["canceled","unavailable"]

# creation de la classe des ventes par periode
class VentesParPeriodeView(APIView):
    # gestion de la connection pour visualiser les donnees
    permission_classes = [IsAuthenticated]

    def get(self,request):
        # recuperation des lignes du data warehouse en excluant les commandes annulees et indisponible
        lignes=FaitArticleCommande.objects.exclude(statut_commande__in=STATUTS_EXCLUS)

        granularite=request.query_params.get("granularite","mois")

        if granularite=="trimestre":
            colonne_periode="date_achat__trimestre"
        else:
            colonne_periode="date_achat__mois"

        resultats = (lignes
                     .values("date_achat__annee", colonne_periode)
                     .annotate(CA=Sum("price"),total_commandes=Count("order_id", distinct=True),)
                     .order_by("date_achat__annee", colonne_periode))

        # liste finale
        liste=[]
        for ligne in resultats:
            liste.append({
                "periode": f"{ligne['date_achat__annee']}-{ligne[colonne_periode]:02d}",
                "CA": round(ligne["CA"],2),
                "total_commandes": ligne["total_commandes"],
            })

        return Response(liste)


