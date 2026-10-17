import csv

# Lire les liens du premier lot.
with open(
    "liens_plusieurs_categories.csv", encoding="utf-8"
) as fichier:
    anciens_liens = []

    for ligne in csv.DictReader(fichier):
        anciens_liens.append(ligne["url_source"])

# Garder uniquement les nouveaux liens.
nouveaux_liens = []

with open(
    "liens_categories_restantes.csv", encoding="utf-8"
) as fichier:
    for ligne in csv.DictReader(fichier):
        url = ligne["url_source"]

        if url not in anciens_liens and url not in nouveaux_liens:
            nouveaux_liens.append(url)

# Enregistrer sans écraser un fichier existant.
with open(
    "liens_nouveaux.csv", "x", newline="", encoding="utf-8"
) as fichier:
    writer = csv.writer(fichier)
    writer.writerow(["url_source"])

    for url in nouveaux_liens:
        writer.writerow([url])

print("Nouveaux liens :", len(nouveaux_liens))
print("Fichier créé : liens_nouveaux.csv")