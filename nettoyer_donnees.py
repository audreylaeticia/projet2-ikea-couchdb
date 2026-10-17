import csv
import json
import math

# Les deux fichiers contenant les produits extraits.
fichiers = [
    "produits_bruts_681.csv",
    "produits_bruts_nouveaux.csv"
]

produits = []
identifiants = set()

nombre_lignes = 0
doublons = 0
sans_identifiant = 0
nombres_invalides = 0


def nettoyer_texte(valeur):
    """Enlever les espaces inutiles et remplacer un texte vide par None."""
    texte = " ".join((valeur or "").split())
    return texte if texte else None


def convertir_nombre(valeur, entier=False):
    """Convertir un nombre. Une valeur absente ou invalide devient None."""
    global nombres_invalides

    texte = nettoyer_texte(valeur)

    if texte is None:
        return None

    try:
        nombre = float(texte.replace(",", "."))

        if not math.isfinite(nombre) or nombre < 0:
            raise ValueError

        if entier:
            if not nombre.is_integer():
                raise ValueError
            return int(nombre)

        return nombre

    except ValueError:
        nombres_invalides += 1
        return None


# 1. Lire les CSV bruts.
for nom_fichier in fichiers:
    with open(nom_fichier, encoding="utf-8", newline="") as fichier:
        lecteur = csv.DictReader(fichier)

        for ligne in lecteur:
            nombre_lignes += 1

            # 2. Préparer l'identifiant stable.
            identifiant = nettoyer_texte(ligne["identifiant"])

            if identifiant is None:
                sans_identifiant += 1
                continue

            identifiant = identifiant.replace(".", "").replace(" ", "")
            identifiant = "ikea_" + identifiant

            # 3. Retirer les doublons.
            if identifiant in identifiants:
                doublons += 1
                continue

            identifiants.add(identifiant)

            # 4. Nettoyer les champs et convertir les nombres.
            produit = {
                "_id": identifiant,
                "nom": nettoyer_texte(ligne["nom"]),
                "description": nettoyer_texte(ligne["description"]),
                "categorie": nettoyer_texte(ligne["categorie"]),
                "prix": convertir_nombre(ligne["prix"]),
                "devise": nettoyer_texte(ligne["devise"]),
                "evaluation": {
                    "note": convertir_nombre(ligne["note"]),
                    "nombre_avis": convertir_nombre(
                        ligne["nombre_avis"], entier=True
                    )
                },
                "url_source": nettoyer_texte(ligne["url_source"])
            }

            produits.append(produit)

# 5. Créer un tableau JSON en conservant les accents.
with open("donnees.json", "w", encoding="utf-8") as fichier:
    json.dump(
        produits,
        fichier,
        ensure_ascii=False,
        indent=2,
        allow_nan=False
    )

# 6. Afficher le bilan.
print("Lignes avant nettoyage :", nombre_lignes)
print("Doublons retirés :", doublons)
print("Lignes sans identifiant retirées :", sans_identifiant)
print("Valeurs numériques invalides remplacées par null :", nombres_invalides)
print("Produits après nettoyage :", len(produits))
print("Fichier créé : donnees.json")

if len(produits) < 2500:
    print("Attention : le minimum de 2 500 produits n'est pas atteint.")