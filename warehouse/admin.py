from django.contrib import admin
from .models import DimClient,DimRegion,DimTemps,DimProduit,DimVendeur,FaitArticleCommande

# Register your models here.
@admin.register(DimTemps)
class DimTempsAdmin(admin.ModelAdmin):
    list_display=["date","annee","trimestre","mois","jour_semaine"]
    list_filter = ["annee","trimestre","mois"]

@admin.register(DimClient)
class DimClientAdmin(admin.ModelAdmin):
    list_display=["customer_unique_id","ville","code_postal_prefix"]
    search_fields=["customer_unique_id","ville"]

@admin.register(DimProduit)
class DimProduitAdmin(admin.ModelAdmin):
    list_display=["product_id","categorie_portugais","categorie_anglais","poids"]
    list_filter = ["categorie_anglais"]

@admin.register(DimVendeur)
class DimVendeurAdmin(admin.ModelAdmin):
    list_display=["seller_id","ville","code_postal_prefix"]
    search_fields=["seller_id","ville"]

@admin.register(DimRegion)
class DimRegionAdmin(admin.ModelAdmin):
    list_display=["etat","grande_region"]
    list_filter = ["grande_region"]

@admin.register(FaitArticleCommande)
class FaitArticleCommandeAdmin(admin.ModelAdmin):
    list_display=["order_id","order_item_id","price","statut_commande"]
    list_filter = ["statut_commande","est_en_retard"]
    search_fields = ["order_id"]
