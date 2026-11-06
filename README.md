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


 Architecture du projet

Notre solution suit la chaîne classique d'un projet de Business Intelligence :
1. **Pipeline ETL** : Nettoyage et chargement des CSV Olist vers PostgreSQL.
2. **Data Warehouse** : Modélisation en étoile (1 table de faits, 5 dimensions).
3. **API Backend** : Django REST Framework (endpoints d'agrégation sécurisés par Token).
4. **Intelligence Artificielle** : Agent conversationnel (LangChain + Groq).
5. **Frontend** : Tableau de bord interactif (HTML/JS/Chart.js) et interface de chat.
6. **DevOps** : Conteneurisation complète avec Docker et Docker Compose.

## 🤖 Architecture de l'Agent Conversationnel

L'agent ne se contente pas de générer du texte : il utilise une architecture **ReAct (Reasoning and Acting)** pour interroger la base de données de manière sécurisée.

*Ci-dessous, le schéma du flux d'une requête vers l'agent :*
*(Note : Remplace `chemin_vers_ton_image.png` par le vrai chemin de ton image)*
![Schéma de l'architecture de l'agent](chemin_vers_ton_image.png)

**Explication du flux :**
1. L'utilisateur pose une question sur l'interface de chat.
2. L'API Django (`/api/agent/ask/`) reçoit la requête et initialise le LLM (Groq).
3. L'agent analyse la question (Thought) et choisit le bon outil Python (`@tool`).
4. L'outil exécute une requête SQL via l'ORM Django sur PostgreSQL.
5. Le résultat est renvoyé au LLM (Observation) qui formule une réponse en langage naturel.
6. L'API renvoie la réponse formatée à l'interface.

## ⚙️ Installation et Lancement

### Option 1 : Lancement avec Docker (Recommandé)
1. Cloner le projet :
   ```bash
   git clone https://github.com/ntantame/projet8-olist.git
   cd projet8-olist
# 5. Ouvrir une Pull Request sur GitHub
# → Un autre membre approuve
# → Merge dans main
