from django.urls import path
from .api import ventes_periode,kpis
urlpatterns = [
    path("kpis/resume/", kpis.KPIsResumeView.as_view(), name="kpis-rsume"),
    path("ventes/par-periode/", ventes_periode.VentesParPeriodeView.as_view(), name="ventes-par-periode"),
]