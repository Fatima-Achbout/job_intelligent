import os
import json
from datetime import datetime
import requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("FRANCE_TRAVAIL_CLIENT_ID")
CLIENT_SECRET = os.getenv("FRANCE_TRAVAIL_CLIENT_SECRET")

TOKEN_URL = "https://entreprise.francetravail.fr/connexion/oauth2/access_token?realm=/partenaire"
SEARCH_URL = "https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search"

RAW_DIR = "data/raw"


def get_access_token():
    payload = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": "api_offresdemploiv2 o2dsoffre"
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = requests.post(TOKEN_URL, data=payload, headers=headers, timeout=30)
    response.raise_for_status()
    return response.json()["access_token"]


def search_jobs(access_token, keyword="BI Analyst", start=0, end=19):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    params = {
        "motsCles": keyword
    }

    headers["Range"] = f"{start}-{end}"

    response = requests.get(SEARCH_URL, headers=headers, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def save_raw_data(data, keyword):
    os.makedirs(RAW_DIR, exist_ok=True)

    safe_keyword = keyword.lower().replace(" ", "_")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = os.path.join(RAW_DIR, f"france_travail_{safe_keyword}_{timestamp}.json")

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return file_path


def main():
    keyword = "BI Analyst"

    token = get_access_token()
    jobs_data = search_jobs(token, keyword=keyword, start=0, end=19)
    file_path = save_raw_data(jobs_data, keyword)

    print("Collecte terminée")
    print("Mot-clé :", keyword)
    print("Fichier sauvegardé :", file_path)


if __name__ == "__main__":
    main()