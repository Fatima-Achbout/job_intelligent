from airflow.decorators import dag, task
from datetime import datetime

@dag(
    schedule=None,
    start_date=datetime(2024, 6, 1),
    catchup=False
)
def taskflow_example():

    @task()
    def extract():
        return "Données extraites"

    @task()
    def transform(data):
        return f"Transformation de : {data}"

    @task()
    def load(data):
        print(f"Chargement : {data}")

    data = extract()
    transformed_data = transform(data)
    load(transformed_data)

taskflow_example()