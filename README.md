# Air-Quality-Data-Processing-Pipeline


## Project Overview
This project consists of an ETL (Extract, Transform, Load) pipeline that reads city data from a CSV file, fetches air quality data from an https://api.meersens.com/environment/public/air/current API, processes the data, and stores it into a MySQL database. The pipeline is built using Python and Airflow, allowing for automation and scheduling.

## Table of Contents
- [Project Overview](#project-overview)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Installation and Setup](#installation-and-setup)
- [Project Structure](#project-structure)
- [Usage](#usage)
- [DAG Workflow](#dag-workflow)
- [Future Enhancements](#future-enhancements)
- [License](#license)

## Features
- Reads city data from a CSV file.
- Fetches real-time air quality data using an API.
- Cleans and transforms the data, including error handling.
- Saves the cleaned data into CSV files and MySQL tables.
- Airflow DAG for scheduling and automation.

## Technologies Used
- **Python** (Pandas, Requests, JSON)
- **Apache Airflow** (DAGs, PythonOperator)
- **MySQL** (Data storage)
- **Jupyter Notebook** (Data processing and testing)

## Installation and Setup
### Prerequisites
- Python 3.x
- Apache Airflow
- MySQL Server
- Jupyter Notebook (for testing)

### Installation Steps
1. **Clone the Repository**:
    ```bash
    git clone https://github.com/your-username/air-quality-etl.git
    cd air-quality-etl
    ```

2. **Install Python Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3. **Set Up Airflow**:
    - Follow [Airflow's official installation guide](https://airflow.apache.org/docs/apache-airflow/stable/start.html).
    - Create a new DAG directory in your Airflow `dags_folder` and place the `data_processing_pipeline.py` in it.

4. **Set Up MySQL**:
    - Create a database named `new_schema` or update the `conn` settings in the Python script.

### Configuration
- Ensure the API key in the script is valid:
    ```python
    headers = {'apikey': 'your_api_key_here'}
    ```
- Update the CSV file path in the scripts to match your system's directory structure.

## Project Structure
air-quality-etl/ ├── data_processing_pipeline.py # Airflow DAG script ├── etl_script.ipynb # Jupyter Notebook with data processing code ├── cities.csv # Processed city data ├── index_df.csv # Index data ├── pollutants_df.csv # Pollutants data ├── README.md # Project documentation └── requirements.txt # Python dependencies

## Usage
1. **Run the Airflow Scheduler**:
    ```bash
    airflow scheduler
    ```

2. **Trigger the DAG**:
    - Go to the Airflow UI (`http://localhost:8080`) and manually trigger the `data_processing_pipeline` DAG.

## DAG Workflow
1. **Read City Data**: Reads city data from a CSV file.
2. **Fetch Air Quality Data**: Calls the external API to fetch data for each city.
3. **Transform Data**: Cleans, processes, and prepares data for storage.
4. **Load Data to MySQL**: Inserts the data into the MySQL database.

## Future Enhancements
- Add more data validation checks.
- Implement data visualizations.
- Integrate logging and error tracking.
- Expand the pipeline to handle other data sources and regions.


