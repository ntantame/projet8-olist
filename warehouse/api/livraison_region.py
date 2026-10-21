from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Avg, Count, Q, F
from warehouse.models import FaitArticleCommande
from rest_framework.permissions import IsAuthenticated


class LivraisonParRegionView(APIView):
    permission_classes = [IsAuthenticated]


    def get(self, request):
        # On ne regarde que les commandes livrées
        livrees = FaitArticleCommande.objects.filter(statut_commande='delivered')

        # On regroupe par région du client
        stats = (
            livrees
            .values('region_client__etat')
            .annotate(
                delai_moyen=Avg('delai_livraison_jours'),
                total_livraisons=Count('id'),
                # On compte combien sont en retard 
                retards=Count('id', filter=Q(est_en_retard=True))
            )
            .order_by('region_client__etat')
        )

        resultat = []
        for s in stats:
            total = s['total_livraisons'] or 1
            taux_retard = (s['retards'] / total) * 100

            resultat.append({
                'etat': s['region_client__etat'],
                'delai_moyen_jours': round(s['delai_moyen'], 2) if s['delai_moyen'] else None,
                'taux_retard_pourcentage': round(taux_retard, 2),
                'total_livraisons': total
            })

        return Response(resultat)