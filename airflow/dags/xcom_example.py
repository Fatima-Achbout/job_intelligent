from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

def push_data(ti):
    ti.xcom_push(key="my_key", value="Airflow XCom Test")

def pull_data(ti):
    value = ti.xcom_pull(key="my_key", task_ids="push_task")
    print(f"Valeur XCom : {value}")

with DAG(
    dag_id="xcom_example",
    start_date=datetime(2024, 6, 1),
    schedule=None,
    catchup=False
) as dag:

    push_task = PythonOperator(
        task_id="push_task",
        python_callable=push_data
    )

    pull_task = PythonOperator(
        task_id="pull_task",
        python_callable=pull_data
    )

    push_task >> pull_task