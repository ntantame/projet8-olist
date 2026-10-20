from django.urls import path
from .api import ventes_periode,kpis
from .api.ventes_categorie import VentesParCategorieView
from .api.livraison_region import LivraisonParRegionView
from .api.satisfaction_region import SatisfactionParRegionView
urlpatterns = [
    path("kpis/resume/", kpis.KPIsResumeView.as_view(), name="kpis-rsume"),
    path("ventes/par-periode/", ventes_periode.VentesParPeriodeView.as_view(), name="ventes-par-periode"),
    path('ventes/par-categorie/', VentesParCategorieView.as_view(), name='ventes-categorie'),
    path('livraison/par-region/', LivraisonParRegionView.as_view(), name='livraison-region'),
    path('satisfaction/par-region/', SatisfactionParRegionView.as_view(), name='satisfaction-region'),
]