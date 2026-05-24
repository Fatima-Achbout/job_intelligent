from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

task_names = ["task_1", "task_2", "task_3"]

with DAG(
    dag_id="dynamic_dag_example",
    start_date=datetime(2024, 6, 1),
    schedule=None,
    catchup=False
) as dag:

    for task_name in task_names:
        BashOperator(
            task_id=task_name,
            bash_command=f"echo 'Running {task_name}'"
        )