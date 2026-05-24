import os
from pathlib import Path

import pandas as pd
import psycopg2
import streamlit as st
import pdfplumber
from docx import Document
from dotenv import load_dotenv

BASE_PATH = Path(r"C:\Users\pc\Downloads\job_intelligent\job_intelligent")
load_dotenv(BASE_PATH / ".env")

POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

SKILLS_LIST = [
    "python", "sql", "airflow", "docker", "spark", "azure",
    "power bi", "databricks", "etl", "pandas", "excel",
    "machine learning", "nlp", "hadoop", "hdfs", "kafka",
    "postgresql", "data warehouse", "data lake", "streamlit"
]

st.set_page_config(
    page_title="Job Intelligent",
    page_icon="🚀",
    layout="wide"
)

st.markdown("""
<style>
.main {
    background-color: #f7f9fc;
}
.title-box {
    background: linear-gradient(90deg, #1f4e79, #2f80ed);
    padding: 28px;
    border-radius: 18px;
    color: white;
    margin-bottom: 25px;
}
.metric-card {
    background-color: white;
    padding: 18px;
    border-radius: 16px;
    box-shadow: 0 3px 10px rgba(0,0,0,0.08);
    text-align: center;
}
.job-card {
    background-color: white;
    border-radius: 18px;
    padding: 22px;
    margin-bottom: 18px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.10);
    border-left: 7px solid #2f80ed;
}
.badge {
    background-color: #eaf3ff;
    color: #1f4e79;
    padding: 6px 10px;
    border-radius: 12px;
    margin-right: 6px;
    display: inline-block;
    margin-bottom: 6px;
}
.score-green {
    color: #138a36;
    font-weight: bold;
}
.score-orange {
    color: #d97706;
    font-weight: bold;
}
.score-red {
    color: #dc2626;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)


def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
            text += "\n"
    return text


def extract_text_from_docx(file):
    doc = Document(file)
    return "\n".join([p.text for p in doc.paragraphs])


def extract_skills(text):
    text = text.lower()
    return sorted(list(set([skill for skill in SKILLS_LIST if skill in text])))


def get_jobs_from_postgres():
    conn = psycopg2.connect(
        host=POSTGRES_HOST,
        database=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        port=POSTGRES_PORT,
        sslmode="require"
    )

    query = """
    SELECT
        j.job_uid,
        j.title,
        c.company_name,
        l.location_name,
        s.source_name,
        STRING_AGG(DISTINCT sk.skill_name, ', ') AS job_skills,
        MAX(fm.match_score) AS old_match_score
    FROM fact_job_offer fo
    JOIN dim_job j ON fo.job_key = j.job_key
    JOIN dim_company c ON fo.company_id = c.company_id
    JOIN dim_location l ON fo.location_id = l.location_id
    JOIN dim_source s ON fo.source_id = s.source_id
    LEFT JOIN fact_job_matching fm ON j.job_key = fm.job_key
    LEFT JOIN dim_skill sk ON fm.skill_id = sk.skill_id
    GROUP BY
        j.job_uid, j.title, c.company_name, l.location_name, s.source_name
    """

    df = pd.read_sql(query, conn)
    conn.close()
    return df


def compute_score(candidate_skills, job_skills):
    job_skills_text = str(job_skills).lower()
    matched = [skill for skill in candidate_skills if skill in job_skills_text]

    if not candidate_skills:
        return 0, []

    score = int((len(matched) / len(candidate_skills)) * 100)
    return score, matched


def score_class(score):
    if score >= 70:
        return "score-green"
    if score >= 40:
        return "score-orange"
    return "score-red"


st.markdown("""
<div class="title-box">
    <h1>🚀 Job Intelligent</h1>
    <p>Plateforme intelligente de recommandation d’offres d’emploi dans la Data</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ Filtres")
    min_score = st.slider("Score minimum", 0, 100, 0)
    top_n = st.slider("Nombre d'offres à afficher", 5, 30, 10)
    st.markdown("---")
    st.write("📌 Pipeline : Airflow + Azure Blob + PostgreSQL + Power BI")
    st.write("⭐ Modèle : Schéma en étoile")

uploaded_file = st.file_uploader(
    "📄 Importer votre CV",
    type=["pdf", "docx", "txt"]
)

if uploaded_file is None:
    st.info("Importe un CV pour afficher les offres recommandées.")
else:
    file_type = uploaded_file.name.split(".")[-1].lower()

    if file_type == "pdf":
        cv_text = extract_text_from_pdf(uploaded_file)
    elif file_type == "docx":
        cv_text = extract_text_from_docx(uploaded_file)
    else:
        cv_text = uploaded_file.read().decode("utf-8", errors="ignore")

    candidate_skills = extract_skills(cv_text)

    st.subheader("🧠 Compétences détectées")

    if candidate_skills:
        badges = "".join([f'<span class="badge">{skill}</span>' for skill in candidate_skills])
        st.markdown(badges, unsafe_allow_html=True)
    else:
        st.warning("Aucune compétence détectée. Ajoute plus de mots-clés à SKILLS_LIST.")

    with st.spinner("Chargement des offres depuis PostgreSQL..."):
        jobs_df = get_jobs_from_postgres()

    results = []

    for _, row in jobs_df.iterrows():
        score, matched_skills = compute_score(candidate_skills, row["job_skills"])

        results.append({
            "title": row["title"],
            "company": row["company_name"],
            "location": row["location_name"],
            "source": row["source_name"],
            "job_skills": row["job_skills"],
            "matched_skills": matched_skills,
            "score": score
        })

    results_df = pd.DataFrame(results)
    results_df = results_df[results_df["score"] >= min_score]
    results_df = results_df.sort_values(by="score", ascending=False).head(top_n)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{len(candidate_skills)}</h3>
            <p>Compétences CV</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{len(results_df)}</h3>
            <p>Offres recommandées</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        best_score = int(results_df["score"].max()) if not results_df.empty else 0
        st.markdown(f"""
        <div class="metric-card">
            <h3>{best_score}%</h3>
            <p>Meilleur score</p>
        </div>
        """, unsafe_allow_html=True)

    st.subheader("🎯 Offres recommandées")

    if results_df.empty:
        st.warning("Aucune offre ne correspond au filtre actuel.")
    else:
        for _, job in results_df.iterrows():
            matched_badges = "".join([
                f'<span class="badge">{skill}</span>' for skill in job["matched_skills"]
            ])

            st.markdown(f"""
            <div class="job-card">
                <h3>{job['title']}</h3>
                <p><b>🏢 Entreprise :</b> {job['company']}</p>
                <p><b>📍 Localisation :</b> {job['location']}</p>
                <p><b>🔗 Source :</b> {job['source']}</p>
                <p><b>⭐ Score :</b> <span class="{score_class(job['score'])}">{job['score']}%</span></p>
                <p><b>✅ Compétences matchées :</b></p>
                {matched_badges if matched_badges else "<p>Aucune compétence matchée</p>"}
                <p><b>📌 Compétences de l'offre :</b> {job['job_skills']}</p>
            </div>
            """, unsafe_allow_html=True)

    with st.expander("Voir le texte extrait du CV"):
        st.text_area("Texte CV", cv_text[:4000], height=250)