#!/usr/bin/env python3
"""
Fetch dependencies from Snyk REST API (v3) and export as CSV
Uses the official REST API: https://apidocs.snyk.io/
"""
import requests
import pandas as pd
import argparse
import json
from datetime import datetime

def fetch_dependencies(org_id, api_token, package_type="npm"):
    """Fetch dependencies from Snyk using REST API v3"""
    
    # Use REST API (current, stable version)
    base_url = "https://api.snyk.io/rest"
    api_version = "2024-01-04"
    headers = {
        "Authorization": f"token {api_token}",
        "Content-Type": "application/vnd.api+json"
    }
    
    all_dependencies = {}  # Use dict to deduplicate by package@version
    
    # Step 1: Get all projects using REST API
    print(f"🔍 Fetching projects for org: {org_id}")
    print(f"📦 Looking for package type: {package_type}")
    
    projects_url = f"{base_url}/orgs/{org_id}/projects?version={api_version}&limit=100"
    
    try:
        response = requests.get(projects_url, headers=headers)
        response.raise_for_status()
        projects_data = response.json()
    except requests.exceptions.HTTPError as e:
        print(f"❌ Error fetching projects: {e}")
        print(f"Response status: {response.status_code if 'response' in locals() else 'N/A'}")
        if 'response' in locals():
            print(f"Response body: {response.text[:500]}")
        return []
    
    projects = projects_data.get("data", [])
    
    # Map package types
    if package_type == "npm":
        target_types = ["npm", "yarn", "pnpm"]
    elif package_type == "nuget":
        target_types = ["nuget"]
    elif package_type == "pip":
        target_types = ["pip"]
    else:
        target_types = [package_type]
    
    # Filter projects by type
    filtered_projects = [
        p for p in projects 
        if p.get("attributes", {}).get("type") in target_types
    ]
    
    print(f"✅ Found {len(filtered_projects)} {package_type} projects (out of {len(projects)} total)")
    
    if len(filtered_projects) == 0:
        print("⚠️  No projects found for this type. Available project types:")
        type_counts = {}
        for p in projects:
            ptype = p.get("attributes", {}).get("type", "unknown")
            type_counts[ptype] = type_counts.get(ptype, 0) + 1
        
        for ptype, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"     - {ptype}: {count} projects")
        return []
    
    # Step 2: For each project, get dependencies using sbom endpoint
    for idx, project in enumerate(filtered_projects, 1):
        project_id = project.get("id")
        project_attrs = project.get("attributes", {})
        project_name = project_attrs.get("name", "Unknown")
        
        print(f"   [{idx}/{len(filtered_projects)}] Processing: {project_name}")
        
        # Use SBOM (Software Bill of Materials) endpoint to get dependencies
        sbom_url = f"{base_url}/orgs/{org_id}/projects/{project_id}/sbom?version={api_version}&format=cyclonedx1.4%2Bjson"
        
        try:
            sbom_response = requests.get(sbom_url, headers=headers)
            sbom_response.raise_for_status()
            sbom_data = sbom_response.json()
            
            # Extract components from SBOM (CycloneDX format)
            components = sbom_data.get("components", [])
            
            for component in components:
                name = component.get("name", "")
                version = component.get("version", "")
                purl = component.get("purl", "")
                
                # Extract type from purl (pkg:npm/package-name@version)
                comp_type = package_type
                if purl.startswith("pkg:"):
                    comp_type = purl.split("/")[0].replace("pkg:", "")
                
                # Get licenses
                licenses = ""
                if component.get("licenses"):
                    license_list = []
                    for lic in component.get("licenses", []):
                        if "license" in lic:
                            license_id = lic["license"].get("id", "")
                            if license_id:
                                license_list.append(license_id)
                    licenses = ", ".join(license_list)
                
                if name and version:
                    dep_key = f"{name}@{version}"
                    
                    # Deduplicate - only add if not exists or append project name
                    if dep_key in all_dependencies:
                        existing_projects = all_dependencies[dep_key]["projects"]
                        if project_name not in existing_projects:
                            all_dependencies[dep_key]["projects"] += f"; {project_name}"
                    else:
                        all_dependencies[dep_key] = {
                            "id": dep_key,
                            "name": name,
                            "version": version,
                            "type": comp_type,
                            "issuesCritical": 0,
                            "issuesHigh": 0,
                            "issuesMedium": 0,
                            "issuesLow": 0,
                            "dependenciesWithIssues": "",
                            "licenses": licenses,
                            "projects": project_name,
                            "license urls": "",
                            "latestVersion": "",
                            "latestVersionPublishedDate": "",
                            "firstPublishedDate": "",
                            "isDeprecated": ""
                        }
        
        except requests.exceptions.HTTPError as e:
            print(f"      ⚠️  Error fetching SBOM for {project_name}: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"      Response: {e.response.text[:200]}")
            continue
    
    return list(all_dependencies.values())


def save_to_csv(dependencies, output_path):
    """Save dependencies to CSV file"""
    if not dependencies:
        print("❌ No dependencies to save")
        return False
    
    df = pd.DataFrame(dependencies)
    
    # Ensure all expected columns exist
    expected_columns = [
        "id", "name", "version", "type", "issuesCritical", "issuesHigh", 
        "issuesMedium", "issuesLow", "dependenciesWithIssues", "licenses", 
        "projects", "license urls", "latestVersion", "latestVersionPublishedDate", 
        "firstPublishedDate", "isDeprecated"
    ]
    
    for col in expected_columns:
        if col not in df.columns:
            df[col] = ""
    
    # Reorder columns
    df = df[expected_columns]
    
    # Save to CSV
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    
    print(f"✅ Saved {len(df)} dependencies to {output_path}")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Fetch dependencies from Snyk REST API and export as CSV"
    )
    parser.add_argument("--org", required=True, help="Snyk organization ID")
    parser.add_argument("--token", required=True, help="Snyk API token")
    parser.add_argument("--type", default="npm", choices=["npm", "nuget", "pip"], 
                       help="Package type to fetch (default: npm)")
    parser.add_argument("--output", required=True, help="Output CSV file path")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("  Fetch Dependencies from Snyk REST API")
    print("=" * 60)
    print()
    
    # Fetch dependencies
    dependencies = fetch_dependencies(args.org, args.token, args.type)
    
    if not dependencies:
        print()
        print("❌ No dependencies found")
        return 1
    
    print()
    print(f"📊 Total unique dependencies: {len(dependencies)}")
    
    # Save to CSV
    from pathlib import Path
    output_path = Path(args.output)
    
    if save_to_csv(dependencies, output_path):
        print()
        print("🎉 Done!")
        return 0
    else:
        return 1


if __name__ == "__main__":
    exit(main())
