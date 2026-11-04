# agent conversationnel sur les KPIs du data warehouse

import unicodedata
from drf_spectacular.utils import extend_schema
from dotenv import load_dotenv
from django.db.models import Sum, Avg, Count

from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from warehouse.models import FaitArticleCommande
from django.db.models import Q

# chargement du fichier .env
load_dotenv()


# fonction de retrait des accents
def enlever_accents(texte):
    if not texte:
        return texte
    texte_sans_accent = unicodedata.normalize('NFKD', texte).encode('ASCII', 'ignore').decode('utf-8')
    return texte_sans_accent.lower()


@tool
def get_ca_total(region: str | None = None, ville: str | None = None, annee: int | None = None, categorie: str | None = None) -> str:
    """retourne le chiffre d'affaires total excluant les commandes annulées"""
    statuts_exclus = ["canceled", "unavailable"]
    lignes = FaitArticleCommande.objects.exclude(statut_commande__in=statuts_exclus)

    if region: lignes = lignes.filter(region_client__etat=region.upper())
    if ville:
        ville_propre = enlever_accents(ville)
        lignes = lignes.filter(client__ville__icontains=ville_propre)
    if annee: lignes = lignes.filter(date_achat__annee=annee)
    if categorie: lignes = lignes.filter(produit__categorie_anglais__iexact=categorie)

    total = lignes.aggregate(total=Sum("price"))["total"] or 0
    return f"Le chiffre d'affaire total est de {round(float(total), 2)} R$."


@tool
def get_total_commandes(region: str | None = None, ville: str | None = None, annee: int | None = None, categorie: str | None = None) -> str:
    """Retourne le nombre total de commandes distinctes. Accepte des filtres optionnels (region, ville, annee, categorie)."""
    lignes = FaitArticleCommande.objects.all()

    if region: lignes = lignes.filter(region_client__etat=region.upper())
    if ville:
        ville_propre = enlever_accents(ville)
        lignes = lignes.filter(client__ville__icontains=ville_propre)
    if annee: lignes = lignes.filter(date_achat__annee=annee)
    if categorie: lignes = lignes.filter(produit__categorie_anglais__iexact=categorie)

    total_cmde = lignes.values("order_id").distinct().count() or 0
    return f"Le data warehouse possede {total_cmde} commandes distinctes (avec les filtres appliques)."


@tool
def get_delai_moyenne(region: str | None = None, ville: str | None = None, annee: int | None = None, categorie: str | None = None) -> str:
    """Retourne le delai moyen de livraison en jours. Accepte des filtres optionnels (region, ville, annee, categorie)."""
    lignes = FaitArticleCommande.objects.all()

    if region: lignes = lignes.filter(region_client__etat=region.upper())
    if ville:
        ville_propre = enlever_accents(ville)
        lignes = lignes.filter(client__ville__icontains=ville_propre)
    if annee: lignes = lignes.filter(date_achat__annee=annee)
    if categorie: lignes = lignes.filter(produit__categorie_anglais__iexact=categorie)

    moyenne = lignes.aggregate(m=Avg("delai_livraison_jour"))["m"] or 0
    return f"Le delai moyen de livraison est de {round(float(moyenne), 2)} jours (avec les filtres appliques)."


@tool
def get_taux_retard(region: str | None = None, ville: str | None = None, annee: int | None = None) -> str:
    """Retourne le taux de retard de livraison en pourcentage. Accepte des filtres optionnels (region, ville, annee)."""

    requete = FaitArticleCommande.objects.filter(est_en_retard__isnull=False)

    if region: requete = requete.filter(region_client__etat=region.upper())
    if ville:
        ville_propre = enlever_accents(ville)
        requete = requete.filter(client__ville__icontains=ville_propre)
    if annee: requete = requete.filter(date_achat__annee=annee)

    total = requete.count()
    if total == 0:
        return "Pas de donnees de retard disponibles pour ces criteres."

    total_retards = requete.filter(est_en_retard=True).count()
    taux = (total_retards / total) * 100
    return f"Le taux de retard est de {round(taux, 2)} % (avec les filtres appliques)."


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
        return "Aucune donnee de vente par categorie disponible."

    texte = "Voici le chiffre d'affaires par categorie :Top 10 :\n"
    for r in resultats:
        categorie = r['produit__categorie_anglais'] or "Non renseignee"
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


@tool
def get_ca_par_region(annee: int | None = None) -> str:
    """Retourne le chiffre d'affaires total regroupé par région. Accepte un filtre optionnel sur l'année (ex: annee=2017)."""
    statuts_exclus = ["canceled", "unavailable"]
    lignes = FaitArticleCommande.objects.exclude(statut_commande__in=statuts_exclus)

    if annee:
        lignes = lignes.filter(date_achat__annee=annee)

    resultats = lignes.values('region_client__etat') \
        .annotate(total=Sum('price')) \
        .order_by('-total')

    if not resultats:
        return "Aucune donnée de vente par région disponible pour ces critères."

    texte = f"Voici le chiffre d'affaires par région" + (f" pour l'année {annee}" if annee else "") + " :\n"
    for r in resultats:
        region = r['region_client__etat'] or "Inconnue"
        total = round(float(r['total'] or 0), 2)
        texte += f"- {region} : {total} R$\n"
    return texte


@tool
def analyser_anomalies_retards() -> str:
    """
    detecte les pics de retards anormaux ,pour chaque anomalie, identifie les régions les plus touchées pour aider
    a formuler une hypothese causale.
    """
    total_filtre = FaitArticleCommande.objects.filter(est_en_retard__isnull=False)
    total_global = total_filtre.count()
    if total_global == 0:
        return "pas assez de données pour analyser les retards."

    retards_globaux = total_filtre.filter(est_en_retard=True).count()
    taux_moyen_global = (retards_globaux / total_global) * 100

    stats_mois = total_filtre.values('date_achat__annee', 'date_achat__mois') \
        .annotate(
        nb_total=Count('id'),
        nb_retards=Count('id', filter=Q(est_en_retard=True))
    ).order_by('date_achat__annee', 'date_achat__mois')

    texte_final = f"Taux de retard moyen global : {round(taux_moyen_global, 2)} %\n\n"
    anomalies_trouvees = False

    for m in stats_mois:
        if m['nb_total'] < 100:
            continue

        taux_mois = (m['nb_retards'] / m['nb_total']) * 100

        if taux_mois > (taux_moyen_global * 1.5):
            anomalies_trouvees = True
            annee = m['date_achat__annee']
            mois = m['date_achat__mois']

            texte_final += f"ANOMALIE DETECTEE : {mois:02d}/{annee}\n"
            texte_final += f"- Taux de retard ce mois-la : {round(taux_mois, 2)} % (sur {m['nb_total']} commandes)\n"

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

            delai_moyen = total_filtre.filter(
                date_achat__annee=annee,
                date_achat__mois=mois
            ).aggregate(m=Avg("delai_livraison_jour"))["m"] or 0

            texte_final += f"- Delai de livraison moyen ce mois-la : {round(float(delai_moyen), 2)} jours\n\n"

    if not anomalies_trouvees:
        return "Aucune anomalie majeure de retard détectee (aucun mois ne dépasse 1.5x la moyenne globale)."

    return texte_final


@tool
def get_top_flop_ca_par_region() -> str:
    """Retourne la région avec le chiffre d'affaires le plus élevé et celle avec le plus bas."""
    statuts_exclus = ["canceled", "unavailable"]
    stats = FaitArticleCommande.objects.exclude(statut_commande__in=statuts_exclus) \
        .values('region_client__etat') \
        .annotate(CA=Sum('price')) \
        .order_by('-CA')

    if not stats:
        return "Pas de données disponibles."

    top_region = stats.first()
    flop_region = stats.last()

    return (f"La région avec le CA le plus élevé est {top_region['region_client__etat']} "
            f"avec {round(float(top_region['CA']), 2)} R$.\n"
            f"La région avec le CA le plus bas est {flop_region['region_client__etat']} "
            f"avec {round(float(flop_region['CA']), 2)} R$.")


@tool
def get_top_flop_ca_par_ville() -> str:
    """Retourne la ville avec le chiffre d'affaires le plus élevé et celle avec le plus bas (parmi les villes ayant au moins 100 commandes)."""
    statuts_exclus = ["canceled", "unavailable"]
    stats = FaitArticleCommande.objects.exclude(statut_commande__in=statuts_exclus) \
        .values('client__ville') \
        .annotate(CA=Sum('price'), nb_cmd=Count('order_id', distinct=True)) \
        .filter(nb_cmd__gte=100) \
        .order_by('-CA')

    if not stats:
        return "Pas de données disponibles."

    top_ville = stats.first()
    flop_ville = stats.last()

    return (f"La ville avec le CA le plus élevé est {top_ville['client__ville'].title()} "
            f"avec {round(float(top_ville['CA']), 2)} R$.\n"
            f"La ville avec le CA le plus bas (minimum 100 commandes) est {flop_ville['client__ville'].title()} "
            f"avec {round(float(flop_ville['CA']), 2)} R$.")


@tool
def get_top_flop_categories_par_region(region: str, limite: int = 2) -> str:
    """Retourne les N catégories de produits avec le CA le plus bas et le plus élevé pour une région donnée.
    - region: l'état (ex: 'SP').
    - limite: le nombre de catégories à afficher (par défaut 2)."""
    statuts_exclus = ["canceled", "unavailable"]
    lignes = FaitArticleCommande.objects.exclude(statut_commande__in=statuts_exclus)

    lignes = lignes.filter(region_client__etat=region.upper())

    stats = lignes.values('produit__categorie_anglais') \
        .annotate(total=Sum('price')) \
        .order_by('total')

    if not stats:
        return f"Aucune donnée disponible pour la région {region}."

    # Utilisation de la limite dynamique
    plus_basses = stats[:limite]
    plus_hautes = list(stats)[-limite:]

    texte = f"Pour la région {region.upper()} :\n"
    texte += f"Top {limite} des catégories au CA le plus BAS :\n"
    for r in plus_basses:
        texte += f"- {r['produit__categorie_anglais']} : {round(float(r['total']), 2)} R$\n"

    texte += f"\nTop {limite} des catégories au CA le plus HAUT :\n"
    for r in reversed(plus_hautes):
        texte += f"- {r['produit__categorie_anglais']} : {round(float(r['total']), 2)} R$\n"

    return texte


@tool
def get_top_regions_moins_retard_avec_ca(limite: int = 3) -> str:
    """Retourne les N régions ayant le taux de retard le plus bas, avec leur chiffre d'affaires respectif.
    - limite: le nombre de régions à afficher (par défaut 3)."""
    statuts_exclus = ["canceled", "unavailable"]

    stats_retard = FaitArticleCommande.objects.filter(est_en_retard__isnull=False) \
        .values('region_client__etat') \
        .annotate(
        total=Count('id'),
        retards=Count('id', filter=Q(est_en_retard=True))
    )

    regions_triees = []
    for r in stats_retard:
        if r['total'] > 100:
            taux = (r['retards'] / r['total']) * 100
            regions_triees.append({'etat': r['region_client__etat'], 'taux': taux})

    # Utilisation de la limite dynamique
    regions_triees = sorted(regions_triees, key=lambda x: x['taux'])[:limite]

    texte = f"Voici les {limite} régions avec le taux de retard le plus bas et leur chiffre d'affaires :\n"
    for reg in regions_triees:
        ca = FaitArticleCommande.objects.exclude(statut_commande__in=statuts_exclus) \
                 .filter(region_client__etat=reg['etat']) \
                 .aggregate(total=Sum('price'))['total'] or 0

        texte += f"- {reg['etat']} : Taux de retard de {round(reg['taux'], 2)} % | CA de {round(float(ca), 2)} R$\n"

    return texte


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
    permission_classes = [AllowAny]

    def post(self, request):
        question = request.data.get("question", "").strip()

        if not question:
            return Response({"erreur": "question vide"}, status=400)

        llm = ChatGroq(
            model="openai/gpt-oss-120b",
            temperature=0,
        )

        tools = [
            get_ca_total,
            get_total_commandes,
            get_delai_moyenne,
            get_taux_retard,
            get_score_moyenne,
            get_ventes_par_categorie,
            get_ca_par_region,
            get_top_flop_categories_par_region,
            get_top_regions_moins_retard_avec_ca,
            get_livraison_par_region,
            get_satisfaction_par_region,
            analyser_anomalies_retards,
            get_top_flop_ca_par_region,
            get_top_flop_ca_par_ville
        ]

        agent = create_react_agent(llm, tools)

        try:
            resultat = agent.invoke({"messages": [("user", question)]})
            reponse = resultat["messages"][-1].content
            return Response({"reponse": reponse})
        except Exception as e:
            return Response({"erreur": str(e)}, status=500)