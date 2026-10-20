# Projet IKEA — Collecte et exploitation avec CouchDB

## Présentation

Ce projet extrait des informations sur des produits IKEA à partir de pages HTML, conserve les données brutes en CSV, puis les nettoie et les transforme en documents JSON.

Le fichier `donnees.json` contient 2 880 produits. Il permet de recréer la base CouchDB sans refaire l’extraction du site.

## 1. Prérequis

- Python 3 installé.
- Git installé pour cloner le dépôt.
- Apache CouchDB installé et démarré.
- Un compte CouchDB autorisé à créer une base et à importer des documents.

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

## 6. Vérifier l’importation

Dans Fauxton :

1. Ouvrir `ikea_produits`.
2. Vérifier la présence des produits.
3. Ouvrir un document dont l’identifiant commence par `ikea_`.
4. Vérifier que les accents sont conservés.
5. Vérifier que les prix sont numériques, sans guillemets.
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

## 7. Créer les index Mango

Dans Fauxton, ouvrir la base et accéder à la création d’un index Mango, généralement depuis **Run a Query with Mango**, puis **Manage Indexes** ou **Index Manager**.

Créer séparément les deux index suivants.

### Index sur la catégorie et le prix

```json
{
  "index": {
    "fields": ["categorie", "prix"]
  },
  "name": "idx_categorie_prix",
  "type": "json"
}
```

### Index sur le prix

```json
{
  "index": {
    "fields": ["prix"]
  },
  "name": "idx_prix",
  "type": "json"
}
```

Ces définitions correspondent aux corps des requêtes de création d’index :

```text
POST /ikea_produits/_index
```

## 8. Exécuter les requêtes Mango

Dans Fauxton, ouvrir `ikea_produits`, puis **Run a Query with Mango**. Coller chaque requête séparément et cliquer sur **Run Query**.

### Requête 1 — Filtre multicritère avec projection

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

### Requête 2 — Tri avec limite

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

## 9. Créer la vue MapReduce

Dans Fauxton, ouvrir la base `ikea_produits`, puis utiliser l’option de création d’une vue.

Configurer :

- **Document de conception :** `_design/analyses`
- **Nom de la vue :** `par_categorie`

Si l’interface ajoute automatiquement `_design/`, saisir uniquement `analyses`.

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

### Consulter les résultats

Dans les options de la vue :

1. Activer **Reduce**.
2. Régler **Group Level** sur **Exact**.
3. Exécuter ou actualiser la vue.

La requête HTTP équivalente est :

```text
GET /ikea_produits/_design/analyses/_view/par_categorie?group=true
```

Chaque catégorie contient les statistiques suivantes :

- `sum` : somme des prix;
- `count` : nombre de produits pris en compte;
- `min` : prix minimum;
- `max` : prix maximum;
- `sumsqr` : somme des carrés des prix.

Les produits sans prix numérique sont exclus.

Pour la catégorie « Abat-jour décoratifs pour lampes », les résultats observés étaient :

```json
{
  "key": "Abat-jour décoratifs pour lampes",
  "value": {
    "sum": 157.84,
    "count": 16,
    "min": 6.99,
    "max": 14.99,
    "sumsqr": 1668.8416000000002
  }
}
```

## 10. Refaire la transformation depuis les CSV

Cette étape est facultative pour recréer la base, puisque `donnees.json` est fourni.

Pour reconstruire le JSON à partir des CSV bruts :

```powershell
python nettoyer_donnees.py
```

Le script lit :

- `produits_bruts_681.csv`;
- `produits_bruts_nouveaux.csv`.

Il réécrit `donnees.json`, sans modifier les CSV bruts.

## 11. Code d’extraction

Le script `extraire_produits.py` utilise `requests` et `BeautifulSoup` pour analyser les blocs JSON-LD de type `Product` présents dans les pages HTML IKEA.

Dans sa version actuelle, il lit `liens_nouveaux.csv`, traite au maximum 2 200 liens et écrit dans `produits_bruts_nouveaux.csv`.

Il attend trois secondes entre les requêtes et s’arrête en cas de réponse HTTP 401, 403 ou 429.

L’extraction n’est pas nécessaire pour reproduire les résultats à partir du JSON fourni. Le script refuse d’écraser son CSV de sortie s’il existe déjà.

## 12. Équipe

- Audrey Laeticia Djoum Kom
- Anne Joelle Allou

## 13. Utilisation de l’IA

ChatGPT a été utilisé pour aider à réviser la documentation, examiner les scripts et repérer des incohérences dans les résultats.

Les vérifications et les résultats sont décrits dans `rapport.md`.
