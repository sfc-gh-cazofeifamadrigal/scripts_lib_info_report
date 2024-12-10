import pandas as pd

file_input = "updated_filtered_output_nuget.csv"
file_output = "updated_filtered_output_nuget.xlsx"

df = pd.read_csv(file_input)
df.to_excel(file_output , index=False)
print("DONE => 'merged_output.xlsx'")

file_input = "updated_filtered_output_npm.csv"
file_output = "updated_filtered_output_npm.xlsx"

df = pd.read_csv(file_input)
df.to_excel(file_output , index=False)
print("DONE => 'merged_output.xlsx'")