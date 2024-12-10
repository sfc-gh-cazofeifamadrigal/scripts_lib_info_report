
import pandas as pd

def remove_duplicates_with_highest_version(file_path, output_file):
    df = pd.read_csv(file_path)
    df.sort_values(by='version', ascending=False, inplace=True)
    df.drop_duplicates(subset=['name'], keep='first', inplace=True)
    df.to_csv(output_file, index=False)
    print("DONE => 'merged_output_no_duplicated.csv'")

def sort_csv_file(input_file, output_file, sort_column):
    df = pd.read_csv(input_file)
    df_sorted = df.sort_values(by=sort_column)
    df_sorted.to_csv(output_file, index=False)
    print("DONE => 'merged_output_sorted.csv'")

def remove_specific_names(input_file, output_file):
    df = pd.read_csv(input_file)
    df_filtered = df[~df['name'].str.startswith(('Mobilize.', 'Artinsoft.', 'AMG', 'Snowflake.', 'MSTest.', 'snowconvert', 'SnowFlake.Common.', 'Microsoft.TestPlatform.', 'Microsoft.NET.Test.', 'FluentAssertions'))]
    df_filtered.to_csv(output_file, index=False)
    print("DONE => 'filtered_output.csv'")

if __name__ == "__main__":
    file_path = 'merged_output_merged.csv'
    output_file = 'merged_output_no_duplicated.csv' 

    remove_duplicates_with_highest_version(file_path, output_file)
    input_file = 'merged_output_no_duplicated.csv'
    output_file = 'merged_output_sorted.csv'
    sort_column = 'type'
    sort_csv_file(input_file, output_file, sort_column)

    input_file = 'merged_output_sorted.csv'
    output_file = 'filtered_output.csv'
    remove_specific_names(input_file, output_file)