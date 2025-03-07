import requests
import os
import json
import psycopg2
from dotenv import load_dotenv
from airflow.models import Variable
API_KEY = os.getenv("OPENWEATHER_API_KEY")

# Load API Key from .env
load_dotenv()
#API_KEY = os.getenv("OPENWEATHER_API_KEY")
CITY = "Chicago,US"
URL = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"

# PostgreSQL connection details
DB_PARAMS = {
    "dbname": "weather_db",
    "user": "airflow",
    "password": "airflow",
    "host": "postgres_db",
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
