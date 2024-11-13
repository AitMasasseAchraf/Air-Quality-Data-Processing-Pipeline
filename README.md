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
