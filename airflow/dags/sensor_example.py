from airflow import DAG
from airflow.sensors.filesystem import FileSensor
from airflow.operators.empty import EmptyOperator
from datetime import datetime

with DAG(
    dag_id="sensor_example",
    start_date=datetime(2024, 6, 1),
    schedule=None,
    catchup=False
) as dag:

    wait_for_file = FileSensor(
        task_id="wait_for_file",
        filepath="/opt/airflow/dags/data_ready.txt",
        poke_interval=10,
        timeout=300
    )

    file_ready_task = EmptyOperator(task_id="file_ready")

    wait_for_file >> file_ready_task