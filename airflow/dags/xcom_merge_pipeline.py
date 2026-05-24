from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy import create_engine

default_args = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}

# connexion MySQL
mysql_url = "mysql+pymysql://root:rootpassword@mysql_db_airflow:3306/airflow_db"

def extract_csv(**context):
    df = pd.read_csv("/opt/airflow/dags/customer_data.csv")

    path = "/tmp/customers.csv"
    df.to_csv(path, index=False)

    context["ti"].xcom_push(key="csv_path", value=path)

    print("CSV extrait")
    print(df)

def extract_mysql(**context):
    engine = create_engine(mysql_url)
    df = pd.read_sql("SELECT * FROM orders", engine)

    path = "/tmp/orders.csv"
    df.to_csv(path, index=False)

    context["ti"].xcom_push(key="mysql_path", value=path)

    print("Données MySQL extraites")
    print(df)

def transform_data(**context):
    csv_path = context["ti"].xcom_pull(task_ids="extract_csv", key="csv_path")
    mysql_path = context["ti"].xcom_pull(task_ids="extract_mysql", key="mysql_path")

    print(f"Chemin CSV reçu : {csv_path}")
    print(f"Chemin MySQL reçu : {mysql_path}")

    customers = pd.read_csv(csv_path)
    orders = pd.read_csv(mysql_path)

    merged = pd.merge(customers, orders, on="customer_id")
    merged["total_amount"] = merged["amount"] * 1.05

    output_path = "/tmp/merged_data.csv"
    merged.to_csv(output_path, index=False)

    context["ti"].xcom_push(key="merged_path", value=output_path)

    print("Données fusionnées")
    print(merged)

def load_mysql(**context):
    merged_path = context["ti"].xcom_pull(task_ids="transform_data", key="merged_path")

    print(f"Chemin fusionné reçu : {merged_path}")

    engine = create_engine(mysql_url)
    df = pd.read_csv(merged_path)

    df.to_sql(
        "customer_orders_summary",
        engine,
        if_exists="replace",
        index=False
    )

    print("Données insérées dans MySQL")

with DAG(
    dag_id="xcom_merge_pipeline",
    default_args=default_args,
    start_date=datetime(2024, 6, 1),
    schedule=None,
    catchup=False,
) as dag:

    task1 = PythonOperator(
        task_id="extract_csv",
        python_callable=extract_csv
    )

    task2 = PythonOperator(
        task_id="extract_mysql",
        python_callable=extract_mysql
    )

    task3 = PythonOperator(
        task_id="transform_data",
        python_callable=transform_data
    )

    task4 = PythonOperator(
        task_id="load_mysql",
        python_callable=load_mysql
    )

    task1 >> task2 >> task3 >> task4