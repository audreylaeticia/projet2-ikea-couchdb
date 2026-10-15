import csv
import json
import requests
from bs4 import BeautifulSoup

url = (
    "https://www.ikea.com/ca/fr/p/"
    "begavning-cloche-en-verre-sur-socle-50343939/"
)


def trouver_produit(donnees):
    """Chercher un objet Product dans les données JSON-LD."""
    if isinstance(donnees, list):
        for element in donnees:
            produit = trouver_produit(element)
            if produit is not None:
                return produit

    elif isinstance(donnees, dict):
        types = donnees.get("@type", [])
        if isinstance(types, str):
            types = [types]

        if "Product" in types:
            return donnees

        if "@graph" in donnees:
            return trouver_produit(donnees["@graph"])

    return None


try:
    reponse = requests.get(url, timeout=30)
    reponse.raise_for_status()

    soup = BeautifulSoup(reponse.content, "html.parser")
    produit = None

    for bloc in soup.find_all("script", type="application/ld+json"):
        try:
            donnees = json.loads(bloc.get_text())
        except json.JSONDecodeError:
            continue

        produit = trouver_produit(donnees)

        if produit is not None:
            break

    if produit is None:
        print("Aucune donnée Product trouvée.")

    else:
        offre = produit.get("offers") or {}
        if isinstance(offre, list):
            offre = offre[0] if offre else {}

        avis = produit.get("aggregateRating") or {}

        images = produit.get("image") or []
        if not isinstance(images, list):
            images = [images]

        image = images[0] if images else ""
        if isinstance(image, dict):
            image = image.get("contentUrl") or image.get("url", "")

        ligne = {
            "identifiant": produit.get("sku", ""),
            "nom": produit.get("name", ""),
            "description": produit.get("description", ""),
            "categorie": produit.get("category", ""),
            "couleur": produit.get("color", ""),
            "prix": offre.get("price", ""),
            "devise": offre.get("priceCurrency", ""),
            "note": avis.get("ratingValue", ""),
            "nombre_avis": avis.get("reviewCount", ""),
            "url_source": reponse.url,
            "url_image": image,
        }

        with open(
            "produits_test_brut.csv",
            "w",
            newline="",
            encoding="utf-8"
        ) as fichier:
            writer = csv.DictWriter(fichier, fieldnames=ligne.keys())
            writer.writeheader()
            writer.writerow(ligne)

        print("Produit extrait :", ligne["nom"])
        print("Prix brut :", ligne["prix"], ligne["devise"])
        print("CSV créé : produits_test_brut.csv")

except requests.RequestException as erreur:
    print("Erreur de connexion ou HTTP :", erreur)