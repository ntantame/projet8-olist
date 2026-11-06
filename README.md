# Projet 8 — Pipeline ETL & BI : ventes e-commerce (Olist)

**Master 2 Data Science — Développement Web en Python**
**Durée** : 3 semaines — **Groupe de 3**

---

##  Équipe et répartition

| Membre | Rôle | Branche de travail |
|--------|------|--------------------|
| @ntantame | Modèles Django + DimTemps + FaitArticleCommande + Industrialisation + Agent IA | `feature/dim-temps-faits/ntantame` |
| @fouelarissa | DimClient + DimVendeur | `feature/dim-client-vendeur/fouelarissa` |
| @kendricdonald | DimProduit + DimRegion | `feature/dim-produit-region/kendricdonald` |

---

##  Règles du groupe

- **Une tâche = une branche = une Pull Request** relue par un autre membre.
- **Chacun committe régulièrement** sous son propre compte.
- **Point de synchronisation** tous les 2 jours (15 min).
- **Une part modeste mais maîtrisée** vaut mieux qu'une grosse part non comprise.

---

##  Workflow Git

### Règles strictes
-  **JAMAIS de push direct sur `main`** (branche protégée).
-  Toute contribution passe par une **branche `feature/...`**.
-  **1 approbation** obligatoire avant merge dans `main`.
-  **Toutes les conversations** doivent être résolues avant merge.

### Cycle de travail
```bash
# 1. Récupérer les dernières modifications
git fetch origin

# 2. Passer sur sa branche
git checkout feature/ma-branche

# 3. Travailler, puis commiter
git add .
git commit -m "feat: description de la modification"

# 4. Pousser sur sa branche
git push origin feature/ma-branche

# 5. Ouvrir une Pull Request sur GitHub
# → Un autre membre approuve
# → Merge dans main
```

---

##  Architecture du projet

Notre solution suit la chaîne classique d'un projet de Business Intelligence :
1. **Pipeline ETL** : Nettoyage et chargement des CSV Olist vers PostgreSQL.
2. **Data Warehouse** : Modélisation en étoile (1 table de faits, 5 dimensions).
3. **API Backend** : Django REST Framework (endpoints d'agrégation sécurisés par Token).
4. **Intelligence Artificielle** : Agent conversationnel (LangChain + Groq).
5. **Frontend** : Tableau de bord interactif (HTML/JS/Chart.js) et interface de chat.
6. **DevOps** : Conteneurisation complète avec Docker et Docker Compose.

---

##  Conception du Data Warehouse (Modèle en étoile)

Avant de coder, nous avons analysé les fichiers bruts (exploration) pour identifier les anomalies (doublons, dates manquantes, identifiants multiples). Cela nous a conduit à concevoir un schéma en étoile pour optimiser les requêtes d'agrégation.

### Décisions de conception majeures :
*   **Grain de la table de faits** : Nous avons choisi de définir une ligne par **article commandé** (`FaitArticleCommande`). Cela permet de conserver le détail du produit et du vendeur, contrairement à un grain par commande.
*   **Double rôle pour la région** : La table `DimRegion` est reliée deux fois à la table de faits : `region_client` (destination) et `region_vendeur` (origine).
*   **Gestion des doublons** : Nous avons identifié le `customer_unique_id` (et non le `customer_id` qui change à chaque commande) pour compter les vrais clients. Les avis multiples ont été dédoublonnés pour ne garder que le plus récent.
*   **Règle métier** : Le chiffre d'affaires exclut toujours les commandes avec le statut `canceled` et `unavailable`.

### Schéma du Data Warehouse :

![Schéma du Data Warehouse](https://github.com/user-attachments/assets/5d3770b5-864b-4eb7-a8bc-6c60728e3ae5)

---

##  Architecture de l'Agent Conversationnel

L'agent ne se contente pas de générer du texte : il utilise une architecture **ReAct (Reasoning and Acting)** pour interroger la base de données de manière sécurisée.

*Ci-dessous, le schéma du flux d'une requête vers l'agent :*

![Architecture de l'agent](https://github.com/user-attachments/assets/e560923b-d0fc-4943-8496-e05af77bac02)

**Explication du flux :**
1. L'utilisateur pose une question sur l'interface de chat.
2. L'API Django (`/api/agent/ask/`) reçoit la requête et initialise le LLM (Groq).
3. L'agent analyse la question (Thought) et choisit le bon outil Python (`@tool`).
4. L'outil exécute une requête SQL via l'ORM Django sur PostgreSQL.
5. Le résultat est renvoyé au LLM (Observation) qui formule une réponse en langage naturel.
6. L'API renvoie la réponse formatée à l'interface.

---

##  Fonctionnalités clés

- **Dashboard interactif** : 5 KPIs (CA, commandes, délai, retard, note), 4 graphiques interactifs (Chart.js), filtres globaux (date, région, catégorie, ville).
- **Agent Conversationnel** : 
  - Répond aux questions en langage naturel sur les données.
  - Filtre les résultats par région, ville, année et catégorie.
  - **Détection d'anomalies** : Identifie les pics de retard et propose des hypothèses causales.
- **API REST** : Documentation interactive avec Swagger, authentification par Token.

---

##  Installation et Lancement

### Option 1 : Lancement avec Docker (Recommandé)
1. Cloner le projet :
   ```bash
   git clone https://github.com/ntantame/projet8-olist.git
   cd projet8-olist
   ```
2. Créer un fichier `.env` à la racine avec la clé API Groq :
   ```env
   GROQ_API_KEY=votre_cle_gsk_ici
   ```
3. Lancer les conteneurs :
   ```bash
   docker compose up --build -d
   ```
4. Appliquer les migrations et lancer l'ETL :
   ```bash
   docker compose exec web python manage.py migrate
   docker compose exec web python manage.py run_etl
   ```
5. Créer un superutilisateur (pour l'admin et le Token) :
   ```bash
   docker compose exec web python manage.py createsuperuser
   ```
6. L'application est accessible sur `http://localhost:8000/dashboard/`.

### Option 2 : Lancement en local (sans Docker)
Si vous souhaitez lancer l'application directement sur votre machine, suivez ces étapes :

1. Créer un environnement virtuel et l'activer :
   ```bash
   python -m venv .venv
   # Sous Windows :
   .venv\Scripts\activate
   # Sous Mac/Linux :
   source .venv/bin/activate
   ```
2. Installer les dépendances :
   ```bash
   pip install -r requirements.txt
   ```
3. Créer la base de données PostgreSQL en local et configurer les accès dans `config/settings.py`.
4. Créer le fichier `.env` avec la clé Groq.
5. Appliquer les migrations et lancer l'ETL :
   ```bash
   python manage.py migrate
   python manage.py run_etl
   ```
6. Créer un superutilisateur :
   ```bash
   python manage.py createsuperuser
   ```
7. Lancer le serveur Django :
   ```bash
   python manage.py runserver
   ```
8. L'application est accessible sur `http://localhost:8000/dashboard/`.
