
import pandas as pd


def read_customer_language(source_file_path) :
    try:
        df = pd.read_csv(source_file_path)
        return df
    except Exception as e:
        print(f"An error occurred while reading the CSV file: {str(e)}")
        return None
