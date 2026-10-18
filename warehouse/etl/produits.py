"""
   CONTRUCTION DE LA DIMENSION PRODUITS
"""

# importation des bibliotheques
import  pandas as pd
from pathlib import Path



# redirection vers les sources de donnees
data_dir=Path(__file__).resolve().parent.parent.parent/"data"/"raw"

# fonction de chargement des produits

def build_dim_produit():
    produit = pd.read_csv(data_dir/"olist_products_dataset.csv")
    translation=pd.read_csv(data_dir/"product_category_name_translation.csv")

    dim_produit=produit.merge(translation,
                              on="product_category_name",how="left").rename(columns={
        "product_category_name":"categorie_portugais",
        "product_category_name_english":"categorie_anglais",
        "product_weight_g":"poids"
    })[["product_id","categorie_portugais","categorie_anglais","poids"]]


    assert len(dim_produit) == 32951
    assert dim_produit["product_id"].is_unique

    return dim_produit