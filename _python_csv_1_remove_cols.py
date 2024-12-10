import pandas as pd
import os

directory = 'sma'

for file_name in os.listdir(directory):
    if file_name.endswith('.csv'):
        file_path = os.path.join(directory, file_name)
        df = pd.read_csv(file_path)
        df.drop(columns=['id', 'issuesCritical', 'issuesHigh', 'issuesMedium', 'issuesLow', 'dependenciesWithIssues', 'projects', 'latestVersion', 'latestVersionPublishedDate', 'firstPublishedDate', 'isDeprecated'], inplace=True)
        df.to_csv(file_path, index=False)