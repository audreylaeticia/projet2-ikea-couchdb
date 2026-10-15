import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

url = "https://www.ikea.com/ca/fr/cat/accessoires-decoratifs-24924/"

try:
    reponse = requests.get(url, timeout=30)

    print("Code HTTP :", reponse.status_code)
    reponse.raise_for_status()

    soup = BeautifulSoup(reponse.content, "html.parser")

    titre = soup.find("title")
    print("Titre :", titre.get_text(strip=True) if titre else "Absent")

    categories = set()
    produits = set()

    for lien in soup.find_all("a", href=True):
        adresse = urljoin(reponse.url, lien["href"])

        # Ignorer les URL avec des paramètres.
        if "?" in adresse:
            continue

        # Retirer les ancres pour éviter les doublons.
        adresse = adresse.split("#")[0]

        if adresse.startswith("https://www.ikea.com/ca/fr/cat/"):
            categories.add(adresse)

        elif adresse.startswith("https://www.ikea.com/ca/fr/p/"):
            produits.add(adresse)

    print("\nNombre de liens de catégories :", len(categories))

    for adresse in sorted(categories)[:10]:
        print(adresse)

    print("\nNombre de liens de produits :", len(produits))

    for adresse in sorted(produits)[:5]:
        print(adresse)

except requests.RequestException as erreur:
    print("Erreur de connexion ou HTTP :", erreur)