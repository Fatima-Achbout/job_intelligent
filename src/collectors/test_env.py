import os
from dotenv import load_dotenv

load_dotenv()

client_id = os.getenv("FRANCE_TRAVAIL_CLIENT_ID")
client_secret = os.getenv("FRANCE_TRAVAIL_CLIENT_SECRET")

print("Client ID chargé :", bool(client_id))
print("Client Secret chargé :", bool(client_secret))