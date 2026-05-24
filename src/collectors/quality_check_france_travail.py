import pandas as pd

INPUT_FILE = "data/processed/france_travail_all_jobs.csv"


def main():
    df = pd.read_csv(INPUT_FILE, encoding="utf-8-sig")

    print("\n===== APERCU GENERAL =====")
    print("Nombre de lignes :", len(df))
    print("Nombre de colonnes :", len(df.columns))
    print("\nColonnes :")
    print(df.columns.tolist())

    print("\n===== TYPES DES COLONNES =====")
    print(df.dtypes)

    print("\n===== VALEURS MANQUANTES =====")
    print(df.isnull().sum())

    print("\n===== DOUBLONS =====")
    if "job_id" in df.columns:
        print("Nombre de job_id dupliqués :", df["job_id"].duplicated().sum())
    else:
        print("Colonne job_id introuvable")

    print("\n===== APERCU DES 5 PREMIERES LIGNES =====")
    print(df.head())

    print("\n===== STATISTIQUES SUR QUELQUES CHAMPS =====")
    for col in ["title", "company", "location", "contract_type_label", "experience_level"]:
        if col in df.columns:
            print(f"\nTop 10 pour {col} :")
            print(df[col].value_counts(dropna=False).head(10))

    print("\n===== LONGUEUR DES DESCRIPTIONS =====")
    if "description" in df.columns:
        desc_len = df["description"].fillna("").apply(len)
        print("Description min :", desc_len.min())
        print("Description max :", desc_len.max())
        print("Description moyenne :", round(desc_len.mean(), 2))


if __name__ == "__main__":
    main()