from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

PROJECT_BASE = "/opt/airflow/project/job_intelligent"
PROJECT_SCRIPTS = "/opt/airflow/project/scripts"

with DAG(
    dag_id="job_intelligent_pipeline_v2_postgres_star_schema",
    start_date=datetime(2026, 4, 1),
    schedule="@daily",
    catchup=False,
    description="Pipeline Job Intelligent V2 avec branches par source + PostgreSQL + schéma étoile",
) as dag:

    check_france_travail = BashOperator(
        task_id="check_france_travail_data",
        bash_command=f"test -f {PROJECT_BASE}/data/processed/france_travail_all_jobs_cleaned.csv",
    )

    check_jsearch = BashOperator(
        task_id="check_jsearch_data",
        bash_command=f"test -f {PROJECT_BASE}/data/processed/jsearch_all_jobs_cleaned.csv",
    )

    check_linkedin = BashOperator(
        task_id="check_linkedin_data",
        bash_command=f"test -f {PROJECT_BASE}/data/processed/linkedin_all_jobs_cleaned.csv",
    )

    merge = BashOperator(
        task_id="merge_all_sources",
        bash_command=f"python {PROJECT_SCRIPTS}/merge_all_sources.py",
    )

    dedup = BashOperator(
        task_id="deduplicate_jobs",
        bash_command=f"python {PROJECT_SCRIPTS}/deduplicate_jobs.py",
    )

    skills = BashOperator(
        task_id="extract_skills_all",
        bash_command=f"python {PROJECT_SCRIPTS}/extract_skills_all.py",
    )

    match = BashOperator(
        task_id="match_jobs",
        bash_command=f"python {PROJECT_SCRIPTS}/match_jobs.py",
    )

    upload = BashOperator(
        task_id="upload_to_blob",
        bash_command=f"python {PROJECT_SCRIPTS}/upload_to_blob.py",
    )

    load_postgres = BashOperator(
        task_id="load_to_postgresql_star_schema",
        bash_command=f"python {PROJECT_SCRIPTS}/load_to_postgresql.py",
    )

    [check_france_travail, check_jsearch, check_linkedin] >> merge
    merge >> dedup >> skills >> match >> upload >> load_postgres