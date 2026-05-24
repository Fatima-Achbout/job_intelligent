import json
import pandas as pd

INPUT_FILE = "data/processed/france_travail_all_jobs.json"
OUTPUT_FILE = "data/processed/france_travail_all_jobs.csv"


def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        jobs = json.load(f)

    df = pd.DataFrame(jobs)
    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

    print("CSV créé :", OUTPUT_FILE)
    print("Nombre de lignes :", len(df))


if __name__ == "__main__":
    main()