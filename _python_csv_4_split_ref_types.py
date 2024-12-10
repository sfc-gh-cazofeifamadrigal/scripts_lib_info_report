import pandas as pd

def split_csv_by_type(input_file, output_file_nuget, output_file_npm):
    df = pd.read_csv(input_file)
    
    df_nuget = df[df['type'] == 'nuget']
    df_npm = df[df['type'] == 'npm']
    
    df_nuget.to_csv(output_file_nuget, index=False)
    df_npm.to_csv(output_file_npm, index=False)
    
    print(f"DONE => '{output_file_nuget}'")
    print(f"DONE => '{output_file_npm}'")

if __name__ == "__main__":
    input_file = 'filtered_output.csv'
    output_file_nuget = 'filtered_output_nuget.csv'
    output_file_npm = 'filtered_output_npm.csv'
    
    split_csv_by_type(input_file, output_file_nuget, output_file_npm)