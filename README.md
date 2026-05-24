# 🚀 Job Intelligent

**Plateforme intelligente de recommandation d'offres d'emploi dans le domaine de la Data**

Une solution end-to-end qui collecte automatiquement des offres d'emploi depuis plusieurs sources, les traite via un pipeline ETL orchestré, et recommande les meilleures offres à un candidat en fonction de son CV.

---

## 📋 Table des matières

- [Objectif du projet](#-objectif-du-projet)
- [Architecture globale](#-architecture-globale)
- [Technologies utilisées](#-technologies-utilisées)
- [Structure du projet](#-structure-du-projet)
- [Sources de données](#-sources-de-données)
- [Pipeline ETL détaillé](#-pipeline-etl-détaillé)
- [Orchestration avec Airflow](#-orchestration-avec-airflow)
- [Modélisation Data Warehouse](#-modélisation-data-warehouse)
- [Application Streamlit](#-application-streamlit)
- [Dashboard Power BI](#-dashboard-power-bi)
- [Installation et exécution](#-installation-et-exécution)
- [Aperçu des résultats](#-aperçu-des-résultats)

---

## 🎯 Objectif du projet

Concevoir et implémenter une plateforme complète de Data Engineering qui :

1. **Collecte** des offres d'emploi depuis 3 APIs différentes (France Travail, JSearch, LinkedIn/Indeed)
2. **Normalise** les données dans un schéma unifié
3. **Nettoie et déduplique** les offres
4. **Extrait les compétences** techniques requises dans chaque offre
5. **Calcule un score de matching** entre le profil d'un candidat et les offres
6. **Stocke** les résultats dans le cloud (Azure Blob Storage + PostgreSQL)
7. **Visualise** les recommandations via une application Streamlit et un dashboard Power BI

---

## 🏗️ Architecture globale

```
┌─────────────────────────────────────────────────────────────────────┐
│                        SOURCES DE DONNÉES                           │
├──────────────────┬──────────────────┬───────────────────────────────┤
│  France Travail  │  JSearch API     │  LinkedIn/Indeed (RapidAPI)   │
│  (OAuth2 API)    │  (RapidAPI)      │  (RapidAPI)                   │
└────────┬─────────┴────────┬─────────┴──────────────┬────────────────┘
         │                  │                        │
         ▼                  ▼                        ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     COLLECTE (Python Scripts)                        │
│  collect_france_travail.py | collect_jsearch.py | collect_linkedin.py│
└─────────────────────────────────┬───────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   NORMALISATION + NETTOYAGE                          │
│  normalize_*.py → Schéma unifié (job_id, title, company, etc.)      │
│  clean_france_travail.py → Standardisation texte/dates/expérience   │
└─────────────────────────────────┬───────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    FUSION + DÉDUPLICATION                            │
│  merge_all_sources.py → Combinaison des 3 sources                   │
│  deduplicate_jobs.py → Suppression des doublons par job_id          │
└─────────────────────────────────┬───────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  EXTRACTION DE COMPÉTENCES                           │
│  extract_skills_all.py → Détection de 22 skills techniques          │
│  (python, sql, spark, azure, power bi, docker, etc.)                │
└─────────────────────────────────┬───────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       MATCHING (Scoring)                             │
│  match_jobs.py → Score = (skills matchées / skills profil) × 100    │
└─────────────────────────────────┬───────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      STOCKAGE CLOUD (Azure)                         │
├─────────────────────────────┬───────────────────────────────────────┤
│  Azure Blob Storage         │  Azure PostgreSQL                     │
│  (fichiers CSV/JSON)        │  (Schéma en étoile)                   │
└─────────────────────────────┴──────────────┬────────────────────────┘
                                             │
                                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        VISUALISATION                                 │
├─────────────────────────────────┬───────────────────────────────────┤
│  Streamlit (app.py)             │  Power BI (dashboard .pbix)       │
│  Upload CV → Recommandations    │  Analyses business                │
└─────────────────────────────────┴───────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    ORCHESTRATION (Apache Airflow)                    │
│  DAGs automatisés → Exécution quotidienne du pipeline complet       │
│  Docker Compose (Scheduler, Worker, Redis, PostgreSQL, Flower)      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Technologies utilisées

| Couche | Technologie |
|--------|-------------|
| **Langage** | Python 3.x |
| **Collecte de données** | Requests, APIs REST, OAuth2 |
| **Traitement** | Pandas, BeautifulSoup |
| **Orchestration** | Apache Airflow 3.1.7 (CeleryExecutor) |
| **Stockage fichiers** | Azure Blob Storage |
| **Base de données** | Azure PostgreSQL (schéma en étoile) |
| **Application web** | Streamlit |
| **Dashboard BI** | Power BI |
| **Conteneurisation** | Docker, Docker Compose |
| **Message Broker** | Redis |
| **Extraction CV** | pdfplumber, python-docx |

---

## 📁 Structure du projet

```
job_intelligent/
│
├── airflow/                          # Configuration Airflow
│   ├── dags/                         # DAGs du pipeline
│   │   ├── job_intelligent_dag.py    # Pipeline v1 (linéaire)
│   │   └── job_intelligent_pipeline_v2.py  # Pipeline v2 (avec validation)
│   ├── config/                       # Configuration Airflow
│   ├── logs/                         # Logs d'exécution
│   ├── plugins/                      # Plugins custom
│   ├── docker-compose.yaml           # Cluster Airflow complet
│   └── .env                          # Variables Airflow
│
├── src/
│   └── collectors/                   # Scripts de collecte et traitement
│       ├── collect_france_travail.py # Collecte API France Travail
│       ├── collect_jsearch_rapidapi.py  # Collecte API JSearch
│       ├── collect_linkedin_rapidapi.py # Collecte API LinkedIn/Indeed
│       ├── normalize_france_travail.py  # Normalisation France Travail
│       ├── normalize_jsearch.py      # Normalisation JSearch
│       ├── normalize_linkedin.py     # Normalisation LinkedIn
│       ├── clean_france_travail.py   # Nettoyage avancé
│       ├── merge_france_travail.py   # Fusion des fichiers
│       ├── export_france_travail_csv.py # Export JSON → CSV
│       ├── extract_skills_france_travail.py # Extraction compétences
│       ├── matching_france_travail.py # Calcul du matching
│       ├── quality_check_france_travail.py # Contrôle qualité
│       └── get_token.py              # Authentification OAuth2
│
├── data/
│   ├── raw/                          # Données brutes (JSON)
│   │   ├── france_travail/
│   │   ├── jsearch/
│   │   └── linkedin/
│   ├── processed/                    # Données nettoyées (JSON + CSV)
│   └── final/                        # Données finales prêtes au chargement
│       ├── all_jobs_merged.csv
│       ├── all_jobs_deduplicated.csv
│       ├── all_jobs_skills.csv
│       └── all_jobs_matched.csv
│
├── Dashboard/
│   └── dashboard_JobIntelligent.pbix # Dashboard Power BI
│
├── app.py                            # Application Streamlit
├── requirements.txt                  # Dépendances Python
├── .env                              # Variables d'environnement
├── .gitignore
└── README.md
```

---

## 📥 Sources de données

### 1. France Travail (Pôle Emploi) — API officielle

- **Authentification** : OAuth2 (client_credentials)
- **Endpoint** : `https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search`
- **Mots-clés recherchés** : "data analyst", "data engineer", "BI analyst", "data scientist"
- **Pagination** : Header `Range` (par blocs de 20 offres)

### 2. JSearch — RapidAPI

- **Endpoint** : `https://jsearch.p.rapidapi.com/search`
- **Requêtes** : "data analyst in Paris", "data engineer in Paris", "python data in France", "power bi in France", etc.
- **Pagination** : Par pages (jusqu'à 5 pages par requête)
- **Pays** : France

### 3. LinkedIn / Indeed — RapidAPI

- **Endpoint** : `https://indeed12.p.rapidapi.com/jobs/search`
- **Mots-clés** : "data", "data analyst", "business analyst", "bi analyst", "data engineer"
- **Pagination** : Via `next_page_id` (jusqu'à 20 pages)
- **Localisation** : France

---

## 🔄 Pipeline ETL détaillé

### Étape 1 — Collecte

Les scripts appellent les APIs et sauvegardent les réponses JSON brutes :

```python
# Exemple : collecte France Travail
token = get_access_token()  # OAuth2
jobs_data = search_jobs(token, keyword="data analyst", start=0, end=19)
save_raw_data(jobs_data, keyword)  # → data/raw/france_travail/
```

### Étape 2 — Normalisation

Chaque source est transformée en un **schéma unifié** :

| Champ | Description |
|-------|-------------|
| `job_id` | Identifiant unique de l'offre |
| `title` | Intitulé du poste |
| `company` | Nom de l'entreprise |
| `location` | Localisation complète |
| `city` | Ville |
| `region` | Région |
| `contract_type` | CDI, CDD, Stage, Alternance, Freelance |
| `experience_level` | Junior, Confirmé, Senior, Stage/Alternance |
| `publication_date` | Date de publication |
| `description` | Description complète de l'offre |
| `source_url` | Lien vers l'offre originale |
| `source` | France Travail / JSearch / LinkedIn |

### Étape 3 — Nettoyage

- Suppression des espaces et caractères parasites
- Standardisation de l'expérience ("1 an" → Junior, "5 ans" → Senior)
- Extraction du code département et de la ville
- Conversion des dates en format datetime
- Remplissage des valeurs manquantes

### Étape 4 — Fusion et déduplication

- Combinaison des 3 sources en un seul dataset
- Suppression des doublons par `job_id`

### Étape 5 — Extraction de compétences

Détection de **22 compétences techniques** dans les descriptions :

```python
SKILLS = [
    "python", "sql", "power bi", "excel", "azure", "aws", "spark",
    "tableau", "machine learning", "dataiku", "git", "hadoop", "sas",
    "vba", "java", "scala", "pandas", "numpy", "etl", "airflow",
    "docker", "kubernetes"
]
```

Résultat : une colonne binaire (0/1) par compétence + une colonne `skills_detected`.

### Étape 6 — Matching

Calcul du score de correspondance :

```python
score = (nombre de skills matchées / nombre de skills du profil) × 100
```

Exemple : si le profil contient [python, sql, azure, power bi] et l'offre requiert [python, sql] → score = 50%

### Étape 7 — Chargement cloud

- **Azure Blob Storage** : Upload des fichiers CSV finaux
- **Azure PostgreSQL** : Chargement dans un schéma en étoile

---

## ⚙️ Orchestration avec Airflow

### DAG v1 : `job_intelligent_pipeline`

Pipeline linéaire simple :

```
merge → deduplicate → extract_skills → match → upload_to_blob → load_to_azure_sql
```

### DAG v2 : `job_intelligent_pipeline_v2_postgres_star_schema`

Pipeline avec validation parallèle des sources :

```
[check_france_travail_data]  ─┐
[check_jsearch_data]          ├──→ merge → dedup → skills → match → upload → load_postgresql
[check_linkedin_data]        ─┘
```

- **Vérification** : S'assure que les 3 fichiers CSV sources existent avant de lancer le merge
- **Scheduling** : Exécution quotidienne (`@daily`)
- **Infrastructure** : Docker Compose avec Scheduler, Worker, Triggerer, API Server, DAG Processor, Flower (monitoring), Redis, PostgreSQL

---

## ⭐ Modélisation Data Warehouse

### Schéma en étoile (Star Schema)

```
                    ┌──────────────┐
                    │  dim_skill   │
                    │──────────────│
                    │ skill_id     │
                    │ skill_name   │
                    └──────┬───────┘
                           │
┌──────────────┐    ┌──────┴───────────────┐    ┌──────────────┐
│  dim_company │    │  fact_job_matching    │    │  dim_source  │
│──────────────│    │──────────────────────│    │──────────────│
│ company_id   │    │ job_key              │    │ source_id    │
│ company_name │    │ skill_id             │    │ source_name  │
└──────┬───────┘    │ match_score          │    └──────┬───────┘
       │            └──────────────────────┘           │
       │                                               │
       │            ┌──────────────────────┐           │
       └────────────┤   fact_job_offer     ├───────────┘
                    │──────────────────────│
                    │ job_key              │
                    │ company_id           │
                    │ location_id          │
                    │ source_id            │
                    └──────┬───────────────┘
                           │
                    ┌──────┴───────┐    ┌──────────────┐
                    │  dim_job     │    │ dim_location │
                    │──────────────│    │──────────────│
                    │ job_key      │    │ location_id  │
                    │ job_uid      │    │ location_name│
                    │ title        │    │ city         │
                    └──────────────┘    │ region       │
                                        └──────────────┘
```

---

## 🖥️ Application Streamlit

L'application (`app.py`) offre une interface interactive :

1. **Upload du CV** : Supporte PDF, DOCX et TXT
2. **Extraction automatique des compétences** depuis le texte du CV
3. **Requête PostgreSQL** : Récupère toutes les offres avec leurs compétences
4. **Calcul du score de matching** en temps réel
5. **Affichage des recommandations** triées par pertinence

### Fonctionnalités :
- 🎚️ Filtres : score minimum, nombre d'offres à afficher
- 📊 Métriques : nombre de compétences CV, offres recommandées, meilleur score
- 🏷️ Badges visuels pour les compétences détectées et matchées
- 🎨 Interface moderne avec cards et code couleur (vert/orange/rouge selon le score)

---

## 📊 Dashboard Power BI

Le fichier `dashboard_JobIntelligent.pbix` se connecte à la base PostgreSQL et fournit :
- Répartition des offres par source
- Distribution des compétences les plus demandées
- Analyse géographique des offres
- Évolution temporelle des publications
- Statistiques de matching

---

## 🚀 Installation et exécution

### Prérequis

- Python 3.9+
- Docker & Docker Compose
- Compte Azure (Blob Storage + PostgreSQL)
- Clés API (France Travail, RapidAPI)

### 1. Cloner le projet

```bash
git clone https://github.com/votre-username/job_intelligent.git
cd job_intelligent
```

### 2. Configurer les variables d'environnement

Créer un fichier `.env` à la racine :

```env
# France Travail API
FRANCE_TRAVAIL_CLIENT_ID=votre_client_id
FRANCE_TRAVAIL_CLIENT_SECRET=votre_client_secret

# RapidAPI
RAPIDAPI_KEY=votre_rapidapi_key

# Azure Blob Storage
AZURE_STORAGE_CONNECTION_STRING=votre_connection_string
AZURE_STORAGE_CONTAINER=jobdata

# Azure PostgreSQL
POSTGRES_HOST=votre_host.postgres.database.azure.com
POSTGRES_DB=job_intelligent_db
POSTGRES_USER=votre_user
POSTGRES_PASSWORD=votre_password
POSTGRES_PORT=5432
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Lancer la collecte

```bash
python src/collectors/collect_france_travail.py
python src/collectors/collect_jsearch_rapidapi.py
python src/collectors/collect_linkedin_rapidapi.py
```

### 5. Exécuter le pipeline de traitement

```bash
python src/collectors/normalize_france_travail.py
python src/collectors/normalize_jsearch.py
python src/collectors/normalize_linkedin.py
python src/collectors/clean_france_travail.py
python src/collectors/merge_france_travail.py
python src/collectors/extract_skills_france_travail.py
python src/collectors/matching_france_travail.py
```

### 6. Lancer Airflow (optionnel — pour l'orchestration automatique)

```bash
cd airflow
docker-compose up -d
```

Accéder à l'interface Airflow : `http://localhost:8080` (user: airflow / password: airflow)

### 7. Lancer l'application Streamlit

```bash
streamlit run app.py
```

---

## 📸 Aperçu des résultats

### Données collectées

| Source | Offres collectées |
|--------|-------------------|
| France Travail | ~200+ offres |
| JSearch | ~150+ offres |
| LinkedIn/Indeed | ~100+ offres |
| **Total (après déduplication)** | **~400+ offres uniques** |

### Compétences les plus demandées

| Compétence | Fréquence |
|------------|-----------|
| SQL | ⬛⬛⬛⬛⬛⬛⬛⬛⬛ |
| Python | ⬛⬛⬛⬛⬛⬛⬛⬛ |
| Excel | ⬛⬛⬛⬛⬛⬛⬛ |
| Power BI | ⬛⬛⬛⬛⬛⬛ |
| Azure | ⬛⬛⬛⬛⬛ |
| Spark | ⬛⬛⬛⬛ |
| ETL | ⬛⬛⬛ |

---

## 📚 Compétences développées

- ✅ Conception d'un pipeline Data Engineering end-to-end
- ✅ Intégration d'APIs REST avec authentification OAuth2
- ✅ Orchestration de workflows avec Apache Airflow
- ✅ Modélisation dimensionnelle (schéma en étoile)
- ✅ Déploiement cloud sur Azure (Blob Storage + PostgreSQL)
- ✅ Développement d'une application interactive avec Streamlit
- ✅ Création de dashboards avec Power BI
- ✅ Conteneurisation avec Docker Compose
- ✅ Nettoyage et qualité des données

---

## 👤 Auteur

Projet réalisé dans le cadre de la formation **TDIA2** (Traitement de Données et Intelligence Artificielle).

---

## 📄 Licence

Ce projet est à usage éducatif.
