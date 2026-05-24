import csv
import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parents[2]
RAW_DIR = BASE_DIR / "data" / "raw" / "jsearch"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def parse_location(job: dict):
    city = (job.get("job_city") or "").strip()
    region = (job.get("job_state") or "").strip()
    country = (job.get("job_country") or "").strip()

    parts = [p for p in [city, region, country] if p]
    location = ", ".join(parts)

    return location, city, region


def detect_contract_type(job: dict) -> str:
    employment_type = (job.get("job_employment_type") or "").strip()
    title = (job.get("job_title") or "").upper()
    description = (job.get("job_description") or "").upper()
    text = f"{employment_type} {title} {description}".upper()

    if any(x in text for x in ["STAGE", "INTERNSHIP", "INTERN"]):
        return "STAGE"
    if any(x in text for x in ["ALTERNANCE", "APPRENTICESHIP", "APPRENTI"]):
        return "ALTERNANCE"
    if "CDD" in text:
        return "CDD"
    if "FREELANCE" in text or "CONTRACT" in text:
        return "FREELANCE"
    if any(x in text for x in ["FULL_TIME", "FULL-TIME", "FULL TIME", "CDI"]):
        return "CDI"

    return employment_type if employment_type else "Non spécifié"


def detect_experience_level(job: dict) -> str:
    title = (job.get("job_title") or "").upper()
    description = (job.get("job_description") or "").upper()
    text = f"{title} {description}"

    if "SENIOR" in text or "SR." in text:
        return "Senior"
    if "JUNIOR" in text or "JR." in text:
        return "Junior"
    if any(x in text for x in ["CONFIRMÉ", "CONFIRME", "EXPÉRIMENTÉ", "EXPERIMENTE"]):
        return "Confirmé"
    if any(x in text for x in ["STAGE", "ALTERNANCE", "APPRENTICESHIP"]):
        return "Stage/Alternance"

    return "Non spécifié"


def normalize_publication_date(job: dict) -> str:
    value = (job.get("job_posted_at_datetime_utc") or "").strip()
    if value:
        return value

    posted = (job.get("job_posted_at") or "").strip()
    return posted


def normalize_job(job: dict) -> dict:
    location, city, region = parse_location(job)

    source_url = (
        (job.get("job_apply_link") or "").strip()
        or (job.get("job_google_link") or "").strip()
        or (job.get("job_offer_expiration_datetime_utc") or "").strip()
    )

    return {
        "job_id": (job.get("job_id") or "").strip(),
        "title": (job.get("job_title") or "").strip(),
        "company": (job.get("employer_name") or "").strip(),
        "location": location,
        "city": city,
        "region": region,
        "contract_type": detect_contract_type(job),
        "experience_level": detect_experience_level(job),
        "publication_date": normalize_publication_date(job),
        "description": (job.get("job_description") or "").strip(),
        "source_url": source_url,
        "source": "JSearch",
        "keyword": (job.get("search_query") or "").strip()
    }


def normalize_file(input_path: Path):
    with open(input_path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    jobs = raw.get("data", [])
    normalized = [normalize_job(job) for job in jobs if isinstance(job, dict)]

    before = len(normalized)
    normalized = [j for j in normalized if j["title"] and j["company"]]
    filtered = before - len(normalized)

    output_path = PROCESSED_DIR / f"{input_path.stem}_clean.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(normalized, f, ensure_ascii=False, indent=2)

    return output_path, len(normalized), filtered


def main():
    files = sorted(RAW_DIR.glob("*.json"))

    if not files:
        print(f"Aucun fichier JSON dans {RAW_DIR}")
        return

    all_jobs = []
    total_jobs = 0
    total_filtered = 0

    for path in files:
        out_path, count, filtered = normalize_file(path)
        total_jobs += count
        total_filtered += filtered

        print(f"✅ {path.name}")
        print(f"   → {out_path}")
        print(f"   → {count} offres normalisées ({filtered} filtrées)\n")

        with open(out_path, "r", encoding="utf-8") as f:
            all_jobs.extend(json.load(f))

    csv_path = PROCESSED_DIR / "jsearch_all_jobs_cleaned.csv"
    if all_jobs:
        fieldnames = list(all_jobs[0].keys())
        with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_jobs)

    print("=" * 50)
    print(f"TOTAL : {total_jobs} offres normalisées")
    print(f"FILTRÉES : {total_filtered}")
    print(f"CSV global : {csv_path}")
    print("=" * 50)


if __name__ == "__main__":
    main()
    