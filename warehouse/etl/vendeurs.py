"""
   CONTRUCTION DE LA DIMENSION REGION
"""

# importation des bbibliotheques
import  pandas as  pd
from pathlib import Path

# redirection vers les sources de donnees
data_dir=Path(__file__).resolve().parent.parent.parent/"data"/"raw"


# fonction de chargement
def build_dim_vendeur():
    vendeur=pd.read_csv(data_dir/"olist_sellers_dataset.csv",
                        dtype={"seller_zip_code_prefix":str})

    dim_vendeur=vendeur[["seller_id","seller_city","seller_zip_code_prefix"]].copy()
    dim_vendeur.columns=["seller_id","ville","code_postal_prefix"]

    assert len(dim_vendeur)==3095
    assert dim_vendeur["seller_id"].is_unique

    return dim_vendeur
