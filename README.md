# Projet 8 — Pipeline ETL & BI : ventes e-commerce (Olist)

**Master 2 Data Science — Développement Web en Python**
**Durée** : 3 semaines — **Groupe de 3**

---

##  Équipe et répartition

| Membre | Rôle | Branche de travail                         |
|--------|------|--------------------------------------------|
| @ntantame | Modèles Django + DimTemps + FaitArticleCommande + Industrialisation | `feature/dim-temps-faits/ntantame`         |
| @fouelarissa | DimClient + DimVendeur | `feature/dim-client-vendeur/fouelarissa`   |
| @kendricdonald | DimProduit + DimRegion | `feature/dim-produit-region/kendricdonald` |

---

##  Règles du groupe

- **Une tâche = une branche = une Pull Request** relue par un autre membre
- **Chacun committe régulièrement** sous son propre compte (pas de commits groupés en fin de projet)
- **Point de synchronisation** tous les 2 jours (15 min)
- **Une part modeste mais maîtrisée** vaut mieux qu'une grosse part non comprise

---

## Workflow Git

### Règles strictes

-  **JAMAIS de push direct sur `main`** (branche protégée)
-  Toute contribution passe par une **branche `feature/...`**
-  **1 approbation** obligatoire avant merge dans `main`
-  **Toutes les conversations** doivent être résolues avant merge

### Cycle de travail

```bash
# 1. Récupérer les dernières modifications
git fetch origin

# 2. Passer sur sa branche
git checkout feature/dim-client-vendeur   # (adapter selon votre branche)

# 3. Travailler, puis commiter
git add .
git commit -m "feat: dimension client + vendeur"

# 4. Pousser sur sa branche
git push origin feature/dim-client-vendeur

# 5. Ouvrir une Pull Request sur GitHub
# → Un autre membre approuve
# → Merge dans main