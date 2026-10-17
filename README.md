## 🚀 Guide de Reproduction (Procédure d'installation)

### 1. Prérequis

* Python 3.x installé.
* Apache CouchDB fonctionnel en local (`http://127.0.0.1:5984/`).

### 2. Cloner le dépôt et installer les dépendances

git clone https://github.com/audreylaeticia/projet2-ikea-couchdb.git

cd projet2-ikea-couchdb

pip install requests beautifulsoup4


### 3. Créer la base et importer les données

Pour recréer la base de données `ikea_produits` à partir du fichier `donnees.json` sans refaire le scraping :

1. Assurez-vous que votre instance CouchDB est démarrée (`http://127.0.0.1:5984/_utils/`).
2. Exécutez le script d'importation :
python scripts/importer_couchdb.py
3. Le script va automatiquement créer la base de données `ikea_produits` et y injecter les 2 880 documents JSON.

## Exécution des Requêtes dans Fauxton

### 1. Création de l'index requis pour le tri

Pour exécuter les requêtes de tri, créez un index JSON sur le champ `prix` dans Fauxton -> **Index Manager** :

{
  "index": {
    "fields": ["prix"]
  },
  "name": "index-prix",
  "type": "json"
}


### 2. Requête Mango 1 : Filtre multicritère et projection

Dans Fauxton -> `ikea_produits` -> **Mango Query** :

{
  "selector": {
    "categorie": "Câbles, gestion des câbles et accessoires",
    "prix": { "$lt": 20 }
  },
  "fields": ["_id", "nom", "prix", "categorie"],
  "limit": 10
}


### 3. Requête Mango 2 : Tri ascendant et limite

Dans Fauxton -> `ikea_produits` -> **Mango Query** :

{
  "selector": {
    "prix": { "$gt": 0 }
  },
  "sort": [{ "prix": "asc" }],
  "limit": 5,
  "fields": ["_id", "nom", "prix"]
}


### 4. Vue MapReduce : Statistiques de prix par catégorie

1. Rendez-vous dans Fauxton -> ikea_produits -> **Design Documents** -> **+ New View**.
2. Nommez le document design newDesign (`_design/analyses`) et l'index `par_categorie`.
3. **Map function :**
function (doc) {
  if (doc.categorie && doc.prix) {
    emit(doc.categorie, doc.prix);
  }
}
4. **Reduce function :** Choisissez `_stats` (fonction intégrée).
5. Dans les options de la vue, cochez **Reduce** et réglez **Group Level** sur `Exact`.


## Équipe

* **Audrey Laeticia Djoum Kom**
* **Anne Joelle Allou**
