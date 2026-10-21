# importation des outils de calcul
from django.db.models import Sum,Avg
from rest_framework.views import APIView
from rest_framework.response import Response
from  rest_framework.permissions import IsAuthenticated


# importation  de la table de faits
from  warehouse.models import FaitArticleCommande

# exlcusion des commandes annulees ou indisponibles
STATUTS_EXCLUS=["canceled","unavailable"]

class KPIsResumeView(APIView):
    # gestion de la connection pour visualiser les donnees
    permission_classes = [IsAuthenticated]
    def get(self,request):
        # recuperation des lignes du datawarehouse
        lignes=FaitArticleCommande.objects.all()
        # application des filtres mis dans l'URL par les client
        if request.query_params.get("date_debut"):
            lignes=lignes.filter(date_achat__date__gte=request.query_params["date_debut"])
        if request.query_params.get("date_fin"):
            lignes=lignes.filter(date_achat__date__lt=request.query_params["date_fin"])
        if request.query_params.get("region"):
            lignes=lignes.filter(region_client__etat=request.query_params["region"])
        if request.query_params.get("categorie"):
            lignes=lignes.filter(produit__categorie_anglais=request.query_params["categorie"])

        # chiffre d'affaire: exclusion des commandes annules ou indisponibles
        ventes=lignes.exclude(statut_commande__in=STATUTS_EXCLUS)
        CA=ventes.aggregate(total=Sum("price"))["total"]
        if CA is None:
            CA=0

        # nombre de commande: compatage une seule fois chaque numero de commande
        total_commande=lignes.values("order_id").distinct().count()

        # delai moyende livraison
        delai=lignes.aggregate(moyenne=Avg("delai_livraison_jour"))["moyenne"]
        if delai is None:
            delai=0

        # taux de retard : conservation des lignes ou les retards sont connus
        lignes_delai=lignes.filter(est_en_retard__isnull=False)
        total=lignes_delai.count()

        if total>0:
            total_retard=lignes.filter(est_en_retard=True).count()
            taux_retard=total_retard/total*100
        else:
            taux_retard=0

        # score moyen
        score=lignes.aggregate(moyenne=Avg("review_score"))["moyenne"]
        if score is None:
            score=0

        return Response({
            "CA_total": round(CA,2),
            "total_commandes": total_commande,
            "delai_moyen": round(float(delai),2),
            "taux_retard": round(taux_retard,2),
            "score_moyen": round(float(score),2),
        })




