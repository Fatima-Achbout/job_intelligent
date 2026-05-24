import pandas as pd

INPUT_FILE = "data/processed/france_travail_all_jobs_skills.csv"
OUTPUT_FILE = "data/processed/france_travail_all_jobs_matched.csv"

USER_PROFILE_SKILLS = [
    "python",
    "sql",
    "power bi",
    "azure"
]


def compute_match_score(row, profile_skills):
    matched_skills = []

    for skill in profile_skills:
        col_name = skill.replace(" ", "_") + "_skill"
        if col_name in row.index and row[col_name] == 1:
            matched_skills.append(skill)

    score = round((len(matched_skills) / len(profile_skills)) * 100, 2)
    return score, matched_skills


def main():
    df = pd.read_csv(INPUT_FILE, encoding="utf-8-sig")

    scores = []
    matched_skills_list = []

    for _, row in df.iterrows():
        score, matched_skills = compute_match_score(row, USER_PROFILE_SKILLS)
        scores.append(score)
        matched_skills_list.append(", ".join(matched_skills))

    df["match_score"] = scores
    df["matched_skills"] = matched_skills_list

    df = df.sort_values(by="match_score", ascending=False)

    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

    print("Matching terminé")
    print("Fichier sauvegardé :", OUTPUT_FILE)
    print("Nombre de lignes :", len(df))
    print("Top 10 scores :")
    print(df[["title", "company", "match_score", "matched_skills"]].head(10))


if __name__ == "__main__":
    main()