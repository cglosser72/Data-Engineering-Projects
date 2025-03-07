# Weather ETL Pipeline with Airflow & PostgreSQL

This project builds an **ETL pipeline** using **OpenWeather API, PostgreSQL, and Apache Airflow**. The pipeline:
- **Extracts** weather data from OpenWeather API.
- **Transforms** it into a structured format.
- **Loads** it into a PostgreSQL database.
- Runs on a **schedule** using Apache Airflow.

## 🚀 Setup Instructions

### **1️⃣ Create Project Structure**
Run the following commands to set up your directories:
```bash
mkdir weather_etl && cd weather_etl
mkdir dags scripts db
touch docker-compose.yml requirements.txt .env
```
- `dags/` → Airflow DAGs  
- `scripts/` → Python scripts (API extraction)  
- `db/` → SQL transformation scripts  
- `.env` → Stores API keys & DB credentials  

---

### **2️⃣ Get OpenWeather API Key**
1. Sign up at [OpenWeather](https://home.openweathermap.org/users/sign_up).
2. Go to **API Keys** and copy your key.
3. Add it to `.env`:
   ```bash
   OPENWEATHER_API_KEY=your_actual_api_key
   ```

---

### **3️⃣ Write the Weather Extraction Script**
Create `scripts/extract_weather.py`:
```python
import requests
import os
import json
import psycopg2
from dotenv import load_dotenv

# Load API Key from .env
load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")
CITY = "Chicago,US"
URL = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"

# PostgreSQL connection details
DB_PARAMS = {
    "dbname": "weather_db",
    "user": "airflow",
    "password": "airflow",
    "host": "localhost",
    "port": "5432",
}

def get_weather_data():
    response = requests.get(URL)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching data: {response.status_code}")
        return None

def store_data(data):
    if not data:
        return
    
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS weather (
            id SERIAL PRIMARY KEY,
            city TEXT,
            temperature FLOAT,
            humidity INT,
            weather TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cur.execute("""
        INSERT INTO weather (city, temperature, humidity, weather)
        VALUES (%s, %s, %s, %s)
    """, (CITY, data['main']['temp'], data['main']['humidity'], data['weather'][0]['description']))

    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    weather_data = get_weather_data()
    store_data(weather_data)
```

---

### **4️⃣ Set Up PostgreSQL & Airflow with Docker**
Create `docker-compose.yml`:
```yaml
version: '3'
services:
  postgres:
    image: postgres:latest
    container_name: postgres_db
    restart: always
    environment:
      POSTGRES_USER: airflow
      POSTGRES_PASSWORD: airflow
      POSTGRES_DB: weather_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  airflow:
    image: apache/airflow:latest
    container_name: airflow
    restart: always
    depends_on:
      - postgres
    environment:
      - AIRFLOW__CORE__EXECUTOR=LocalExecutor
      - AIRFLOW__CORE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres:5432/weather_db
    ports:
      - "8080:8080"
    volumes:
      - ./dags:/opt/airflow/dags
      - ./scripts:/opt/airflow/scripts
      - ./db:/opt/airflow/db

volumes:
  postgres_data:
```

Start the services:
```bash
docker-compose up -d
```
- PostgreSQL will run on **port 5432**.
- Airflow UI will be available at **http://localhost:8080**.

---

### **5️⃣ Create an Airflow DAG**
Create `dags/weather_etl.py`:
```python
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
```

---

### **6️⃣ Deploy & Test**
#### **Restart Docker Services**
```bash
docker-compose down && docker-compose up -d
```

#### **Initialize Airflow**
```bash
docker exec -it airflow airflow db init
docker exec -it airflow airflow users create --username admin --password admin --role Admin --email admin@example.com
docker exec -it airflow airflow scheduler &
docker exec -it airflow airflow webserver &
```
- **Access Airflow UI:** [http://localhost:8080](http://localhost:8080)  
  - **Username:** `admin`
  - **Password:** `admin`
- **Activate the `weather_etl` DAG** in Airflow.

#### **Verify Data in PostgreSQL**
```bash
docker exec -it postgres_db psql -U airflow -d weather_db -c "SELECT * FROM weather;"
```

---

## ✅ **Next Steps**
- Fetch weather data for multiple cities.
- Store historical data for analysis.
- Add logging and error handling.
- Create a visualization dashboard.

---

### 📌 **Project Overview**
| Component    | Technology  |
|-------------|------------|
| Data Source | OpenWeather API |
| Database    | PostgreSQL |
| Orchestration | Apache Airflow |
| Containerization | Docker |
| Language | Python |

🚀 **Happy Coding!** Let me know if you need help setting up! 🎯
