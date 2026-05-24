from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pandas as pd

input_file = "/opt/airflow/dags/weather_data.csv"
extract_file = "/tmp/weather_extracted.csv"
transform_file = "/tmp/weather_transformed.csv"
output_file = "/tmp/weather_cleaned.csv"

default_args = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}

def extract_data():
    df = pd.read_csv(input_file)
    print("Données extraites :")
    print(df)
    df.to_csv(extract_file, index=False)

def transform_data():
    df = pd.read_csv(extract_file)

    df = df.dropna()
    df["feels_temp"] = df["temperature"] - (df["wind_speed"] * 0.1)

    print("Données transformées :")
    print(df)

    df.to_csv(transform_file, index=False)

def save_data():
    df = pd.read_csv(transform_file)
    df.to_csv(output_file, index=False)
    print("Fichier sauvegardé dans /tmp/weather_cleaned.csv")

with DAG(
    dag_id="weather_pipeline",
    default_args=default_args,
    description="Pipeline ETL météo",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
) as dag:

    extract_task = PythonOperator(
        task_id="extract_data",
        python_callable=extract_data
    )

    transform_task = PythonOperator(
        task_id="transform_data",
        python_callable=transform_data
    )

    save_task = PythonOperator(
        task_id="save_data",
        python_callable=save_data
    )

    extract_task >> transform_task >> save_task