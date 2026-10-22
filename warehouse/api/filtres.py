def application_filtres(queryset, request):
    # Applique les filtres globaux (date, région, catégorie, ville) à un queryset.

    if request.query_params.get("date_debut"):
        queryset = queryset.filter(date_achat__date__gte=request.query_params["date_debut"])

    if request.query_params.get("date_fin"):
        queryset = queryset.filter(date_achat__date__lte=request.query_params["date_fin"])

    if request.query_params.get("region"):
        queryset = queryset.filter(region_client__etat=request.query_params["region"])

    if request.query_params.get("categorie"):
        queryset = queryset.filter(produit__categorie_anglais=request.query_params["categorie"])

    if request.query_params.get("ville"):
        queryset = queryset.filter(client__ville__iexact=request.query_params["ville"])

    return queryset