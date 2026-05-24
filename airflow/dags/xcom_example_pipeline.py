from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime, timedelta
import pandas as pd

default_args = {
    "owner": "airflow",
    "retries": 2,
    "retry_delay": timedelta(minutes=1),
}

# Tâche 1 : lire le CSV, calculer la somme, envoyer via XCom
def extract_sum(**context):
    df = pd.read_csv("/opt/airflow/dags/values_data.csv")
    total = df["column1"].sum()
    context["ti"].xcom_push(key="total_sum", value=int(total))
    print(f"Somme extraite : {total}")

# Tâche 2 : récupérer la somme depuis XCom et l'afficher
def display_sum(**context):
    total = context["ti"].xcom_pull(task_ids="extract_sum_task", key="total_sum")
    print(f"Somme transmise via XCom : {total}")

with DAG(
    dag_id="xcom_example_pipeline_corrected",
    default_args=default_args,
    description="Pipeline XCom avec extraction et affichage",
    schedule=None,
    start_date=datetime(2024, 6, 1),
    catchup=False,
) as dag:

    extract_task = PythonOperator(
        task_id="extract_sum_task",
        python_callable=extract_sum,
    )

    display_task = PythonOperator(
        task_id="display_sum_task",
        python_callable=display_sum,
    )

    extract_task >> display_task