"""
CREATION DE LA Commande Django  run_etl.
Orchestre le chargement complet du DataWarehouse.
Usage : python manage.py run_etl
"""
import pandas as pd
# importation des bibliotheques
from django.core.management import BaseCommand
from django.db import transaction

from warehouse.models import DimTemps,DimRegion,DimClient,DimVendeur,DimProduit, FaitArticleCommande
from warehouse.etl.temps import build_dim_temps
from warehouse.etl.regions import build_dim_region
from warehouse.etl.clients import build_dim_client
from  warehouse.etl.vendeurs import build_dim_vendeur
from warehouse.etl.produits import build_dim_produit
from warehouse.etl.faits import build_fait_article_commande

# creation de la classe commande
class Command(BaseCommand):
    help = 'chargement du data warehouse depuis les sources de donnees csv'
    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("demarrage du pipeline ETL..."))

        with transaction.atomic():

            self.stdout.write("Suppression des données existantes...")
            FaitArticleCommande.objects.all().delete()
            # chargements des dimensions

            # dimension Region
            self.stdout.write("\n DimRegion")
            data=build_dim_region()
            DimRegion.objects.all().delete()
            DimRegion.objects.bulk_create([
                DimRegion(etat=row["etat"], grande_region=row["grande_region"])
                for _, row in data.iterrows()
            ])
            self.stdout.write(f"total observation de DimRegion: {len(data)}")

            # dimension temps
            self.stdout.write("DimTemps")
            data=build_dim_temps()
            DimTemps.objects.all().delete()
            DimTemps.objects.bulk_create([
                DimTemps(
                    date=row["date"],
                    annee=row["annee"],
                    trimestre=row["trimestre"],
                    mois=row["mois"],
                    jour_semaine=row["jour_semaine"],
                )
                for _,row in data.iterrows()
            ])
            self.stdout.write(f"total observation de DimTemps: {len(data)}")

            self.stdout.write("DimClient")
            data=build_dim_client()
            DimClient.objects.all().delete()
            DimClient.objects.bulk_create([
                DimClient(
                    customer_unique_id=row["customer_unique_id"],
                    ville=row["ville"],
                    code_postal_prefix=row["code_postal_prefix"],
                )
                for _,row in data.iterrows()
            ])
            self.stdout.write(f"total observation de DimClient: {len(data)}")

            self.stdout.write("DimVendeur")
            data=build_dim_vendeur()
            DimVendeur.objects.all().delete()
            DimVendeur.objects.bulk_create([
                DimVendeur(
                    seller_id=row["seller_id"],
                    ville=row["ville"],
                    code_postal_prefix=row["code_postal_prefix"],
                )
                for _,row in data.iterrows()
            ])
            self.stdout.write(f"total observation de DimVendeur: {len(data)}")

            self.stdout.write("DimProduit")
            data=build_dim_produit()
            DimProduit.objects.all().delete()
            DimProduit.objects.bulk_create([
                DimProduit(
                    product_id=row["product_id"],
                    categorie_portugais=row["categorie_portugais"],
                    categorie_anglais=row["categorie_anglais"],
                    poids=row["poids"],
                )
                for _, row in data.iterrows()
            ])
            self.stdout.write(f"total observation de DimProduit: {len(data)}")

            # contruction de la table de faits
            self.stdout.write("faits FaitArticleCommande ...")
            data=build_fait_article_commande()

            # construction des maps pour retrouver les objects
            clients={c.customer_unique_id: c for c in DimClient.objects.all()}
            produits={p.product_id: p for p in DimProduit.objects.all()}
            vendeurs={v.seller_id:v for v in DimVendeur.objects.all()}
            regions={r.etat: r for r in DimRegion.objects.all()}
            temps={t.date: t for t in DimTemps.objects.all()}

            FaitArticleCommande.objects.all().delete()

            # chargement par lot
            batch=[]
            total=len(data)
            for i,row in data.iterrows():
                batch.append(FaitArticleCommande(
                    order_id=row["order_id"],
                    order_item_id=row["order_item_id"],
                    client=clients.get(row["client_id"]),
                    produit=produits.get(row["produit_id"]),
                    vendeur=vendeurs.get(row["vendeur_id"]),
                    region_client=regions.get(row["region_client_etat"]),
                    region_vendeur=regions.get(row["region_vendeur_etat"]),
                    date_achat=temps.get(
                        row["date_achat"].date() if hasattr(row["date_achat"], "date") else row["date_achat"]),
                    price=row["price"],
                    freight_value=row["freight_value"],
                    delai_livraison_jour=row["delai_livraison_jour"] if not pd.isna(
                        row["delai_livraison_jour"]) else None,
                    delai_estime_jour=row["delai_estime_jour"] if not pd.isna(row["delai_estime_jour"]) else None,
                    retard_jour=row["retard_jour"] if not pd.isna(row["retard_jour"]) else None,
                    est_en_retard=row["est_en_retard"] if not pd.isna(row["est_en_retard"]) else None,
                    review_score=row["review_score"] if not pd.isna(row["review_score"]) else None,
                    statut_commande=row["statut_commande"],
                ))
                if len(batch)>=5000:
                    FaitArticleCommande.objects.bulk_create(batch)
                    batch=[]
                    self.stdout.write(f"... {min(i+1,total)}/{total}")
            if batch:
                FaitArticleCommande.objects.bulk_create(batch)
            self.stdout.write(f"FaitArticleCommande: {len(data)}")
        self.stdout.write(self.style.SUCCESS("pipeline ETL termine avec succes!"))




