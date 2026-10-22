from django.db.models import Sum, Avg
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from warehouse.models import FaitArticleCommande
from .filtres import application_filtres

STATUTS_EXCLUS = ["canceled", "unavailable"]


class KPIsResumeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        lignes = FaitArticleCommande.objects.all()

        # Application des filtres magiques
        lignes = application_filtres(lignes, request)

        ventes = lignes.exclude(statut_commande__in=STATUTS_EXCLUS)
        CA = ventes.aggregate(total=Sum("price"))["total"] or 0

        total_commande = lignes.values("order_id").distinct().count()
        delai = lignes.aggregate(moyenne=Avg("delai_livraison_jour"))["moyenne"] or 0

        lignes_delai = lignes.filter(est_en_retard__isnull=False)
        total = lignes_delai.count()
        if total > 0:
            total_retard = lignes.filter(est_en_retard=True).count()
            taux_retard = total_retard / total * 100
        else:
            taux_retard = 0

        score = lignes.aggregate(moyenne=Avg("review_score"))["moyenne"] or 0

        return Response({
            "CA_total": round(CA, 2),
            "total_commandes": total_commande,
            "delai_moyen": round(float(delai), 2),
            "taux_retard": round(taux_retard, 2),
            "score_moyen": round(float(score), 2),
        })