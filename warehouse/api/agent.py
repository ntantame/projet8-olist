# agent conversationnel sur les KPIs du data warehouse

from drf_spectacular.utils import extend_schema
from dotenv import load_dotenv
from django.db.models import Sum, Avg, Count

from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated , AllowAny

from warehouse.models import FaitArticleCommande
from django.db.models import Q

# chargement du fichier .env
load_dotenv()


@tool
def get_ca_total() -> str:
    """retourne le chiffre d'affaires total excluant les commandes annulées"""
    statuts_exclus = ["canceled", "unavailable"]
    lignes = FaitArticleCommande.objects.exclude(statut_commande__in=statuts_exclus)
    total = lignes.aggregate(total=Sum("price"))["total"] or 0
    return f"Le chiffre d'affaire total est de {round(float(total), 2)} R$."


@tool
def get_total_commandes() -> str:
    """retourne le nombre total de commandes distinctes du data ware house."""
    total_cmde = FaitArticleCommande.objects.values("order_id").distinct().count() or 0
    return f"Le data warehouse possede {total_cmde} commandes distinctes."


@tool
def get_delai_moyenne() -> str:
    """retourne le delai moyen de livraison en jours."""
    moyenne = FaitArticleCommande.objects.aggregate(m=Avg("delai_livraison_jour"))["m"] or 0
    return f"Le delai moyen de livraison est de {round(float(moyenne), 2)} jours."


@tool
def get_taux_retard() -> str:
    """retourne le taux de retard de livraison en pourcentage."""
    total = FaitArticleCommande.objects.filter(est_en_retard__isnull=False).count()
    if total == 0:
        return "Pas de données de retard disponibles."
    total_retards = FaitArticleCommande.objects.filter(est_en_retard=True).count()
    taux = (total_retards / total) * 100
    return f"Le taux de retard est de {round(taux, 2)} %."


@tool
def get_score_moyenne() -> str:
    """retourne le score moyen des clients sur 5."""
    moyenne = FaitArticleCommande.objects.aggregate(m=Avg("review_score"))["m"] or 0
    return f"Le score moyen des clients est de {round(float(moyenne), 2)}/5."


@tool
def get_ventes_par_categorie() -> str:
    """retourne le chiffre d'affaires total par categorie de produit."""
    statuts_exclus = ["canceled", "unavailable"]
    resultats = FaitArticleCommande.objects.exclude(statut_commande__in=statuts_exclus) \
        .values('produit__categorie_anglais') \
        .annotate(total=Sum('price')) \
        .order_by('-total')[:10]

    if not resultats:
        return "Aucune donnee de vente par catégorie disponible."

    texte = "Voici le chiffre d'affaires par catégorie :Top 10 :\n"
    for r in resultats:
        categorie = r['produit__categorie_anglais'] or "Non renseignée"
        total = round(float(r['total'] or 0), 2)
        texte += f"- {categorie} : {total} R$\n"
    return texte


@tool
def get_livraison_par_region() -> str:
    """retourne le nombre de commandes livrees par grande region du client."""
    statuts_exclus = ["canceled", "unavailable"]
    resultats = FaitArticleCommande.objects.exclude(statut_commande__in=statuts_exclus) \
        .values('region_client__grande_region') \
        .annotate(total_commandes=Count('order_id', distinct=True)) \
        .order_by('-total_commandes')

    texte = "Voici le nombre de commandes livrees par region :\n"
    for r in resultats:
        region = r['region_client__grande_region'] or "Inconnue"
        texte += f"- {region} : {r['total_commandes']} commandes\n"
    return texte


@tool
def get_satisfaction_par_region() -> str:
    """retourne le score de satisfaction moyen des clients par grande region."""
    resultats = FaitArticleCommande.objects.exclude(review_score__isnull=True) \
        .values('region_client__grande_region') \
        .annotate(score_moyen=Avg('review_score')) \
        .order_by('-score_moyen')

    texte = "Voici la satisfaction moyenne par region :\n"
    for r in resultats:
        region = r['region_client__grande_region'] or "Inconnue"
        score = round(float(r['score_moyen'] or 0), 2)
        texte += f"- {region} : {score}/5\n"
    return texte


from django.db.models import Q  # N'oublie pas cet import si tu ne l'as pas déjà


@tool
def analyser_anomalies_retards() -> str:
    """
    detecte les pics de retards anormaux ,pour chaque anomalie, identifie les régions les plus touchées pour aider
    a formuler une hypothese causale.
    """
    # Calcul du taux de retard global
    total_filtre = FaitArticleCommande.objects.filter(est_en_retard__isnull=False)
    total_global = total_filtre.count()
    if total_global == 0:
        return "pas assez de données pour analyser les retards."

    retards_globaux = total_filtre.filter(est_en_retard=True).count()
    taux_moyen_global = (retards_globaux / total_global) * 100

    # Analyse par mois via la dimension Temps
    stats_mois = total_filtre.values('date_achat__annee', 'date_achat__mois') \
        .annotate(
        nb_total=Count('id'),
        nb_retards=Count('id', filter=Q(est_en_retard=True))
    ).order_by('date_achat__annee', 'date_achat__mois')

    texte_final = f"Taux de retard moyen global : {round(taux_moyen_global, 2)} %\n\n"
    anomalies_trouvees = False

    for m in stats_mois:
        # On ignore les mois avec très peu de commandes (bruit statistique)
        if m['nb_total'] < 100:
            continue

        taux_mois = (m['nb_retards'] / m['nb_total']) * 100

        # Condition d'anomalie : 1.5 fois la moyenne globale
        if taux_mois > (taux_moyen_global * 1.5):
            anomalies_trouvees = True
            annee = m['date_achat__annee']
            mois = m['date_achat__mois']

            texte_final += f"ANOMALIE DETECTEE : {mois:02d}/{annee}\n"
            texte_final += f"- Taux de retard ce mois-la : {round(taux_mois, 2)} % (sur {m['nb_total']} commandes)\n"

            # Recherche de la cause : quelles regions ont le plus souffert ce mois-la ?
            regions_touchees = total_filtre.filter(
                date_achat__annee=annee,
                date_achat__mois=mois,
                est_en_retard=True
            ).values('region_client__grande_region') \
                .annotate(nb=Count('id')) \
                .order_by('-nb')[:3]

            texte_final += "- Regions les plus touchees par ces retards :\n"
            for r in regions_touchees:
                reg = r['region_client__grande_region'] or "Inconnue"
                texte_final += f"  * {reg} ({r['nb']} retards)\n"

            # On regarde aussi le délai moyen pour ce mois
            delai_moyen = total_filtre.filter(
                date_achat__annee=annee,
                date_achat__mois=mois
            ).aggregate(m=Avg("delai_livraison_jour"))["m"] or 0

            texte_final += f"- Delai de livraison moyen ce mois-la : {round(float(delai_moyen), 2)} jours\n\n"

    if not anomalies_trouvees:
        return "Aucune anomalie majeure de retard détectee (aucun mois ne dépasse 1.5x la moyenne globale)."

    return texte_final


#  LA VUE API

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

        # liste des outils (TOUS les outils sont ici !)
        tools = [
            get_ca_total,
            get_total_commandes,
            get_delai_moyenne,
            get_taux_retard,
            get_score_moyenne,
            get_ventes_par_categorie,
            get_livraison_par_region,
            get_satisfaction_par_region,
            analyser_anomalies_retards
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