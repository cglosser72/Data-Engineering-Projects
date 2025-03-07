from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import subprocess

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 3, 1),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG(
    "weather_etl",
    default_args=default_args,
    schedule_interval="0 * * * *",  # Every hour
    catchup=False
)

def run_script():
    subprocess.run(["python", "/opt/airflow/scripts/extract_weather.py"], check=True)

extract_task = PythonOperator(
    task_id="extract_weather",
    python_callable=run_script,
    dag=dag,
)

extract_task
