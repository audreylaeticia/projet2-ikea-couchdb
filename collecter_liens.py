import csv
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# 1. Télécharger la page d'une catégorie.
url = "https://www.ikea.com/ca/fr/cat/accessoires-decoratifs-24924/"

reponse = requests.get(url, timeout=30)
reponse.raise_for_status()

# 2. Lire le HTML.
soup = BeautifulSoup(reponse.content, "html.parser")

# 3. Préparer une liste pour les liens des produits.
liens_produits = []

# 4. Examiner tous les liens de la page.
for lien in soup.find_all("a", href=True):
    adresse = urljoin(url, lien["href"])

    # Garder les fiches produits françaises sans paramètres.
    if adresse.startswith("https://www.ikea.com/ca/fr/p/"):
        if "?" not in adresse:
            adresse = adresse.split("#")[0]

            # Éviter de garder deux fois le même lien.
            if adresse not in liens_produits:
                liens_produits.append(adresse)

# 5. Enregistrer les liens dans un CSV.
with open("liens_produits.csv", "w", newline="", encoding="utf-8") as fichier:
    writer = csv.writer(fichier)
    writer.writerow(["url_source"])

    for adresse in liens_produits:
        writer.writerow([adresse])

# 6. Afficher le résultat.
print("Nombre de liens trouvés :", len(liens_produits))
print("Les liens sont enregistrés dans liens_produits.csv")