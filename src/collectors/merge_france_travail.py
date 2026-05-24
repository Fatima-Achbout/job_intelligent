import os
import json
from glob import glob

PROCESSED_DIR = "data/processed"
OUTPUT_FILE = os.path.join(PROCESSED_DIR, "france_travail_all_jobs.json")


def load_all_clean_files():
    files = glob(os.path.join(PROCESSED_DIR, "*_clean.json"))
    all_jobs = []

    for file_path in files:
        with open(file_path, "r", encoding="utf-8") as f:
            jobs = json.load(f)
            all_jobs.extend(jobs)

    return all_jobs


def remove_duplicates(jobs):
    unique_jobs = {}
    for job in jobs:
        job_id = job.get("job_id")
        if job_id:
            unique_jobs[job_id] = job
    return list(unique_jobs.values())


def main():
    jobs = load_all_clean_files()
    print("Nombre total avant suppression des doublons :", len(jobs))

    unique_jobs = remove_duplicates(jobs)
    print("Nombre total après suppression des doublons :", len(unique_jobs))

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(unique_jobs, f, ensure_ascii=False, indent=2)

    print("Fichier fusionné créé :", OUTPUT_FILE)


if __name__ == "__main__":
    main()