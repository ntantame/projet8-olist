from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Avg, Count
from warehouse.models import FaitArticleCommande

class SatisfactionParRegionView(APIView):

    def get(self, request):
        # On ignore les commandes sans note
        ventes = (
            FaitArticleCommande.objects
            .exclude(review_score__isnull=True)
            .values('region_client__etat')
            .annotate(

                note_moyenne=Avg('review_score')
            )
            .order_by('-note_moyenne')
        )

        resultat = [
            {
                'etat': v['region_client__etat'],
                'note_moyenne': round(v['note_moyenne'], 2) if v['note_moyenne'] else None
            }
            for v in ventes
        ]

        return Response(resultat)