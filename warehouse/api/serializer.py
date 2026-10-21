# importation du module de base de DRF pour les serializer
from rest_framework import serializers

# classe pour la gestion des KPIs
class KPIsResumeSerializer(serializers.Serializer):
    CA_total = serializers.FloatField()
    total_commandes = serializers.IntegerField()
    delai_moyen=serializers.FloatField()
    taux_retard=serializers.FloatField()
    score_moyen=serializers.FloatField()

# classe pour la gestion des ventes par periodes
class VentesPeriodeSerializer(serializers.Serializer):
    periode=serializers.CharField()
    CA= serializers.FloatField()
    total_commandes=serializers.IntegerField()

# classe pour la gestion des ventes par categorie
class VentesCategorieSerializer(serializers.Serializer):
    categorie=serializers.CharField()
    CA= serializers.FloatField()
    total_vente=serializers.IntegerField()


# classe pour la gestion des livraison par region
class LivraisonParRegionSerializer(serializers.Serializer):
    region=serializers.CharField()
    delai_moyen=serializers.FloatField()
    taux_retard=serializers.FloatField()
    total_livraison=serializers.IntegerField()

# classe pour la gestiond de la satisfaction
class SatisfactionParRegionSerializer(serializers.Serializer):
    region=serializers.CharField()
    score_moyen=serializers.FloatField()
    total_avis=serializers.IntegerField()