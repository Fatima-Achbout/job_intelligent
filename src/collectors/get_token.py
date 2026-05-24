import os
import requests
from dotenv import load_dotenv

load_dotenv()

client_id = os.getenv("FRANCE_TRAVAIL_CLIENT_ID")
client_secret = os.getenv("FRANCE_TRAVAIL_CLIENT_SECRET")

token_url = "https://entreprise.francetravail.fr/connexion/oauth2/access_token?realm=/partenaire"

payload = {
    "grant_type": "client_credentials",
    "client_id": client_id,
    "client_secret": client_secret,
    "scope": "api_offresdemploiv2 o2dsoffre"
}

headers = {
    "Content-Type": "application/x-www-form-urlencoded"
}

response = requests.post(token_url, data=payload, headers=headers, timeout=30)

print("Status code :", response.status_code)
print("Réponse :")
print(response.text)