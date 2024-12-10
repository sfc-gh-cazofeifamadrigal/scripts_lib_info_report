import pandas as pd
import os

def merge_csv_files(directory):
    dataframes = []
    
    for filename in os.listdir(directory):
        if filename.endswith(".csv"):
            filepath = os.path.join(directory, filename)
            df = pd.read_csv(filepath)
            dataframes.append(df)
    
    merged_df = pd.concat(dataframes, ignore_index=True)
    
    merged_df.to_csv('merged_output_merged.csv', index=False)
    print("DONE => 'merged_output_merged.csv'")

if __name__ == "__main__":
    directory = "/Users/cazofeifamadrigal/Documents/python-scripts/snyk_sma/sma" 
    merge_csv_files(directory)