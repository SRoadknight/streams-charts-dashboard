# src/utils/database_utils.py

import os
import duckdb
from dotenv import load_dotenv
from utils.file_utils import save_to_csv, load_data_from_csv
import pandas as pd

load_dotenv()

def initialise_connection():
    """Initialise a connection to the database."""
    if not os.environ.get("MOTHERDUCK_TOKEN"):
        raise ValueError("MotherDuck token not found")
    conn = duckdb.connect(database='md:')
    try:
        conn.execute(f"USE {os.environ.get('DATABASE_NAME')}")
    except duckdb.Error as e:
        raise RuntimeError(f"Failed to initialise MotherDuck database connection: {e}")
    return conn

def fetch_data_from_db(year, week_number):
    """Fetch data from the database for a specific year and week number."""
    conn = initialise_connection()
    cursor = conn.execute(f"SELECT * FROM channel_stats WHERE year = {year} and week_number = {week_number}")
    data = cursor.fetchall()
    column_names = [column[0] for column in cursor.description]
    return data, column_names

def fetch_weekly_data(year, week_number, overwrite=False):
    """Fetch weekly data, loading from CSV if available, otherwise querying the database."""
    file_path = f"../data/{year}/{week_number}/{year}{week_number}.csv"
    if not overwrite:
        df = load_data_from_csv(file_path)
        if df is not None:
            return df  # Return the DataFrame if loaded successfully

    print(f"Loading data from MotherDuck")
    data, column_names = fetch_data_from_db(year, week_number)
    
    if not data:
        print(f"No data found for year {year} and week {week_number}.")
        return None  # Return None if no data is found

    df = pd.DataFrame(data, columns=column_names)
    
    save_to_csv(file_path, df)
    
    return df