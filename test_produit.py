import requests
from bs4 import BeautifulSoup

url = (
    "https://www.ikea.com/ca/fr/p/"
    "begavning-cloche-en-verre-sur-socle-50343939/"
)

try:
    reponse = requests.get(url, timeout=30)
    print("Code HTTP :", reponse.status_code)
    reponse.raise_for_status()

    soup = BeautifulSoup(reponse.content, "html.parser")

    titre = soup.find("title")
    print("Titre :", titre.get_text(strip=True) if titre else "Absent")

    # Afficher les données structurées intégrées dans le HTML.
    blocs = soup.find_all("script", type="application/ld+json")

    print("\nNombre de blocs JSON-LD :", len(blocs))

    for numero, bloc in enumerate(blocs, start=1):
        print(f"\n--- Bloc {numero} ---")
        print(bloc.get_text())

    # Examiner aussi le titre et les prix dans les balises HTML.
    print("\n--- Titres H1 ---")

    for titre in soup.find_all("h1"):
        print(titre.get_text(" ", strip=True))

    print("\n--- Balises avec itemprop ---")

    for balise in soup.select(
        '[itemprop="price"], [itemprop="priceCurrency"], [itemprop="name"]'
    ):
        print(
            balise.get("itemprop"),
            ":",
            balise.get("content") or balise.get_text(" ", strip=True)
        )

except requests.RequestException as erreur:
    print("Erreur de connexion ou HTTP :", erreur)