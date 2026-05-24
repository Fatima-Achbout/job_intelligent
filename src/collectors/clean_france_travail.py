import pandas as pd

INPUT_FILE = "data/processed/france_travail_all_jobs.csv"
OUTPUT_FILE = "data/processed/france_travail_all_jobs_cleaned.csv"


def clean_text(value):
    if pd.isna(value):
        return value
    value = str(value).strip()
    value = value.replace("\n", " ").replace("\r", " ")
    value = " ".join(value.split())
    return value


def standardize_experience(value):
    if pd.isna(value):
        return "Non renseigné"

    value = str(value).strip().lower()

    if "débutant" in value or value == "0 an(s)":
        return "Junior"
    elif "1 an" in value or "2 an" in value:
        return "Junior"
    elif "3 an" in value or "4 an" in value:
        return "Confirmé"
    elif "5 an" in value or "6 an" in value or "7 an" in value or "8 an" in value:
        return "Senior"
    elif "expérience exigée" in value:
        return "Expérience requise"
    else:
        return value.title()


def extract_department_code(location):
    if pd.isna(location):
        return None
    location = str(location).strip()
    if " - " in location:
        return location.split(" - ")[0]
    return None


def extract_city(location):
    if pd.isna(location):
        return None
    location = str(location).strip()
    if " - " in location:
        return location.split(" - ", 1)[1].title()
    return location.title()


def main():
    df = pd.read_csv(INPUT_FILE, encoding="utf-8-sig")

    # Nettoyage texte
    text_columns = [
        "title",
        "company",
        "location",
        "contract_type",
        "contract_type_label",
        "experience_level",
        "description",
        "source_url",
        "source"
    ]

    for col in text_columns:
        if col in df.columns:
            df[col] = df[col].apply(clean_text)

    # Remplir company manquant
    if "company" in df.columns:
        df["company"] = df["company"].fillna("Non renseigné")

    # Corriger postal_code
    if "postal_code" in df.columns:
        df["postal_code"] = df["postal_code"].fillna(0).astype(int).astype(str)
        df["postal_code"] = df["postal_code"].replace("0", "Non renseigné")

    # Harmoniser location
    if "location" in df.columns:
        df["location"] = df["location"].str.title()

    # Ajouter department_code et city
    df["department_code"] = df["location"].apply(extract_department_code)
    df["city"] = df["location"].apply(extract_city)

    # Standardiser experience_level
    if "experience_level" in df.columns:
        df["experience_level_standardized"] = df["experience_level"].apply(standardize_experience)

    # Convertir les dates
    for col in ["publication_date", "update_date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # Supprimer doublons si jamais
    if "job_id" in df.columns:
        df = df.drop_duplicates(subset=["job_id"])

    # Sauvegarde
    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

    print("Nettoyage terminé")
    print("Fichier sauvegardé :", OUTPUT_FILE)
    print("Nombre de lignes :", len(df))
    print("Nombre de colonnes :", len(df.columns))


if __name__ == "__main__":
    main()