import requests
import pandas as pd
from bs4 import BeautifulSoup
import time

df = pd.read_csv('filtered_output_nuget.csv')

def get_github_license_url(package_name):
    try:
        response = requests.get(f'https://www.nuget.org/packages/{package_name}')
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        repository_link = soup.find('a', {'href': True, 'title': 'View the source code for this package'})
        if repository_link and 'github.com' in repository_link['href']:
            repository_url = repository_link['href']
            if repository_url.endswith('.git'):
                repository_url = repository_url[:-4]
            
            license_urls = [
                f"{repository_url}/blob/master/LICENSE",
                f"{repository_url}/blob/main/LICENSE",
                f"{repository_url}/blob/master/LICENSE.TXT",
                f"{repository_url}/blob/main/LICENSE.TXT",
                f"{repository_url}/blob/main/LICENSE.txt",
                f"{repository_url}/blob/master/LICENSE.txt",
            ]

            for license_url in license_urls:
                license_response = requests.get(license_url)
                if license_response.status_code == 200:
                    return license_url
        return ''
    except requests.RequestException as e:
        print(f"Error fetching data for {package_name}: {e}")
        return ''

urls = []
for package in df['name']:
    url = get_github_license_url(package)
    print(f"Package: {package}, License URL: {url}")
    urls.append(url)
    time.sleep(2) 

df['license urls'] = urls

df.to_csv('updated_filtered_output_nuget.csv', index=False)