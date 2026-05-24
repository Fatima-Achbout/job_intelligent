from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

PROJECT_SCRIPTS = "/opt/airflow/project/scripts"

with DAG(
    dag_id="job_intelligent_pipeline",
    start_date=datetime(2026, 4, 1),
    schedule="@daily",
    catchup=False,
    description="Pipeline Job Intelligent ETL + Matching + Azure",
) as dag:

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

    load_sql = BashOperator(
        task_id="load_to_azure_sql",
        bash_command=f"python {PROJECT_SCRIPTS}/load_to_azure_sql.py",
    )

    merge >> dedup >> skills >> match >> upload >> load_sql