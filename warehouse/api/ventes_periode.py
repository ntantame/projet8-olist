from django.db.models import Sum, Count
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from warehouse.models import FaitArticleCommande
from .filtres import application_filtres

STATUTS_EXCLUS = ["canceled", "unavailable"]


class VentesParPeriodeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        lignes = FaitArticleCommande.objects.exclude(statut_commande__in=STATUTS_EXCLUS)

        # Application des filtres magiques
        lignes = application_filtres(lignes, request)

        granularite = request.query_params.get("granularite", "mois")

        if granularite == "trimestre":
            colonne_periode = "date_achat__trimestre"
        else:
            colonne_periode = "date_achat__mois"

        resultats = (lignes
                     .values("date_achat__annee", colonne_periode)
                     .annotate(CA=Sum("price"), total_commandes=Count("order_id", distinct=True))
                     .order_by("date_achat__annee", colonne_periode))

        liste = []
        for ligne in resultats:
            liste.append({
                "periode": f"{ligne['date_achat__annee']}-{ligne[colonne_periode]:02d}",
                "CA": round(ligne["CA"], 2),
                "total_commandes": ligne["total_commandes"],
            })

        return Response(liste)