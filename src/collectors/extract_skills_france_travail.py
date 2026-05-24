import pandas as pd

INPUT_FILE = "data/processed/france_travail_all_jobs_cleaned.csv"
OUTPUT_FILE = "data/processed/france_travail_all_jobs_skills.csv"

SKILLS = [
    "python",
    "sql",
    "power bi",
    "excel",
    "azure",
    "aws",
    "spark",
    "tableau",
    "machine learning",
    "dataiku",
    "git",
    "hadoop",
    "sas",
    "vba",
    "java",
    "scala",
    "pandas",
    "numpy",
    "etl",
    "airflow",
    "docker",
    "kubernetes"
]


def detect_skills(description):
    if pd.isna(description):
        return []

    text = str(description).lower()
    detected = []

    for skill in SKILLS:
        if skill in text:
            detected.append(skill)

    return detected


def main():
    df = pd.read_csv(INPUT_FILE, encoding="utf-8-sig")

    df["skills_detected"] = df["description"].apply(detect_skills)
    df["skills_detected"] = df["skills_detected"].apply(lambda x: ", ".join(x))

    for skill in SKILLS:
        col_name = skill.replace(" ", "_") + "_skill"
        df[col_name] = df["description"].str.lower().str.contains(skill, na=False).astype(int)

    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

    print("Extraction des compétences terminée")
    print("Fichier sauvegardé :", OUTPUT_FILE)
    print("Nombre de lignes :", len(df))
    print("Nombre de colonnes :", len(df.columns))


if __name__ == "__main__":
    main()