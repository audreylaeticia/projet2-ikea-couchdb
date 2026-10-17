import csv
import json
import time

import requests
from bs4 import BeautifulSoup

# Lire les liens enregistrés à l'étape précédente.
with open("liens_nouveaux.csv", encoding="utf-8") as fichier:
    liens = list(csv.DictReader(fichier))
# Extraire seulement les 2 200 premiers liens.
liens = liens[:2200]

colonnes = [
    "identifiant", "nom", "description", "categorie",
    "prix", "devise", "note", "nombre_avis", "url_source"
]

# Le mode "x" évite d'écraser un CSV brut existant.
with open(
    "produits_bruts_nouveaux.csv", "x", newline="", encoding="utf-8"
) as fichier:
    writer = csv.DictWriter(fichier, fieldnames=colonnes)
    writer.writeheader()

    nombre = 0

    for ligne in liens:
        url = ligne["url_source"]
        print("Lecture :", url)

        try:
            reponse = requests.get(url, timeout=30)

            if reponse.status_code in (401, 403, 429):
                print("Accès refusé ou limité : arrêt.")
                break

            reponse.raise_for_status()
            soup = BeautifulSoup(reponse.content, "html.parser")

            produit = None

            # Chercher le bloc Product intégré au HTML.
            for bloc in soup.find_all("script", type="application/ld+json"):
                try:
                    donnees = json.loads(bloc.get_text())
                except json.JSONDecodeError:
                    continue

                # Sur les fiches testées, Product est un objet JSON.
                if isinstance(donnees, dict):
                    type_bloc = donnees.get("@type")

                    if type_bloc == "Product":
                        produit = donnees
                        break

            if produit is None:
                print("Bloc Product absent : produit ignoré.")
                continue

            offre = produit.get("offers") or {}
            if isinstance(offre, list):
                offre = offre[0] if offre else {}

            avis = produit.get("aggregateRating") or {}

            # Conserver les valeurs sans conversion ni nettoyage.
            writer.writerow({
                "identifiant": produit.get("sku", ""),
                "nom": produit.get("name", ""),
                "description": produit.get("description", ""),
                "categorie": produit.get("category", ""),
                "prix": offre.get("price", ""),
                "devise": offre.get("priceCurrency", ""),
                "note": avis.get("ratingValue", ""),
                "nombre_avis": avis.get("reviewCount", ""),
                "url_source": url
            })

            fichier.flush()
            nombre += 1
            print("Produit enregistré :", produit.get("name", ""))

        except requests.RequestException as erreur:
            print("Erreur :", erreur)

        finally:
            # Attendre entre les demandes.
            time.sleep(3)

print("\nNombre de produits enregistrés :", nombre)
print("Fichier créé : produits_bruts_24.csv")