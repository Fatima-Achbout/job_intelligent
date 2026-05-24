import os
import json
from glob import glob


RAW_DIR = "data/raw"
PROCESSED_DIR = "data/processed"


def extract_job_fields(job: dict) -> dict:
    entreprise = job.get("entreprise", {}) or {}
    lieu = job.get("lieuTravail", {}) or {}

    return {
        "job_id": job.get("id"),
        "title": job.get("intitule"),
        "company": entreprise.get("nom"),
        "location": lieu.get("libelle"),
        "postal_code": lieu.get("codePostal"),
        "contract_type": job.get("typeContrat"),
        "contract_type_label": job.get("typeContratLibelle"),
        "experience_level": job.get("experienceLibelle"),
        "publication_date": job.get("dateCreation"),
        "update_date": job.get("dateActualisation"),
        "description": job.get("description"),
        "source_url": job.get("origineOffre", {}).get("urlOrigine"),
        "source": "France Travail"
    }


def normalize_file(input_file: str) -> str:
    os.makedirs(PROCESSED_DIR, exist_ok=True)

    with open(input_file, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    jobs = raw_data.get("resultats", [])
    normalized_jobs = [extract_job_fields(job) for job in jobs]

    base_name = os.path.basename(input_file).replace(".json", "_clean.json")
    output_file = os.path.join(PROCESSED_DIR, base_name)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(normalized_jobs, f, ensure_ascii=False, indent=2)

    return output_file, len(normalized_jobs)


def main():
    raw_files = glob(os.path.join(RAW_DIR, "*.json"))

    if not raw_files:
        print("Aucun fichier JSON trouvé dans data/raw/")
        return

    print(f"{len(raw_files)} fichier(s) trouvé(s).")

    for file_path in raw_files:
        output_file, count = normalize_file(file_path)
        print(f"Normalisation terminée : {output_file}")
        print(f"Nombre d'offres normalisées : {count}")


if __name__ == "__main__":
    main()