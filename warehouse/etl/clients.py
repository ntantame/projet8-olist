"""
   CONTRUCTION DE LA DIMENSION REGION
"""

# importation des bibliotheques
import  pandas as pd
from pathlib import Path

# redirection vers les sources de donnees
data_dir=Path(__file__).resolve().parent.parent.parent/"data"/"raw"

# fonction du chargement des clients

def build_dim_client():
    client=pd.read_csv(data_dir/"olist_customers_dataset.csv",
    dtype={"customer_zip_code_prefix" : str})
    commande=pd.read_csv(data_dir/"olist_orders_dataset.csv")
    commande["order_purchase_timestamp"]=pd.to_datetime(commande["order_purchase_timestamp"])

    cmd=commande.merge(client,how="left",on="customer_id")

    dim_client=pd.DataFrame(cmd
               .sort_values("order_purchase_timestamp")
               .drop_duplicates("customer_unique_id", keep="last")
               .reset_index(drop=True)
               .rename(columns={
                  "customer_city":"ville",
                   "customer_zip_code_prefix":"code_postal_prefix",
    })
        [["customer_unique_id","ville","code_postal_prefix"]]
    )
    assert len(dim_client)==96096
    assert dim_client["customer_unique_id"].is_unique

    return dim_client