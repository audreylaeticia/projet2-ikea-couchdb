import json
from getpass import getpass

import requests

url_base = "http://127.0.0.1:5984/ikea_produits"

# Saisir les identifiants sans les enregistrer dans le code.
utilisateur = input("Utilisateur CouchDB : ")
mot_de_passe = getpass("Mot de passe CouchDB : ")

with open("donnees.json", encoding="utf-8") as fichier:
    produits = json.load(fichier)

session = requests.Session()
session.auth = (utilisateur, mot_de_passe)

try:
    # Vérifier que la base existe et que la connexion fonctionne.
    reponse = session.get(url_base, timeout=30)
    reponse.raise_for_status()

    importes = 0
    erreurs = 0

    # Envoyer les produits par groupes de 500.
    for debut in range(0, len(produits), 500):
        lot = produits[debut:debut + 500]

        reponse = session.post(
            url_base + "/_bulk_docs",
            json={"docs": lot},
            timeout=60
        )
        reponse.raise_for_status()

        # CouchDB peut signaler une erreur pour un document
        # même si la demande HTTP a réussi.
        for resultat in reponse.json():
            if resultat.get("ok"):
                importes += 1
            else:
                erreurs += 1
                print(
                    "Erreur :",
                    resultat.get("id"),
                    resultat.get("error"),
                    resultat.get("reason", "")
                )

        print("Documents importés :", importes)

    print("\nImportation terminée.")
    print("Documents ajoutés :", importes)
    print("Erreurs :", erreurs)

except requests.RequestException as erreur:
    print("Erreur de connexion ou HTTP :", erreur)

finally:
    session.close()