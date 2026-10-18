"""
   CONTRUCTION DE LA TABLE DE FAITS
"""

# importation des bibliotheques
import  pandas as pd
from pathlib import Path



# redirection vers les sources de donnees
data_dir=Path(__file__).resolve().parent.parent.parent/"data"/"raw"
# fonction de chargement des faits
def build_fait_article_commande():
    # chargement des fichiers csv
    commande=pd.read_csv(data_dir/"olist_orders_dataset.csv")
    articles=pd.read_csv(data_dir/"olist_order_items_dataset.csv")
    reviews=pd.read_csv(data_dir/"olist_order_reviews_dataset.csv")
    customers=pd.read_csv(data_dir/"olist_customers_dataset.csv")
    vendeur=pd.read_csv(data_dir/"olist_sellers_dataset.csv")

    # conversion des dates en datetime
    commande["order_purchase_timestamp"]=pd.to_datetime(commande["order_purchase_timestamp"])
    commande["order_delivered_customer_date"]=pd.to_datetime(commande["order_delivered_customer_date"])
    commande["order_estimated_delivery_date"]=pd.to_datetime(commande["order_estimated_delivery_date"])
    reviews["review_answer_timestamp"]=pd.to_datetime(reviews["review_answer_timestamp"])

    # jointure entre commande et article
    faits=articles.merge(
        commande[["order_id", "customer_id","order_status","order_purchase_timestamp",
                  "order_delivered_customer_date","order_estimated_delivery_date"]],
        on="order_id",
        how="left"
     )

    # calcul des delais en jours

    # delai de livraison
    faits["delai_livraison_jour"]=(
        faits["order_delivered_customer_date"]- faits["order_purchase_timestamp"]
    ).dt.days

    # delai estime
    faits["delai_estime_jour"]=(
        faits["order_estimated_delivery_date"]-faits["order_purchase_timestamp"]
    ).dt.days

    # retard de livraison
    faits["retard_jour"]=(
        faits["order_delivered_customer_date"]-faits["order_estimated_delivery_date"]
    ).dt.days

    # verification du retard
    faits["est_en_retard"]=faits["retard_jour"]>0

    # dedloublonnage des avis pour ne garder que l'avis le plus recent
    reviews_clean=(
        reviews.sort_values(["order_id","review_answer_timestamp","review_id"]).drop_duplicates("order_id", keep="last")
    )

    # jointure sur les avis : left join pour conserver les commandes sans avis
    faits=faits.merge(
        reviews_clean[["order_id","review_score"]],
        on="order_id",
        how="left"
    )

    # jointure des regions(clients)
    client=customers[["customer_id","customer_unique_id","customer_state"]].rename(
        columns={"customer_state":"region_client_etat"}
    )
    faits=faits.merge(client,on="customer_id",how="left")

    # jointure sur region(vendeurs)
    vendeur_clean=vendeur[["seller_id","seller_state"]].rename(columns={"seller_state":"region_vendeur_etat"})
    faits=faits.merge(vendeur_clean,on="seller_id",how="left")

    # renommage + selection
    faits=faits.rename(columns={
        "customer_unique_id":"client_id",
        "product_id":"produit_id",
        "seller_id":"vendeur_id",
        "order_status":"statut_commande",
        "order_purchase_timestamp":"date_achat",
    })

    colonnes_finales=[
    "order_id","order_item_id","client_id","produit_id","vendeur_id",
    "region_client_etat","region_vendeur_etat","date_achat","price",
    "freight_value","delai_livraison_jour","delai_estime_jour","retard_jour",
    "est_en_retard","review_score","statut_commande",
    ]
    faits=faits[colonnes_finales]

    assert len(faits)==112650
    assert faits.duplicated(subset=["order_id","order_item_id"]).sum()==0

    return faits