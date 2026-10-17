import csv
import time
import requests

from bs4 import BeautifulSoup
from urllib.parse import urljoin

# 1. Trouver les catégories sur la page générale.
url = "https://www.ikea.com/ca/fr/cat/articles-products/"

reponse = requests.get(url, timeout=30)
reponse.raise_for_status()

soup = BeautifulSoup(reponse.content, "html.parser")

categories = []
produits = []

for lien in soup.find_all("a", href=True):
    adresse = urljoin(url, lien["href"])

    if adresse.startswith("https://www.ikea.com/ca/fr/cat/"):
        if "?" not in adresse:
            adresse = adresse.split("#")[0]

            if adresse not in categories:
                categories.append(adresse)

print("Catégories trouvées :", len(categories))

# Premier essai : visiter au maximum 20 catégories.
categories = categories[20:]

# 2. Visiter chaque catégorie.
for categorie in categories:
    time.sleep(3)
    print("\nLecture :", categorie)

    try:
        reponse = requests.get(categorie, timeout=30)

        if reponse.status_code in (401, 403, 429):
            print("Accès refusé ou limité : arrêt.")
            break

        reponse.raise_for_status()
        soup = BeautifulSoup(reponse.content, "html.parser")

        # 3. Trouver les liens des produits.
        for lien in soup.find_all("a", href=True):
            adresse = urljoin(categorie, lien["href"])

            if adresse.startswith("https://www.ikea.com/ca/fr/p/"):
                if "?" not in adresse:
                    adresse = adresse.split("#")[0]

                    if adresse not in produits:
                        produits.append(adresse)

        print("Total de liens de produits :", len(produits))

    except requests.RequestException as erreur:
        print("Erreur :", erreur)

# 4. Enregistrer dans un nouveau fichier.
with open(
    "liens_categories_restantes.csv",
    "x",
    newline="",
    encoding="utf-8"
) as fichier:
    writer = csv.writer(fichier)
    writer.writerow(["url_source"])

    for adresse in produits:
        writer.writerow([adresse])

print("\nCollecte terminée.")
print("Nombre de liens trouvés :", len(produits))
print("Fichier créé : liens_plusieurs_categories.csv")