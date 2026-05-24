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

mysql_url = "mysql+pymysql://root:rootpassword@host.docker.internal:3307/airflow_db"

csv_input = "/opt/airflow/dags/customer_data.csv"
csv_temp = "/tmp/customer_data_extracted.csv"
mysql_temp = "/tmp/orders_data_extracted.csv"
merged_temp = "/tmp/merged_data.csv"

def extract_csv_data():
    df = pd.read_csv(csv_input)
    print("Données CSV extraites :")
    print(df)
    df.to_csv(csv_temp, index=False)

def extract_mysql_data():
    engine = create_engine(mysql_url)
    query = "SELECT customer_id, order_id, amount FROM orders"
    df = pd.read_sql(query, engine)
    print("Données MySQL extraites :")
    print(df)
    df.to_csv(mysql_temp, index=False)

def transform_data():
    df_csv = pd.read_csv(csv_temp)
    df_mysql = pd.read_csv(mysql_temp)

    merged_df = pd.merge(df_csv, df_mysql, on="customer_id")
    merged_df["total_amount"] = merged_df["amount"] * 1.05

    print("Données fusionnées et transformées :")
    print(merged_df)

    merged_df.to_csv(merged_temp, index=False)

def load_to_mysql():
    engine = create_engine(mysql_url)
    df = pd.read_csv(merged_temp)
    df.to_sql("customer_orders_summary", engine, if_exists="replace", index=False)
    print("Résultats insérés dans la table customer_orders_summary")

with DAG(
    dag_id="merge_csv_mysql_pipeline",
    default_args=default_args,
    description="Fusionner CSV et MySQL puis sauvegarder dans MySQL",
    start_date=datetime(2024, 6, 1),
    schedule=None,
    catchup=False,
) as dag:

    task1 = PythonOperator(
        task_id="extract_csv_data",
        python_callable=extract_csv_data
    )

    task2 = PythonOperator(
        task_id="extract_mysql_data",
        python_callable=extract_mysql_data
    )

    task3 = PythonOperator(
        task_id="transform_data",
        python_callable=transform_data
    )

    task4 = PythonOperator(
        task_id="load_to_mysql",
        python_callable=load_to_mysql
    )

    task1 >> task2 >> task3 >> task4