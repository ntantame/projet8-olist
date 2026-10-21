from django.urls import path
from .api import ventes_periode, kpis, agent

urlpatterns = [
    path("kpis/resume/", kpis.KPIsResumeView.as_view(), name="kpis-rsume"),
    path("ventes/par-periode/", ventes_periode.VentesParPeriodeView.as_view(), name="ventes-par-periode"),
    path("agent/ask/",agent.AgentAskView.as_view(), name="agent-ask"),
]