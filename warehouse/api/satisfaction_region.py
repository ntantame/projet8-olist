from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Avg
from warehouse.models import FaitArticleCommande
from rest_framework.permissions import IsAuthenticated
from .filtres import application_filtres


class SatisfactionParRegionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        ventes = FaitArticleCommande.objects.exclude(review_score__isnull=True)

        # APPLICATION DES FILTRES GLOBAUX
        ventes = application_filtres(ventes, request)

        stats = (
            ventes
            .values('region_client__etat')
            .annotate(note_moyenne=Avg('review_score'))
            .order_by('-note_moyenne')
        )

        resultat = [
            {
                'etat': v['region_client__etat'],
                'note_moyenne': round(v['note_moyenne'], 2) if v['note_moyenne'] else None
            }
            for v in stats
        ]
        return Response(resultat)