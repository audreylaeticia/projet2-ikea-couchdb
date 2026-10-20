# Projet IKEA — Collecte et exploitation avec CouchDB

## Présentation

Ce projet extrait des informations sur des produits IKEA à partir de pages HTML, conserve les données brutes en CSV, puis les nettoie et les transforme en documents JSON.

Le fichier `donnees.json` contient 2 880 produits. Il permet de recréer la base CouchDB sans refaire l’extraction du site.

## 1. Prérequis

- Python 3 installé.
- Git installé pour cloner le dépôt.
- Apache CouchDB installé et démarré.
- Un compte CouchDB autorisé à créer une base, importer des documents et créer des index et des vues.

Fauxton est accessible à cette adresse :

http://127.0.0.1:5984/_utils/

## 2. Récupérer le projet

```powershell
git clone https://github.com/audreylaeticia/projet2-ikea-couchdb.git
cd projet2-ikea-couchdb
```

Si le dépôt est déjà présent, ouvrir son dossier dans le terminal et récupérer les changements :

```powershell
git pull
```

Si le projet provient du ZIP de remise, extraire le ZIP et ouvrir un terminal dans le dossier contenant les scripts et `donnees.json`.

## 3. Installer les dépendances

Depuis le dossier du projet :

```powershell
python -m pip install requests beautifulsoup4
```

## 4. Créer la base CouchDB

1. Ouvrir http://127.0.0.1:5984/_utils/
2. Se connecter à CouchDB.
3. Cliquer sur **Create Database**.
4. Nommer la base `ikea_produits`.
5. Choisir une base non partitionnée si cette option est proposée.
6. Valider la création.

Le script d’importation utilise une base existante : il ne la crée pas automatiquement.

Si la base contient déjà les produits, passer directement aux vérifications et aux requêtes.

## 5. Importer les données JSON

Depuis le dossier contenant `donnees.json` et `importer_couchdb.py` :

```powershell
python importer_couchdb.py
```

Saisir le nom d’utilisateur et le mot de passe CouchDB lorsque le script les demande. Le mot de passe ne s’affiche pas pendant la saisie.

Le script :

- lit `donnees.json`;
- vérifie l’accès à `ikea_produits`;
- envoie les documents par lots de 500 avec `_bulk_docs`;
- vérifie les réponses individuelles;
- affiche le nombre de documents ajoutés et les erreurs.

Pour une base vide et une importation réussie, le résultat attendu est :

```text
Documents ajoutés : 2880
Erreurs : 0
```

Ne pas relancer l’importation sur les mêmes documents : des erreurs de conflit peuvent apparaître lorsque leurs identifiants existent déjà.

Aucun mot de passe ou jeton d’accès ne doit être enregistré dans les fichiers du projet.

## 6. Vérifier l’importation

Dans Fauxton :

1. Ouvrir `ikea_produits`.
2. Vérifier la présence des produits.
3. Ouvrir un document dont l’identifiant commence par `ikea_`.
4. Vérifier que les accents sont conservés.
5. Vérifier que les prix connus sont numériques, sans guillemets.
6. Vérifier que les informations inconnues sont représentées par `null`.

Le nombre total de documents peut dépasser 2 880 après la création des documents techniques des index et des vues.

Pour vérifier le nombre de produits dans le fichier JSON avec PowerShell :

```powershell
$produits = Get-Content -Raw -Encoding UTF8 .\donnees.json | ConvertFrom-Json
$produits.Count
```

Résultat attendu :

```text
2880
```

Pour afficher deux exemples :

```powershell
$produits | Select-Object -First 2 | ConvertTo-Json -Depth 5
```

## 7. Fichiers des requêtes

Le dossier `requetes` contient :

| Fichier | Rôle |
|---|---|
| `requete1.json` | Filtre multicritère avec projection |
| `requete2.json` | Tri croissant avec limite |
| `index_categorie_prix.json` | Définition de l’index sur la catégorie et le prix |
| `index_prix.json` | Définition de l’index sur le prix |
| `vue_par_categorie.json` | Définition du document de conception et de la vue MapReduce |

Les étapes suivantes expliquent comment créer ces index et cette vue, puis exécuter les requêtes.

## 8. Créer les index Mango

Dans Fauxton, ouvrir `ikea_produits`, puis accéder à la création d’un index Mango depuis **Run a Query with Mango**, puis **Manage Indexes** ou **Index Manager**, selon la version.

Créer séparément les deux index ci-dessous. S’ils existent déjà avec les mêmes champs, il n’est pas nécessaire de les recréer.

Les noms correspondent aux noms automatiques des index utilisés dans le projet.

### Index sur la catégorie et le prix

Contenu de `requetes/index_categorie_prix.json` :

```json
{
  "index": {
    "fields": [
      {
        "categorie": "asc"
      },
      {
        "prix": "asc"
      }
    ]
  },
  "name": "2ef3c4fb464663802372bb7ce3a2f8ba1d66d446",
  "type": "json"
}
```

### Index sur le prix

Contenu de `requetes/index_prix.json` :

```json
{
  "index": {
    "fields": [
      {
        "prix": "asc"
      }
    ]
  },
  "name": "d7121ec3cfeef227b4c4ae614343a75645b9712f",
  "type": "json"
}
```

Ces définitions correspondent aux corps des requêtes de création d’index :

```text
POST /ikea_produits/_index
```

## 9. Exécuter les requêtes Mango

Dans Fauxton, ouvrir `ikea_produits`, puis **Run a Query with Mango**.

Coller chaque requête séparément et cliquer sur **Run Query**.

### Requête 1 — Filtre multicritère avec projection

Contenu de `requetes/requete1.json` :

```json
{
  "selector": {
    "categorie": "Câbles, gestion des câbles et accessoires",
    "prix": {
      "$type": "number",
      "$lt": 20
    }
  },
  "fields": ["_id", "nom", "prix", "categorie"],
  "limit": 10
}
```

Cette requête retourne au maximum dix produits de la catégorie demandée dont le prix numérique est inférieur à 20 $.

La projection conserve uniquement l’identifiant, le nom, le prix et la catégorie.

### Requête 2 — Tri ascendant avec limite

Contenu de `requetes/requete2.json` :

```json
{
  "selector": {
    "prix": {
      "$gt": 0
    }
  },
  "sort": [
    {
      "prix": "asc"
    }
  ],
  "limit": 5,
  "fields": ["_id", "nom", "prix"]
}
```

Cette requête retourne au maximum cinq produits dont le prix est strictement positif, du moins cher au plus cher.

Les prix observés lors de la vérification étaient :

```text
0.69
0.79
0.79
0.79
0.99
```

L’ordre entre les produits de même prix n’est pas fixé par un critère secondaire.

## 10. Créer et interroger la vue MapReduce

### Création dans Fauxton

Dans Fauxton, ouvrir `ikea_produits`, puis utiliser l’option de création d’une vue dans **Design Documents**.

Configurer :

- **Document de conception :** `_design/newDesign`
- **Nom de la vue :** `par_categorie`

Si l’interface ajoute automatiquement `_design/`, saisir uniquement `newDesign`.

Si la vue existe déjà, consulter sa définition au lieu de créer une deuxième vue.

### Fonction Map

```javascript
function (doc) {
  if (typeof doc.categorie === "string" &&
      typeof doc.prix === "number") {
    emit(doc.categorie, doc.prix);
  }
}
```

### Fonction Reduce

Sélectionner la fonction intégrée :

```text
_stats
```

Enregistrer la vue.

### Définition JSON complète

Contenu de `requetes/vue_par_categorie.json` :

```json
{
  "_id": "_design/newDesign",
  "views": {
    "par_categorie": {
      "map": "function (doc) { if (typeof doc.categorie === \"string\" && typeof doc.prix === \"number\") { emit(doc.categorie, doc.prix); } }",
      "reduce": "_stats"
    }
  }
}
```

Cette définition peut également être utilisée pour créer un nouveau document de conception avec :

```text
PUT /ikea_produits/_design/newDesign
```

Si le document existe déjà, sa modification nécessite sa révision actuelle `_rev`. L’édition de la vue dans Fauxton permet de gérer cette modification.

### Requête 3 — Regroupement avec calcul

Dans les options de la vue :

1. Activer **Reduce**.
2. Régler **Group Level** sur **Exact**.
3. Exécuter ou actualiser la vue.

La requête HTTP équivalente est :

```text
GET /ikea_produits/_design/newDesign/_view/par_categorie?group=true
```

Chaque catégorie contient les statistiques suivantes :

- `sum` : somme des prix;
- `count` : nombre de produits pris en compte;
- `min` : prix minimum;
- `max` : prix maximum;
- `sumsqr` : somme des carrés des prix.

Les produits sans prix numérique sont exclus.

### Extrait des résultats vérifiés

```json
[
  {
    "key": "Abat-jour décoratifs pour lampes",
    "value": {
      "sum": 157.84,
      "count": 16,
      "min": 6.99,
      "max": 14.99,
      "sumsqr": 1668.8416000000002
    }
  },
  {
    "key": "Accessoires de conservation des aliments et sacs refermables",
    "value": {
      "sum": 2.99,
      "count": 1,
      "min": 2.99,
      "max": 2.99,
      "sumsqr": 8.940100000000001
    }
  }
]
```

De légères différences dans les dernières décimales peuvent apparaître dans les calculs en virgule flottante.

## 11. Refaire la transformation depuis les CSV

Cette étape est facultative pour recréer la base, puisque `donnees.json` est fourni.

Pour reconstruire le JSON à partir des CSV bruts :

```powershell
python nettoyer_donnees.py
```

Le script lit :

- `produits_bruts_681.csv`;
- `produits_bruts_nouveaux.csv`.

Il réécrit `donnees.json`, sans modifier les CSV bruts.

Le bilan observé lors du nettoyage était :

```text
Lignes avant nettoyage : 2880
Doublons retirés : 0
Lignes sans identifiant retirées : 0
Valeurs numériques invalides remplacées par null : 0
Produits après nettoyage : 2880
Fichier créé : donnees.json
```

Les valeurs absentes deviennent `null`, mais ne sont pas comptées parmi les valeurs numériques invalides.

## 12. Code d’extraction

Le script `extraire_produits.py` utilise `requests` et `BeautifulSoup` pour analyser les blocs JSON-LD de type `Product` intégrés aux pages HTML IKEA.

Dans sa version actuelle, il :

- lit les URL dans `liens_nouveaux.csv`;
- traite au maximum 2 200 liens;
- écrit les valeurs extraites dans `produits_bruts_nouveaux.csv`;
- attend trois secondes entre les requêtes;
- s’arrête en cas de réponse HTTP 401, 403 ou 429.

L’extraction n’est pas nécessaire pour reproduire les résultats à partir du JSON fourni.

Le script utilise le mode de création `x` : il refuse d’écraser son CSV de sortie si celui-ci existe déjà.

## 13. Principaux fichiers du projet

| Fichier ou dossier | Description |
|---|---|
| `rapport.md` | Rapport du projet |
| `README.md` | Procédure de reproduction |
| `extraire_produits.py` | Extraction des informations sur les produits |
| `nettoyer_donnees.py` | Nettoyage des CSV et transformation en JSON |
| `importer_couchdb.py` | Importation du JSON dans CouchDB |
| `produits_bruts_681.csv` | Premier fichier brut utilisé par le nettoyage |
| `produits_bruts_nouveaux.csv` | Deuxième fichier brut utilisé par le nettoyage |
| `donnees.json` | Tableau des 2 880 produits nettoyés |
| `requetes/` | Requêtes Mango, index et définition de la vue |

Les autres scripts et CSV de liens du dépôt documentent les étapes de collecte et les essais d’extraction.

## 14. Équipe

- Audrey Laeticia Djoum Kom
- Anne Joelle Allou

## 15. Utilisation de l’intelligence artificielle

ChatGPT a été utilisé pour aider à réviser la documentation, examiner les scripts et repérer des incohérences dans les résultats.

Les vérifications effectuées et les résultats obtenus sont décrits dans `rapport.md`.
