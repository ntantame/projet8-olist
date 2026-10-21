from django.urls import path
from .api import kpis, ventes_periode, agent
from .api.ventes_categorie import VentesParCategorieView
from .api.livraison_region import LivraisonParRegionView
from .api.satisfaction_region import SatisfactionParRegionView

urlpatterns = [
    # mes endpoints
    path("kpis/resume/", kpis.KPIsResumeView.as_view(), name="kpis-resume"),
    path("ventes/par-periode/", ventes_periode.VentesParPeriodeView.as_view(), name="ventes-periode"),
    path("agent/ask/", agent.AgentAskView.as_view(), name="agent-ask"),

    # les endpoints de @kendricdonald
    path("ventes/par-categorie/", VentesParCategorieView.as_view(), name="ventes-categorie"),
    path("livraison/par-region/", LivraisonParRegionView.as_view(), name="livraison-region"),
    path("satisfaction/par-region/", SatisfactionParRegionView.as_view(), name="satisfaction-region"),
]