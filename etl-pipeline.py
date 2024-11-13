from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from airflow.utils.dates import days_ago
import pandas as pd
import requests
import time
import json
import mysql.connector
from mysql.connector import Error

# Define default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': time.timedelta(minutes=5),
}

# Define the DAG
dag = DAG(
    'data_processing_pipeline',
    default_args=default_args,
    description='A DAG to process and load data from an API',
    schedule_interval='@daily',  # Set to run daily
    start_date=days_ago(1),
)

def read_data():
    """
    Read and preprocess data from a CSV file.
    """
    file_path = "C:/Users/aitma/Downloads/simplemaps_worldcities_basicv1.77/worldcities.csv"  # Ensure this path is correct
    cities = pd.read_csv(file_path)
    cities = cities[cities['country'] == 'Morocco']
    cities = cities[['city', 'lat', 'lng', 'admin_name']]
    cities.to_csv('/path/to/dag/cities.csv', index=False)
    return 'cities.csv'

def fetch_data_with_error_handling(api_url, headers, params, retries=3, backoff_factor=2):
    """
    Fetch data from an API with error handling for rate limits, timeouts, and missing data.
    """
    for i in range(retries):
        try:
            response = requests.get(api_url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            if not data or 'error' in data:
                print("Warning: Data is missing or incomplete.")
                return None
            return data
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            if response.status_code == 429:
                print("Rate limit exceeded. Retrying after backoff...")
                time.sleep(backoff_factor ** i)
                continue
            time.sleep(backoff_factor ** i)
    return None

def fetch_api_data(**kwargs):
    """
    Fetch data from the API for each city and save to a JSON file.
    """
    cities = pd.read_csv('/path/to/dag/cities.csv')
    url = "https://api.meersens.com/environment/public/air/current"
    headers = {'apikey': 'jYxv9Yb5x1pTicfLRSwK29KaNPX1OAUl'}
    json_data = []
    for _, row in cities.iterrows():
        params = {"lat": row['lat'], "lng": row['lng']}
        data = fetch_data_with_error_handling(url, headers, params)
        if data:
            json_data.append(data)
    with open('data.json', 'w') as file:
        json.dump(json_data, file, indent=4)

def process_and_clean_data(**kwargs):
    """
    Process and clean the JSON data.
    """
    with open('data.json', 'r') as file:
        data = json.load(file)

    def remove_keys(data, keys_to_remove):
        if isinstance(data, dict):
            return {key: remove_keys(value, keys_to_remove) for key, value in data.items() if key not in keys_to_remove}
        elif isinstance(data, list):
            return [remove_keys(item, keys_to_remove) for item in data]
        else:
            return data

    keys_to_remove = ["found", "datetime", "icon", "color", "description"]
    cleaned_data = remove_keys(data, keys_to_remove)

    with open('data_cleaned.json', 'w') as file:
        json.dump(cleaned_data, file, indent=4)

def transform_and_load_data(**kwargs):
    """
    Transform the cleaned data and load it into MySQL.
    """
    cleaned_data = json.load(open('data_cleaned.json'))

    cities_df = pd.read_csv('cities.csv')
    indexes_data = []
    pollutants_data = []

    def transform_data(city_data):
        index_table = {
            "index_type": city_data['index']['index_type'],
            "index_name": city_data['index']['index_name'],
            "index_qualification": city_data['index']['qualification'],
            "index_value": city_data['index']['value']
        }
        indexes_data.append(index_table)

        for key, pollutant in city_data['pollutants'].items():
            pollutant_row = {
                "shortcode": pollutant['shortcode'],
                "name": pollutant['name'],
                "unit": pollutant['unit'],
                "value": pollutant['value'],
                "confidence": pollutant['confidence'],
                "index_qualification": pollutant['index']['qualification'],
                "index_value": pollutant['index']['value']
            }
            pollutants_data.append(pollutant_row)

    for city_data in cleaned_data:
        transform_data(city_data)

    index_df = pd.DataFrame(indexes_data)
    pollutants_df = pd.DataFrame(pollutants_data)

    index_df.reset_index(drop=True, inplace=True)
    cities_df.reset_index(drop=True, inplace=True)
    pollutants_df['city'] = cities_df['city'].repeat(len(pollutants_df) // len(cities_df)).reset_index(drop=True)

    def fill_nulls(df):
        if 'city' in df.columns:
            df = df.dropna(subset=['city'])
        for column in df.columns:
            if pd.api.types.is_numeric_dtype(df[column]):
                df[column].fillna(df[column].median(), inplace=True)
            elif pd.api.types.is_categorical_dtype(df[column]) or pd.api.types.is_object_dtype(df[column]):
                df[column].fillna(df[column].mode()[0], inplace=True)
        return df

    index_df = fill_nulls(index_df)
    pollutants_df = fill_nulls(pollutants_df)
    cities_df = fill_nulls(cities_df)

    cities_df['city_id'] = range(1, len(cities_df) + 1)
    city_id_map = dict(zip(cities_df['city'], cities_df['city_id']))

    index_df['city_id'] = index_df['city'].map(city_id_map)
    index_df.drop('city', axis=1, inplace=True)

    pollutants_df['city_id'] = pollutants_df['city'].map(city_id_map)
    pollutants_df.drop('city', axis=1, inplace=True)

    cities_df.to_csv('cities.csv', index=False)
    index_df.to_csv('index_df.csv', index=False)
    pollutants_df.to_csv('pollutants_df.csv', index=False)

    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Qwerty1234/',
            database='new_schema'
        )
        cursor = conn.cursor()

        cursor.execute("ALTER TABLE cities AUTO_INCREMENT = 1")

        insert_cities_query = """
        INSERT INTO cities (city, lat, lng, admin_name)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE lat=VALUES(lat), lng=VALUES(lng), admin_name=VALUES(admin_name)
        """
        for _, row in cities_df.iterrows():
            cursor.execute(insert_cities_query, (row['city'], row['lat'], row['lng'], row['admin_name']))

        cursor.execute("SELECT city, city_id FROM cities")
        city_id_map = dict(cursor.fetchall())

        insert_index_query = """
        INSERT INTO index_table (index_type, index_name, index_qualification, index_value, city_id)
        VALUES (%s, %s, %s, %s, %s)
        """
        index_data = [(row['index_type'], row['index_name'], row['index_qualification'], row['index_value'], city_id_map.get(row['city'])) for _, row in index_df.iterrows()]
        cursor.executemany(insert_index_query, index_data)

        insert_pollutants_query = """
        INSERT INTO pollutants (shortcode, name, unit, value, confidence, index_qualification, index_value, city_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        pollutants_data = [(row['shortcode'], row['name'], row['unit'], row['value'], row['confidence'], row['index_qualification'], row['index_value'], city_id_map.get(row['city'])) for _, row in pollutants_df.iterrows()]
        cursor.executemany(insert_pollutants_query, pollutants_data)

        conn.commit()
    except Error as e:
        print(f"Error: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Define tasks
start_task = DummyOperator(task_id='start', dag=dag)
read_data_task = PythonOperator(task_id='read_data', python_callable=read_data, dag=dag)
fetch_data_task = PythonOperator(task_id='fetch_data', python_callable=fetch_api_data, dag=dag)
process_data_task = PythonOperator(task_id='process_data', python_callable=process_and_clean_data, dag=dag)
transform_and_load_task = PythonOperator(task_id='transform_and_load', python_callable=transform_and_load_data, dag=dag)
end_task = DummyOperator(task_id='end', dag=dag)

# Define task dependencies
start_task >> read_data_task >> fetch_data_task >> process_data_task >> transform_and_load_task >> end_task