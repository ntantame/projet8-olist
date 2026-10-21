from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum, Count
from warehouse.models import FaitArticleCommande
from rest_framework.permissions import IsAuthenticated


class VentesParCategorieView(APIView):
    permission_classes = [IsAuthenticated]
   
    def get(self, request):

        statuts_exclus = ['canceled', 'unavailable']


        ventes = (
            FaitArticleCommande.objects
            .exclude(statut_commande__in=statuts_exclus)
            .values('produit__categorie_anglais')
            .annotate(
                chiffre_affaires=Sum('price'),
                nombre_articles=Count('id')
            )
            .order_by('-chiffre_affaires')
        )


        resultat = [
            {
                'categorie': v['produit__categorie_anglais'] or 'inconnue',
                'chiffre_affaires': float(v['chiffre_affaires'] or 0),
                'nombre_articles': v['nombre_articles']
            }
            for v in ventes
        ]

        return Response(resultat)