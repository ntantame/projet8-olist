# agent conversationnel sur les KPIs du data warehouse

from drf_spectacular.utils import extend_schema
from rest_framework import serializers
import os
from dotenv import load_dotenv
from django.db.models import Sum, Avg

from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from warehouse.models import FaitArticleCommande

# chargement du fichier .env
load_dotenv()


@tool
def get_ca_total() -> str:
    """Retourne le chiffre d'affaires total (hors commandes annulées)."""
    statuts_exclus = ["canceled", "unavailable"]
    lignes = FaitArticleCommande.objects.exclude(statut_commande__in=statuts_exclus)
    total = lignes.aggregate(total=Sum("price"))["total"] or 0
    return f"Le chiffre d'affaire total est de {round(float(total), 2)} R$."


@tool
def get_total_commandes() -> str:
    """Retourne le nombre total de commandes distinctes dans l'entrepôt."""
    total_cmde = FaitArticleCommande.objects.values("order_id").distinct().count() or 0
    return f"Le data warehouse possède {total_cmde} commandes distinctes."


@tool
def get_delai_moyenne() -> str:
    """Retourne le délai moyen de livraison en jours."""
    moyenne = FaitArticleCommande.objects.aggregate(m=Avg("delai_livraison_jour"))["m"] or 0
    return f"Le délai moyen de livraison est de {round(float(moyenne), 2)} jours."


@tool
def get_taux_retard() -> str:
    """Retourne le taux de retard de livraison en pourcentage."""
    total = FaitArticleCommande.objects.filter(est_en_retard__isnull=False).count()
    if total == 0:
        return "Pas de données de retard disponibles."
    total_retards = FaitArticleCommande.objects.filter(est_en_retard=True).count()
    taux = (total_retards / total) * 100
    return f"Le taux de retard est de {round(taux, 2)} %."


@tool
def get_score_moyenne() -> str:
    """Retourne le score moyen des clients (sur 5)."""
    moyenne = FaitArticleCommande.objects.aggregate(m=Avg("review_score"))["m"] or 0
    return f"Le score moyen des clients est de {round(float(moyenne), 2)}/5."



@extend_schema(request={
        'application/json': {
            'type': 'object',
            'properties': {
                'question': {'type': 'string'}
            },
            'required': ['question']
        }
    }
)
# VUE API
class AgentAskView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        question = request.data.get("question", "").strip()

        if not question:
            return Response({"erreur": "question vide"}, status=400)

        # initialisation du LLM groq
        llm = ChatGroq(
            model="openai/gpt-oss-120b",
            temperature=0,
        )

        # liste des outils
        tools = [
            get_ca_total, get_total_commandes, get_delai_moyenne,
            get_taux_retard, get_score_moyenne
        ]

        # creation de l'agent
        agent = create_react_agent(llm, tools)

        try:
            # nouvelle api
            resultat = agent.invoke({"messages": [("user", question)]})
            # recuperation du contenu du message
            reponse = resultat["messages"][-1].content
            return Response({"reponse": reponse})
        except Exception as e:
            return Response({"erreur": str(e)}, status=500)