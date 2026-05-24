import requests
import json
import os
import time
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]
ENV_PATH = BASE_DIR / ".env"
RAW_DIR = BASE_DIR / "data" / "raw" / "jsearch"
RAW_DIR.mkdir(parents=True, exist_ok=True)

load_dotenv(dotenv_path=ENV_PATH)
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")


def fetch_jsearch_page(query: str, page: int = 1):
    if not RAPIDAPI_KEY:
        raise ValueError(f"RAPIDAPI_KEY introuvable dans {ENV_PATH}")

    url = "https://jsearch.p.rapidapi.com/search?query=data%20jobs&page=1&num_pages=1&country=us&date_posted=all"

    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }

    params = {
        "query": query,
        "page": page,
        "num_pages": 1,
        "country": "fr",
        "date_posted": "all",
        "language": "fr"
    }

    response = requests.get(url, headers=headers, params=params, timeout=30)

    print(f"\n[DEBUG] query={query} | page={page}")
    print("[DEBUG] Final URL:", response.url)
    print("[DEBUG] Status code:", response.status_code)
    print("[DEBUG] Response:", response.text[:1500])

    response.raise_for_status()
    return response.json()


def collect_multiple_queries():
    queries = [
        "data analyst in Paris",
        "data engineer in Paris",
        "business analyst in Paris",
        "data scientist in Paris",
        "python data in France",
        "power bi in France",
        "sql analyst in France"
    ]

    all_jobs = []
    seen_ids = set()

    for query in queries:
        for page in range(1, 6):
            try:
                payload = fetch_jsearch_page(query=query, page=page)
                jobs = payload.get("data", [])

                print(f"[INFO] {query} | page {page} -> {len(jobs)} jobs")

                if not jobs:
                    break

                for job in jobs:
                    job_id = (
                        job.get("job_id")
                        or job.get("job_apply_link")
                        or job.get("job_google_link")
                    )

                    if job_id and job_id not in seen_ids:
                        seen_ids.add(job_id)
                        job["search_query"] = query
                        all_jobs.append(job)

                time.sleep(1)

            except Exception as e:
                print(f"[WARN] {query} | page {page} -> {e}")
                break

    final_payload = {
        "source": "JSearch",
        "country": "fr",
        "collected_at": datetime.utcnow().isoformat(),
        "results_count": len(all_jobs),
        "data": all_jobs
    }

    filename = RAW_DIR / f"jsearch_bulk_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(final_payload, f, ensure_ascii=False, indent=2)

    print(f"\nFichier sauvegardé : {filename}")
    print(f"Total unique jobs : {len(all_jobs)}")


if __name__ == "__main__":
    collect_multiple_queries()