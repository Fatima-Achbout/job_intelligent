from airflow import DAG
from airflow.operators.python import BranchPythonOperator
from airflow.operators.empty import EmptyOperator
from datetime import datetime

def choose_task():
    return "task_A" if datetime.now().hour < 12 else "task_B"

with DAG(
    dag_id="branching_example",
    start_date=datetime(2024, 6, 1),
    schedule=None,   
    catchup=False
) as dag:

    branch_task = BranchPythonOperator(
        task_id="branch_task",
        python_callable=choose_task
    )

    task_A = EmptyOperator(task_id="task_A")
    task_B = EmptyOperator(task_id="task_B")

    branch_task >> [task_A, task_B]
    