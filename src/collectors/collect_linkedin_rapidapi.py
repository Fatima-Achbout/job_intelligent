import requests
import json
import os
import time
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]
ENV_PATH = BASE_DIR / ".env"
RAW_DIR = BASE_DIR / "data" / "raw" / "indeed"
RAW_DIR.mkdir(parents=True, exist_ok=True)

load_dotenv(dotenv_path=ENV_PATH)
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")


def fetch_one_page(query: str, location: str = "france", page_id: int = 1):
    if not RAPIDAPI_KEY:
        raise ValueError(f"RAPIDAPI_KEY introuvable dans {ENV_PATH}")

    url = "https://indeed12.p.rapidapi.com/jobs/search"

    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": "indeed12.p.rapidapi.com"
    }

    params = {
        "query": query,
        "location": location,
        "page_id": page_id,
        "locality": "fr",
        "radius": 50,
        "sort": "date"
    }

    response = requests.get(url, headers=headers, params=params, timeout=30)
    print(f"[DEBUG] {query=} {location=} {page_id=} -> {response.status_code}")
    print("[DEBUG] Final URL:", response.url)

    if response.status_code != 200:
        print("[DEBUG] Response:", response.text[:1500])

    response.raise_for_status()
    return response.json()


def collect_many_pages(query: str, location: str = "france", max_pages: int = 20, sleep_sec: float = 1.0):
    all_hits = []
    seen_ids = set()
    current_page = 1

    for _ in range(max_pages):
        payload = fetch_one_page(query=query, location=location, page_id=current_page)

        hits = payload.get("hits", [])
        next_page_id = payload.get("next_page_id")

        print(f"[INFO] page {current_page} -> {len(hits)} offres")

        for job in hits:
            job_id = job.get("id")
            if job_id and job_id not in seen_ids:
                seen_ids.add(job_id)
                all_hits.append(job)

        if not next_page_id:
            break

        current_page = next_page_id
        time.sleep(sleep_sec)

    return {
        "source": "indeed",
        "query": query,
        "location": location,
        "collected_at": datetime.utcnow().isoformat(),
        "results_count": len(all_hits),
        "hits": all_hits
    }


def collect_multiple_queries():
    queries = [
        "data",
        "data analyst",
        "business analyst",
        "bi analyst",
        "data engineer"
    ]

    merged = []
    seen_ids = set()

    for q in queries:
        try:
            payload = collect_many_pages(query=q, location="france", max_pages=20, sleep_sec=1.0)
            print(f"[INFO] {q} -> {payload['results_count']} offres")
            for job in payload["hits"]:
                job_id = job.get("id")
                if job_id and job_id not in seen_ids:
                    seen_ids.add(job_id)
                    job["search_query"] = q
                    merged.append(job)
        except Exception as e:
            print(f"[WARN] erreur pour {q}: {e}")

    final_payload = {
        "source": "indeed",
        "location": "france",
        "collected_at": datetime.utcnow().isoformat(),
        "results_count": len(merged),
        "hits": merged
    }

    filename = RAW_DIR / f"indeed_bulk_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(final_payload, f, ensure_ascii=False, indent=2)

    print(f"Fichier sauvegardé : {filename}")
    print(f"Total unique Indeed : {len(merged)}")


if __name__ == "__main__":
    collect_multiple_queries()