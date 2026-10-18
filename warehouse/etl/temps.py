"""
   CONTRUCTION DE LA DIMENSION TEMPS
"""

# importation des bibliotheques
import  pandas as pd
from pathlib import Path

# redirection vers les sources de donnees
data_dir=Path(__file__).resolve().parent.parent.parent/"data"/"raw"

# fonction de chargement du dataset
def build_dim_temps():
    commande=pd.read_csv(data_dir/"olist_orders_dataset.csv")
    commande["order_purchase_timestamp"]=pd.to_datetime(commande["order_purchase_timestamp"])

    date_min=commande["order_purchase_timestamp"].min().date()
    date_max=commande["order_purchase_timestamp"].max().date()

    date=pd.date_range(start=date_min,end=date_max)
    dim_temps=pd.DataFrame({
        "date":date.date,
        "annee":date.year,
        "trimestre": date.quarter,
        "mois":date.month,
        "jour_semaine":date.dayofweek+1
        })

    assert len(dim_temps)==774, f"resultat attendu:774, resultat obtenu {len(dim_temps)}"
    assert dim_temps["date"].is_unique
    assert dim_temps.isna().sum().sum() == 0

    return dim_temps