
import pandas as pd
import argparse

def validate_url(df):
    total_rows = df.shape[0]
    rows_without_https = df[~df.apply(lambda row: 'https://' in row.to_string(), axis=1)].shape[0]

    print(f"Total number of rows: {total_rows}")
    print(f"Number of rows without 'https://': {rows_without_https}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Validate CSV file.')
    parser.add_argument('--file', type=str, required=True, help='Path to the CSV file')

    args = parser.parse_args()
    df = pd.read_csv(args.file)    
    validate_url(df)