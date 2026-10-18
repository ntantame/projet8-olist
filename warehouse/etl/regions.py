"""
   CONTRUCTION DE LA DIMENSION REGION
"""

# importation des bibliotheques
import  pandas as pd

grande_region={
    "Norte":["AC","AP","AM","PA","RO","RR","TO"],
    "Nordeste":["AL","BA","CE","MA","PB","PE","PI","RN","SE"],
    "Centro-Oeste":["DF","GO","MT","MS"],
    "Sudeste":["ES","MG","RJ","SP"],
    "Sul": ["PR","RS","SC"],
}

# fonction de chargement des regions

def build_dim_region():
    etat_region = {e: r for r, etats in grande_region.items() for e in etats}

    # construction du dataframe
    dim_region = pd.DataFrame([
        {"etat": etat, "grande_region": region}
        for etat, region in etat_region.items()
    ])

    assert len(dim_region) == 27
    assert dim_region["etat"].is_unique
    assert dim_region["grande_region"].nunique() == 5
    assert dim_region.isna().sum().sum() == 0

    return dim_region