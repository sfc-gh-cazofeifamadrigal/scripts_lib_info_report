"""
Data processors for dependency report generation
"""
import pandas as pd
import requests
from bs4 import BeautifulSoup
import subprocess
import json
from pathlib import Path
from typing import List

from config import (
    LICENSE_FILES,
    GITHUB_BRANCHES,
    MAX_RECURSION_DEPTH,
    KNOWN_LICENSE_URLS
)


class CSVProcessor:
    """Handles CSV data processing operations"""
    
    @staticmethod
    def remove_columns(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """Remove specified columns from DataFrame"""
        existing_columns = [col for col in columns if col in df.columns]
        return df.drop(columns=existing_columns)
    
    @staticmethod
    def merge_csv_files(directory: Path) -> pd.DataFrame:
        """Merge all CSV files in a directory"""
        dataframes = []
        for csv_file in directory.glob("*.csv"):
            df = pd.read_csv(csv_file)
            dataframes.append(df)
        
        if not dataframes:
            raise ValueError(f"No CSV files found in {directory}")
        
        return pd.concat(dataframes, ignore_index=True)
    
    @staticmethod
    def remove_duplicates_keep_highest_version(df: pd.DataFrame) -> pd.DataFrame:
        """Remove duplicates, keeping the entry with highest version"""
        df = df.sort_values(by='version', ascending=False)
        return df.drop_duplicates(subset=['name'], keep='first')
    
    @staticmethod
    def filter_by_prefixes(df: pd.DataFrame, prefixes: List[str]) -> pd.DataFrame:
        """Remove rows where name starts with any of the given prefixes"""
        mask = ~df['name'].str.startswith(tuple(prefixes))
        return df[mask]
    
    @staticmethod
    def split_by_type(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Split DataFrame into nuget and npm packages"""
        df_nuget = df[df['type'] == 'nuget'].copy()
        df_npm = df[df['type'] == 'npm'].copy()
        return df_nuget, df_npm


class LicenseURLFinder:
    """Finds license URLs for packages"""
    
    def __init__(self, session: requests.Session):
        self.session = session
    
    def get_nuget_license_url(self, package_name: str) -> str:
        """Get license URL for a NuGet package"""
        # Check known URLs first
        if package_name in KNOWN_LICENSE_URLS:
            return KNOWN_LICENSE_URLS[package_name]
        
        try:
            response = self.session.get(f'https://www.nuget.org/packages/{package_name}')
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            repository_link = soup.find('a', {'href': True, 'title': 'View the source code for this package'})
            
            if repository_link and 'github.com' in repository_link['href']:
                repository_url = repository_link['href'].rstrip('.git')
                return self._find_github_license(repository_url)
            
            return ''
        except requests.RequestException as e:
            print(f"Error fetching data for {package_name}: {e}")
            return ''
    
    def get_npm_license_url(self, package_name: str) -> str:
        """Get license URL for an NPM package"""
        # Check known URLs first
        if package_name in KNOWN_LICENSE_URLS:
            return KNOWN_LICENSE_URLS[package_name]
        
        try:
            # Handle Azure packages
            if "azure" in package_name and "/" in package_name:
                package_name = package_name.split("/")[0]
            
            # Try NPM registry API
            npm_api_url = f"https://registry.npmjs.org/{package_name.replace('/', '%2F')}"
            response = self.session.get(npm_api_url)
            
            if response.status_code == 200:
                data = response.json()
                repository_url = self._extract_repository_url(data)
                if repository_url:
                    license_url = self._find_github_license(repository_url)
                    if license_url:
                        return license_url
            
            # Try with scoped name
            if not package_name.startswith("@"):
                scoped_package_name = f"@{package_name}"
                response = self.session.get(f"https://registry.npmjs.org/{scoped_package_name}")
                if response.status_code == 200:
                    data = response.json()
                    repository_url = self._extract_repository_url(data)
                    if repository_url:
                        license_url = self._find_github_license(repository_url)
                        if license_url:
                            return license_url
            
            # Try npm view command as fallback
            return self._get_license_from_npm_view(package_name)
            
        except Exception as e:
            print(f"Error processing package {package_name}: {e}")
            return ""
    
    def _extract_repository_url(self, data: dict) -> str:
        """Extract repository URL from NPM package data"""
        repository_info = data.get("repository", {})
        
        if isinstance(repository_info, dict):
            repository_url = repository_info.get("url", "")
        elif isinstance(repository_info, str):
            repository_url = repository_info
        else:
            return ""
        
        # Normalize URL
        repository_url = repository_url.removeprefix("git+")
        repository_url = repository_url.replace("git://", "https://")
        repository_url = repository_url.replace("github:", "https://github.com/")
        repository_url = repository_url.rstrip(".git")
        
        return repository_url
    
    def _find_github_license(self, repository_url: str) -> str:
        """Find license file in GitHub repository"""
        for branch in GITHUB_BRANCHES:
            for license_file in LICENSE_FILES:
                license_url = f"{repository_url}/blob/{branch}/{license_file}"
                response = self.session.get(license_url)
                if response.status_code == 200:
                    return license_url
        
        # Try recursive search via GitHub API
        repo_api_url = repository_url.replace("github.com", "api.github.com/repos")
        return self._find_license_recursively(repo_api_url, depth=0)
    
    def _find_license_recursively(self, repo_api_url: str, depth: int) -> str:
        """Recursively search for license in repository"""
        if depth > MAX_RECURSION_DEPTH:
            return ""
        
        contents_url = f"{repo_api_url}/contents"
        response = self.session.get(contents_url)
        
        if response.status_code == 200:
            contents = response.json()
            for item in contents:
                if item["type"] == "file" and "LICENSE" in item["name"].upper():
                    return item["html_url"]
                elif item["type"] == "dir":
                    subdir_url = f"{repo_api_url}/contents/{item['path']}"
                    license_url = self._find_license_recursively(subdir_url, depth + 1)
                    if license_url:
                        return license_url
        return ""
    
    def _get_license_from_npm_view(self, package_name: str) -> str:
        """Get license URL using npm view command"""
        try:
            result = subprocess.run(
                ["npm", "view", package_name, "--json"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                
                # Try homepage first
                homepage_url = data.get("homepage", "")
                if homepage_url:
                    normalized_url = self._normalize_repo_url(homepage_url)
                    license_url = self._find_github_license(normalized_url)
                    if license_url:
                        return license_url
                
                # Try repository URL
                repository_info = data.get("repository", {})
                repository_url = (
                    repository_info.get("url", "")
                    if isinstance(repository_info, dict)
                    else repository_info
                )
                
                if repository_url:
                    normalized_url = self._normalize_repo_url(repository_url)
                    return self._find_github_license(normalized_url)
            
            return ""
        except Exception as e:
            print(f"Error processing npm view for package {package_name}: {e}")
            return ""
    
    def _normalize_repo_url(self, url: str) -> str:
        """Normalize repository URL"""
        url = url.removeprefix("git+")
        url = url.replace("git://", "https://")
        url = url.replace("github:", "https://github.com/")
        url = url.rstrip(".git")
        return url


class ExportProcessor:
    """Handles export operations"""
    
    @staticmethod
    def to_excel(df: pd.DataFrame, output_path: Path):
        """Export DataFrame to Excel"""
        df.to_excel(output_path, index=False)
    
    @staticmethod
    def to_markdown(df: pd.DataFrame, output_path: Path):
        """Export DataFrame to Markdown table"""
        with open(output_path, 'w') as f:
            # Write header
            f.write("| " + " | ".join(df.columns) + " |\n")
            f.write("|" + "---|" * len(df.columns) + "\n")
            
            # Write rows
            for _, row in df.iterrows():
                f.write("| " + " | ".join(str(val) for val in row) + " |\n")
    
    @staticmethod
    def to_markdown_combined(df_nuget: pd.DataFrame, df_npm: pd.DataFrame, output_path: Path, title: str = "Open Source Libraries"):
        """
        Export combined NuGet and NPM DataFrames to a formatted Markdown file
        similar to the expected format with YAML frontmatter and sections
        """
        with open(output_path, 'w') as f:
            # Write YAML frontmatter
            f.write("---\n")
            # Extract product name without " - Open Source Libraries" suffix for description
            product_name = title.replace(" - Open Source Libraries", "")
            f.write(f"description: 'The open-source libraries used in the Snowflake {product_name} include:'\n")
            f.write("---\n\n")
            
            # Write main title
            f.write(f"# {title}\n\n")
            
            # Write RST include block
            f.write("```{eval-rst}\n")
            f.write(".. include:: /INCLUDE/migrations/sc-legal-sidebar.txt\n")
            f.write("```\n\n")
            
            # Write .NET section
            if not df_nuget.empty:
                f.write("## .NET Open Source Libraries\n\n")
                ExportProcessor._write_markdown_table(f, df_nuget)
                f.write("\n")
            
            # Write Node section
            if not df_npm.empty:
                f.write("## Node Open Source Libraries\n\n")
                ExportProcessor._write_markdown_table(f, df_npm)
    
    @staticmethod
    def _write_markdown_table(f, df: pd.DataFrame):
        """Write a markdown table with license URLs formatted as markdown links"""
        # Sort by name
        df = df.sort_values(by='name')
        
        # Define columns to show
        columns = ['name', 'version', 'type', 'licenses', 'license urls']
        
        # Write header
        f.write("| " + " | ".join(columns) + " |\n")
        f.write("| " + " | ".join(["-" * len(col) for col in columns]) + " |\n")
        
        # Write rows
        for _, row in df.iterrows():
            cells = []
            for col in columns:
                value = row.get(col, '')
                
                # Format license URLs as markdown links or mark for review
                if col == 'license urls':
                    if value and not pd.isna(value) and str(value).strip():
                        value = f"[{value}]({value})"
                    else:
                        value = '[REVIEW URL]'
                
                # Handle empty values
                if pd.isna(value) or value == '':
                    value = ''
                
                cells.append(str(value))
            
            f.write("| " + " | ".join(cells) + " |\n")
