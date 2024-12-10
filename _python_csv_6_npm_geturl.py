import requests
import pandas as pd
import time
from tqdm import tqdm
import subprocess
import json

df = pd.read_csv("filtered_output_npm_sorted.csv")


def get_github_license_url(package_name, session):
    def query_npm_api(pkg_name):
        npm_api_url = f"https://registry.npmjs.org/{pkg_name.replace('/', '%2F')}"
        return session.get(npm_api_url)

    def extract_repository_url(data):
        repository_info = data.get("repository", {})
        if isinstance(repository_info, dict):
            repository_url = repository_info.get("url", "")
        elif isinstance(repository_info, str):
            repository_url = repository_info
        else:
            repository_url = ""

        if repository_url.startswith("git+"):
            repository_url = repository_url[4:]
        if repository_url.startswith("git://"):
            repository_url = repository_url.replace("git://", "https://")
        if repository_url.startswith("github:"):
            repository_url = repository_url.replace("github:", "https://github.com/")
        if repository_url.endswith(".git"):
            repository_url = repository_url[:-4]
        return repository_url

    try:
        if "azure" in package_name and "/" in package_name:
            package_name = package_name.split("/")[0]

        response = query_npm_api(package_name)
        if response.status_code == 200:
            data = response.json()
            repository_url = extract_repository_url(data)
            if repository_url:
                license_url = find_license_url(repository_url, session)

                if license_url:
                    return license_url

        if not package_name.startswith("@"):
            scoped_package_name = f"@{package_name}"
            print(f"Retrying with scoped name: {scoped_package_name}")
            response = query_npm_api(scoped_package_name)
            if response.status_code == 200:
                data = response.json()
                repository_url = extract_repository_url(data)
                if repository_url:
                    license_url = find_license_url(repository_url, session)

                    if license_url:
                        return license_url

        print(f"No repository URL found for package: {package_name}")
        return ""
    except Exception as e:
        print(f"Error processing package {package_name}: {e}")
        return ""


def find_license_url(repository_url, session):
    branches = ["master", "main"]
    license_files = [
        "LICENSE.md",
        "LICENSE",
        "LICENSE.txt",
        "LICENSE-MIT",
        "LICENSE-APACHE",
        "license.md",
        "license",
        "license.txt",
        "license-mit",
        "license-apache",
    ]

    for branch in branches:
        for license_file in license_files:
            license_url = f"{repository_url}/blob/{branch}/{license_file}"
            license_response = session.get(license_url)
            if license_response.status_code == 200:
                return license_url
            else:
                print(
                    f"License file not found at: {license_url} (status code: {license_response.status_code})"
                )

    # If not found in predefined paths, try to list the repository contents recursively
    repo_api_url = repository_url.replace("github.com", "api.github.com/repos")
    license_url = find_license_recursively(repo_api_url, session, depth=0)
    if license_url:
        return license_url
    return ""


def find_license_recursively(repo_api_url, session, depth):
    if depth > 5:
        return ""

    contents_url = f"{repo_api_url}/contents"
    response = session.get(contents_url)
    if response.status_code == 200:
        contents = response.json()
        for item in contents:
            if item["type"] == "file" and "LICENSE" in item["name"].upper():
                return item["html_url"]
            elif item["type"] == "dir":
                subdir_url = f"{repo_api_url}/contents/{item['path']}"
                license_url = find_license_recursively(subdir_url, session, depth + 1)
                if license_url:
                    return license_url
    return ""


def find_license_url_by_npm_view(package_name, session):
    try:
        result = subprocess.run(
            ["npm", "view", package_name, "--json"], capture_output=True, text=True
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            homepage_url = data.get("homepage", "")
            repository_url = (
                data.get("repository", {}).get("url", "")
                if isinstance(data.get("repository", {}), dict)
                else data.get("repository", "")
            )

            if homepage_url:
                if homepage_url.startswith("git+"):
                    homepage_url = homepage_url[4:]
                if homepage_url.startswith("git://"):
                    homepage_url = homepage_url.replace("git://", "https://")
                if homepage_url.startswith("github:"):
                    homepage_url = homepage_url.replace(
                        "github:", "https://github.com/"
                    )
                if homepage_url.endswith(".git"):
                    homepage_url = homepage_url[:-4]
                return find_license_url(homepage_url, session)

            if repository_url:
                if repository_url.startswith("git+"):
                    repository_url = repository_url[4:]
                if repository_url.startswith("git://"):
                    repository_url = repository_url.replace("git://", "https://")
                if repository_url.startswith("github:"):
                    repository_url = repository_url.replace(
                        "github:", "https://github.com/"
                    )
                if repository_url.endswith(".git"):
                    repository_url = repository_url[:-4]
                return find_license_url(repository_url, session)

        print(f"No homepage or repository URL found for package: {package_name}")
        return ""
    except Exception as e:
        print(f"Error processing npm view for package {package_name}: {e}")
        return ""


urls = []
with requests.Session() as session:
    for package in tqdm(df["name"], desc="Processing packages"):
        url = get_github_license_url(package, session)
        if not url:
            url = find_license_url_by_npm_view(package, session)
        if url:
            print(f"Package: {package}, License URL: {url} ✅")
        else:
            print(f"Package: {package}, License URL: Not found ❌")
        urls.append(url)
        time.sleep(1)

df["license urls"] = urls

df.to_csv("updated_filtered_output_npm.csv", index=False)
