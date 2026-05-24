import os
import json
import re
import csv
from glob import glob
from pathlib import Path
from bs4 import BeautifulSoup

# ── Chemins robustes ──────────────────────────────────────
# src/collectors/normalize_linkedin.py -> remonte à job_intelligent/
BASE_DIR = Path(__file__).resolve().parents[2]
RAW_DIR = BASE_DIR / "data" / "raw" / "linkedin"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


# ── Extraction depuis raw_html ────────────────────────────
def extract_job_id(raw_html: str) -> str:
    """Extrait le job_id depuis data-entity-urn='urn:li:jobPosting:XXXXXX'."""
    if not raw_html:
        return ""

    soup = BeautifulSoup(raw_html, "html.parser")
    tag = soup.find(attrs={"data-entity-urn": True})
    if tag:
        urn = tag.get("data-entity-urn", "")
        return urn.split(":")[-1]

    match = re.search(r"jobPosting:(\d+)", raw_html)
    return match.group(1) if match else ""


def extract_publication_date(raw_html: str) -> str:
    """Extrait la date depuis <time datetime='YYYY-MM-DD'>."""
    if not raw_html:
        return ""

    soup = BeautifulSoup(raw_html, "html.parser")
    time_tag = soup.find("time", {"datetime": True})
    return time_tag["datetime"] if time_tag else ""


# ── Détection contract_type depuis le titre ───────────────
def detect_contract_type(title: str) -> str:
    t = (title or "").upper()
    if any(x in t for x in ["STAGE", "INTERNSHIP", "INTERN"]):
        return "STAGE"
    if any(x in t for x in ["ALTERNANCE", "APPRENTICESHIP", "APPRENTI"]):
        return "ALTERNANCE"
    if "FREELANCE" in t or "CONSULTANT INDÉPENDANT" in t or "CONSULTANT INDEPENDANT" in t:
        return "FREELANCE"
    if "CDD" in t:
        return "CDD"
    return "CDI"


# ── Détection experience_level depuis le titre ────────────
def detect_experience_level(title: str) -> str:
    t = (title or "").upper()
    if "SENIOR" in t or "SR." in t:
        return "Senior"
    if "JUNIOR" in t or "JR." in t:
        return "Junior"
    if any(x in t for x in ["CONFIRMÉ", "CONFIRME", "EXPÉRIMENTÉ", "EXPERIMENTE"]):
        return "Confirmé"
    if any(x in t for x in ["STAGE", "ALTERNANCE", "APPRENTICESHIP"]):
        return "Stage/Alternance"
    return "Non spécifié"


# ── Parsing localisation ──────────────────────────────────
def parse_location(location: str) -> tuple[str, str]:
    """
    'Paris, Île-de-France, France'  -> city='Paris', region='Île-de-France'
    'Île-de-France, France'         -> city='',      region='Île-de-France'
    'France'                        -> city='',      region='France'
    """
    if not location:
        return "", ""

    parts = [p.strip() for p in location.split(",") if p.strip()]

    if len(parts) >= 3:
        return parts[0], parts[1]

    if len(parts) == 2:
        known_regions = {
            "île-de-france", "ile-de-france", "nouvelle-aquitaine", "occitanie",
            "auvergne-rhône-alpes", "auvergne-rhone-alpes", "bretagne", "normandie",
            "provence-alpes-côte d'azur", "provence-alpes-cote d'azur",
            "hauts-de-france", "grand est", "pays de la loire",
            "centre-val de loire", "bourgogne-franche-comté", "bourgogne-franche-comte",
            "corse"
        }
        if parts[0].lower() in known_regions:
            return "", parts[0]
        return parts[0], parts[1]

    return "", parts[0]


# ── Normalisation d'un job ────────────────────────────────
def normalize_job(job: dict, keyword: str) -> dict:
    raw_html = job.get("raw_html", "") or ""
    title = (job.get("title") or "").strip()
    location = (job.get("location") or "").strip()
    city, region = parse_location(location)

    extracted_job_id = extract_job_id(raw_html)
    fallback_job_id = str(job.get("id", "") or job.get("job_id", "")).strip()
    job_id = extracted_job_id or fallback_job_id

    pub_date = extract_publication_date(raw_html) or (job.get("date_posted") or "")
    company = (job.get("company") or job.get("organization") or "").strip()

    return {
        "job_id": f"li_{job_id}" if job_id else "",
        "title": title,
        "company": company,
        "location": location,
        "city": city,
        "region": region,
        "contract_type": detect_contract_type(title),
        "experience_level": detect_experience_level(title),
        "publication_date": pub_date,
        "description": (job.get("description") or "").strip(),
        "source_url": job.get("job_url", "") or "",
        "source": "LinkedIn",
        "keyword": keyword,
    }


# ── Traitement d'un fichier ───────────────────────────────
def normalize_file(input_path: Path) -> tuple[Path, int, int]:
    with open(input_path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    # Cas 1 : format enveloppé
    # {
    #   "keyword": "...",
    #   "results": [...]
    # }
    if isinstance(raw, dict):
        keyword = raw.get("keyword", "")
        results = raw.get("results", [])

    # Cas 2 : liste directe de jobs
    # [ {...}, {...} ]
    elif isinstance(raw, list):
        keyword = ""
        results = raw

    else:
        raise ValueError(f"Format JSON non supporté dans {input_path}")

    normalized = [normalize_job(job, keyword) for job in results if isinstance(job, dict)]

    before = len(normalized)
    normalized = [j for j in normalized if j["title"] and j["company"]]
    filtered = before - len(normalized)

    base_name = input_path.stem + "_clean.json"
    output_path = PROCESSED_DIR / base_name

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(normalized, f, ensure_ascii=False, indent=2)

    return output_path, len(normalized), filtered


# ── Main ──────────────────────────────────────────────────
def main():
    print("BASE_DIR       :", BASE_DIR)
    print("RAW_DIR        :", RAW_DIR)
    print("PROCESSED_DIR  :", PROCESSED_DIR)
    print("RAW_DIR exists :", RAW_DIR.exists())
    print()

    files = sorted(RAW_DIR.glob("*.json"))

    if not files:
        print(f"Aucun fichier JSON dans {RAW_DIR}")
        print("Vérifiez que vos fichiers LinkedIn sont bien dans data/raw/linkedin/")
        return

    print(f"{len(files)} fichier(s) LinkedIn trouvé(s)\n")

    total_jobs = 0
    total_filtered = 0
    all_jobs = []

    for path in files:
        out_path, count, filtered = normalize_file(path)
        total_jobs += count
        total_filtered += filtered

        print(f"✅ {path.name}")
        print(f"   → {out_path}")
        print(f"   → {count} offres normalisées ({filtered} filtrées)\n")

        with open(out_path, "r", encoding="utf-8") as f:
            all_jobs.extend(json.load(f))

    csv_path = PROCESSED_DIR / "linkedin_all_jobs_cleaned.csv"
    if all_jobs:
        fieldnames = list(all_jobs[0].keys())
        with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_jobs)

    print("=" * 50)
    print(f"TOTAL : {total_jobs} offres normalisées")
    print(f"FILTRÉES : {total_filtered} offres (sans titre/entreprise)")
    print(f"CSV global : {csv_path}")
    print("=" * 50)
    print("\nProchaine étape → merge_all_sources.py")


if __name__ == "__main__":
    main()