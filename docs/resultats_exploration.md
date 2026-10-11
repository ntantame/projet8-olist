# Constats d'exploration : Données Olist

> Document produit à l'issue de l'exploration commune
> Version 2 : chiffres vérifiés dans le notebook d'exploration

## 0. Vocabulaire

| Mot | Définition simple |
|-----|-------------------|
| Ligne / colonne | Une ligne = un enregistrement ; une colonne = une information |
| Clé de jointure | Colonne commune à deux fichiers (ex: `order_id`) |
| Doublon | Information répétée alors qu'elle devrait être unique |
| Valeur manquante (NULL) | Case vide : on ne connaît pas la valeur |
| Grain | Ce que représente une ligne de la table principale |
| Agréger | Regrouper plusieurs lignes en une (ex: moyenne) |
| Table de faits | Table des événements à mesurer (ventes) |
| Dimension | Table qui décrit un angle d'analyse (qui, quoi, où, quand) |

## 1. Vue d'ensemble des fichiers

| Fichier | Lignes | Col. | Une ligne représente...             | Rôle |
|---------|--------|------|-------------------------------------|------|
| customers | 99 441 | 5 | Un client sur une commande          | Qui achète |
| geolocation | 1 000 163 | 5 | Un point GPS par zip code (répété)  | Où |
| order_items | 112 650 | 7 | Un article dans une commande        | Quoi, à quel prix |
| order_payments | 103 886 | 5 | Un paiement                         | Comment on a payé |
| order_reviews | 99 224 | 7 | Un avis                             | Satisfaction |
| orders | 99 441 | 8 | Une commande                        | Cœur : statut + dates |
| products | 32 951 | 9 | Un produit                          | Catégorie, poids |
| sellers | 3 095 | 4 | Un vendeur                          | Qui vend |
| product_category_name_translation | 71 | 2 | Une catégorie(portuguais → anglais) | Libellés lisibles |

## 2. Clés de jointure

| Clé | Relie... | En mots simples |
|-----|----------|-----------------|
| `order_id` | orders, order_items, order_payments, order_reviews | N° de commande |
| `customer_id` | orders ↔ customers | Client de la commande |
| `product_id` | order_items ↔ products | Produit acheté |
| `seller_id` | order_items ↔ sellers | Vendeur de l'article |
| `geolocation_zip_code_prefix` | customers/sellers ↔ geolocation | Localisation |

## 3. Anomalies détectées

### 3.1 Customers : deux identifiants
- `customer_id` : 99 441 (change à chaque commande = ticket de caisse)
- `customer_unique_id` : 96 096 (identité réelle = carte de fidélité)
- **Ratio** : 1,03 commande/client
- **122 clients** apparaissent avec plusieurs villes

### 3.2 Order_items : 1,14 article/commande
- **98 666 commandes** ont au moins un article
- Maximum : **21 articles**
- **88 863 commandes (90,06%)** n'ont qu'un seul article

### 3.3 Order_reviews : 547 commandes avec plusieurs avis
- 98 673 commandes ont au moins un avis
- **768 commandes sans avis**
- 547 commandes avec plusieurs avis (543 en ont 2, 4 en ont 3)

### 3.4 Order_payments : 2 961 commandes avec plusieurs paiements
- Moyenne : 1,04 paiements/commande

### 3.5 Geolocation : 52,6 doublons par zip code
- 1 000 163 lignes / 19 015 zip codes uniques
- **Solution** : agréger par zip_code (moyenne lat/lng)

### 3.6 Statuts de commande

| Statut | Nb | % |
|--------|-----|-----|
| delivered | 96 478 | 97,02% |
| shipped | 1 107 | 1,11% |
| canceled | 625 | 0,63% |
| unavailable | 609 | 0,61% |
| invoiced | 314 | 0,32% |
| processing | 301 | 0,30% |
| created | 5 | 0,01% |
| approved | 2 | 0,00% |

### 3.7 Dates manquantes

| Colonne | % manquant | Nb exact |
|---------|-----------|----------|
| order_purchase_timestamp | 0,00% | 0 |
| order_approved_at | 0,16% | 160 |
| order_delivered_carrier_date | 1,79% | 1 783 |
| order_delivered_customer_date | **2,98%** | **2 965** |
| order_estimated_delivery_date | 0,00% | 0 |

**Cas étrange** : 8 commandes `delivered` sans date de livraison.

### 3.8 Commandes sans article
- **775 commandes** n'ont aucun article
- Répartition : 603 unavailable, 164 canceled, 5 created, 2 invoiced, 1 shipped

### 3.9 Commandes sans avis
- 768 commandes sur 99 441 n'ont pas d'avis

### 3.10 Chiffre d'affaires par statut

| Statut | Lignes d'articles | CA (R$) | Part |
|--------|-------------------|---------|------|
| delivered | 110 197 | 13 221 498,11 | 97,3% |
| shipped | 1 185 | 150 727,44 | 1,1% |
| canceled | 542 | 95 235,27 | 0,7% |
| invoiced | 359 | 61 526,37 | 0,5% |
| processing | 357 | 60 439,22 | 0,4% |
| unavailable | 7 | 2 007,69 | 0,01% |
| approved | 3 | 209,60 | 0,00% |
| **Total** | **112 650** | **13 591 643,70** | **100%** |

**CA de référence** (hors `canceled` et `unavailable`) : **13 494 400,74 R$**

## 4. Décisions de conception retenues (13 décisions)

| # | Constat | Décision | Pourquoi |
|---|---------|----------|----------|
| 1 | `customer_id` change à chaque commande | Utiliser `customer_unique_id` dans DimClient | Compter les vraies personnes |
| 2 | 1 commande = plusieurs articles | Grain = 1 ligne par article | Prix/produit/vendeur au niveau article |
| 3 | Plusieurs avis par commande | Garder l'avis le plus récent | 1 commande = 1 note |
| 4 | Plusieurs paiements par commande | Ne pas éclater dans la table de faits | Éviter doublons |
| 5 | 52 doublons géo par zip | Agréger par zip_code | 1 ligne par code postal |
| 6 | Dates au format texte | Convertir en datetime | Calculer les délais |
| 7 | 97% livrées, 0,7% CA annulé | Garder tout, exclure canceled/unavailable du CA | Ne pas compter les ventes non réalisées |
| 8 | 2 965 commandes sans date livraison | Délais = NULL | Ne pas inventer |
| 9 | 8 commandes livrées sans date | Exclure du calcul des délais | Impossible de calculer |
| 10 | Catégories en portugais | Joindre avec traduction | Libellés lisibles |
| 11 | 122 clients multi-villes | Garder la ville la plus récente | 1 ligne par client |
| 12 | 775 commandes sans article | Hors table de faits | Sans prix, pas de vente |
| 13 | 768 commandes sans avis | LEFT JOIN, note NULL | Ne pas perdre ces commandes |

## 5. Schéma des relations

(Image `docs/schema_relations.png`)

## 6. Chiffres de contrôle

| Après cette opération... | ...resultat attendu |
|--------------------------|---------------------|
| Dimension clients | **96 096**          |
| Géolocalisation agrégée | **19 015**          |
| Dimension vendeurs | **3 095**           |
| Dimension produits | **32 951**          |
| Traduction catégories | **71**              |
| Commandes livrées | **96 478**          |
| Total commandes | **99 441**          |
| Commandes avec article | **98 666**          |
| Commandes livrées avec date | **96 470**          |
| Table de faits | **112 650**         |
| Avis dédoublonnés | **98 673**          |
| CA brut | **13 591 643,70**   |
| CA de référence | **13 494 400,74**   |

## 7. Ordre logique du nettoyage

1. Convertir les dates en datetime
2. Calculer les délais (NULL si date manquante)
3. Dédoublonner les avis (garder le plus récent)
4. Résumer les paiements au niveau commande
5. Agréger la géolocalisation par zip_code
6. Traduire les catégories en anglais
7. Construire DimClient sur `customer_unique_id`
8. Assembler la table de faits (112 650 lignes)

## 8. À retenir en une page

1. 9 fichiers reliés par 5 clés : `order_id`, `customer_id`, `product_id`, `seller_id`, `zip_code`
2. `orders` est le cœur : tout se rattache à une commande
3. `customer_id` = ticket, `customer_unique_id` = carte fidélité → utiliser le 2nd
4. Une commande peut avoir plusieurs articles → grain = article
5. Avis et paiements multiples = pièges à doublons
6. Géolocalisation ultra-répétitive → agréger
7. 97% des commandes livrées → délais fiables
8. Une date manquante reste NULL, jamais 0
9. Dates = texte au départ → convertir en datetime
10. Compter les lignes après chaque jointure
11. CA de référence = **13 494 400,74** (hors canceled/unavailable)
12. Table de faits = **98 666** commandes, **112 650** lignes