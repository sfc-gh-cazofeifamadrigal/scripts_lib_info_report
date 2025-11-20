"""
Main orchestrator for dependency report generation

Usage:
    python process_dependencies.py --input <input_csv> [options]
    
    Options:
        --input PATH         Input CSV file or directory with CSV files (required)
        --output PATH        Output directory (default: output)
        --skip-urls          Skip fetching license URLs
        --format FORMAT      Output format: md, xlsx, both (default: both)
        --verbose            Show detailed progress
"""
import argparse
import sys
from pathlib import Path
import pandas as pd
import requests
from tqdm import tqdm
import time

from config import (
    COLUMNS_TO_REMOVE,
    FILTER_PREFIXES,
    REQUEST_DELAY_NUGET,
    REQUEST_DELAY_NPM,
    REPORT_TITLE
)
from processors import CSVProcessor, LicenseURLFinder, ExportProcessor


class DependencyReportOrchestrator:
    """Orchestrates the entire dependency report generation process"""
    
    def __init__(self, input_path: Path, output_dir: Path, skip_urls: bool = False, verbose: bool = False):
        self.input_path = input_path
        self.output_dir = output_dir
        self.skip_urls = skip_urls
        self.verbose = verbose
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize processors
        self.csv_processor = CSVProcessor()
        self.export_processor = ExportProcessor()
    
    def log(self, message: str):
        """Log message if verbose mode is enabled"""
        if self.verbose:
            print(f"[INFO] {message}")
    
    def run(self) -> dict:
        """Run the complete processing pipeline"""
        print("🚀 Starting dependency report generation...")
        
        # Step 1: Load and merge CSV files
        print("\n📂 Step 1: Loading CSV data...")
        df = self._load_data()
        self.log(f"Loaded {len(df)} rows")
        
        # Step 2: Remove unnecessary columns
        print("🧹 Step 2: Removing unnecessary columns...")
        df = self.csv_processor.remove_columns(df, COLUMNS_TO_REMOVE)
        self.log(f"Removed columns: {', '.join(COLUMNS_TO_REMOVE)}")
        
        # Step 3: Remove duplicates (keep highest version)
        print("🔍 Step 3: Removing duplicates...")
        original_count = len(df)
        df = self.csv_processor.remove_duplicates_keep_highest_version(df)
        self.log(f"Removed {original_count - len(df)} duplicate entries")
        
        # Step 4: Filter internal packages
        print("🔧 Step 4: Filtering internal packages...")
        original_count = len(df)
        df = self.csv_processor.filter_by_prefixes(df, FILTER_PREFIXES)
        self.log(f"Filtered out {original_count - len(df)} internal packages")
        
        # Step 5: Split by package type
        print("📦 Step 5: Splitting by package type...")
        df_nuget, df_npm = self.csv_processor.split_by_type(df)
        print(f"   - NuGet packages: {len(df_nuget)}")
        print(f"   - NPM packages: {len(df_npm)}")
        
        # Step 6: Fetch license URLs (if not skipped)
        if not self.skip_urls:
            print("\n🔗 Step 6: Fetching license URLs...")
            df_nuget = self._add_license_urls(df_nuget, 'nuget')
            df_npm = self._add_license_urls(df_npm, 'npm')
        else:
            print("\n⏭️  Step 6: Skipped (--skip-urls flag)")
            df_nuget['license urls'] = ''
            df_npm['license urls'] = ''
        
        # Step 7: Export results
        print("\n💾 Step 7: Exporting results...")
        results = self._export_results(df_nuget, df_npm)
        
        print("\n✅ Processing complete!")
        self._print_summary(results)
        
        return results
    
    def _load_data(self) -> pd.DataFrame:
        """Load CSV data from file or directory"""
        if self.input_path.is_file():
            return pd.read_csv(self.input_path)
        elif self.input_path.is_dir():
            return self.csv_processor.merge_csv_files(self.input_path)
        else:
            raise ValueError(f"Input path not found: {self.input_path}")
    
    def _add_license_urls(self, df: pd.DataFrame, package_type: str) -> pd.DataFrame:
        """Add license URLs to DataFrame"""
        if df.empty:
            df['license urls'] = ''
            return df
        
        print(f"   Fetching {package_type.upper()} license URLs...")
        urls = []
        
        with requests.Session() as session:
            finder = LicenseURLFinder(session)
            
            for package_name in tqdm(df['name'], desc=f"   {package_type.upper()}", unit="pkg"):
                try:
                    if package_type == 'nuget':
                        url = finder.get_nuget_license_url(package_name)
                        delay = REQUEST_DELAY_NUGET
                    else:  # npm
                        url = finder.get_npm_license_url(package_name)
                        delay = REQUEST_DELAY_NPM
                    
                    urls.append(url)
                    
                    if self.verbose:
                        status = "✅" if url else "❌"
                        print(f"      {package_name}: {status}")
                    
                    time.sleep(delay)
                    
                except Exception as e:
                    print(f"   ⚠️  Error processing {package_name}: {e}")
                    urls.append('')
        
        df['license urls'] = urls
        found = sum(1 for url in urls if url)
        print(f"   Found {found}/{len(urls)} license URLs")
        
        return df
    
    def _export_results(self, df_nuget: pd.DataFrame, df_npm: pd.DataFrame) -> dict:
        """Export results in requested formats"""
        results = {}
        
        for df, pkg_type in [(df_nuget, 'nuget'), (df_npm, 'npm')]:
            if df.empty:
                continue
            
            # Sort by name
            df = df.sort_values(by='name')
            
            # Export to CSV (always)
            csv_path = self.output_dir / f"dependencies_{pkg_type}.csv"
            df.to_csv(csv_path, index=False)
            print(f"   📄 {csv_path}")
            
            # Export to Excel
            xlsx_path = self.output_dir / f"dependencies_{pkg_type}.xlsx"
            self.export_processor.to_excel(df, xlsx_path)
            print(f"   📊 {xlsx_path}")
            
            # Export to Markdown (individual)
            md_path = self.output_dir / f"dependencies_{pkg_type}.md"
            self.export_processor.to_markdown(df, md_path)
            print(f"   📝 {md_path}")
            
            results[pkg_type] = {
                'count': len(df),
                'csv': csv_path,
                'xlsx': xlsx_path,
                'md': md_path
            }
        
        # Export combined markdown file
        if not df_nuget.empty or not df_npm.empty:
            combined_md_path = self.output_dir / "open-source-libraries.md"
            self.export_processor.to_markdown_combined(
                df_nuget, 
                df_npm, 
                combined_md_path,
                title=REPORT_TITLE
            )
            print(f"   📚 {combined_md_path} (combined)")
            results['combined'] = combined_md_path
        
        return results
    
    def _print_summary(self, results: dict):
        """Print summary of results"""
        print("\n" + "="*60)
        print("📊 SUMMARY")
        print("="*60)
        
        # Filter out the 'combined' key which is just a Path
        package_results = {k: v for k, v in results.items() if k != 'combined'}
        
        total_packages = sum(r['count'] for r in package_results.values())
        print(f"\nTotal packages processed: {total_packages}")
        
        for pkg_type, data in package_results.items():
            print(f"\n{pkg_type.upper()} packages: {data['count']}")
            print("  Output files:")
            print(f"    - CSV:   {data['csv'].name}")
            print(f"    - Excel: {data['xlsx'].name}")
            print(f"    - MD:    {data['md'].name}")
        
        if 'combined' in results:
            print(f"\n📚 Combined report: {results['combined'].name}")
        
        print(f"\n📁 All files saved to: {self.output_dir.absolute()}")
        print("="*60)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Generate dependency reports from Snyk CSV exports",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process single CSV file
  python process_dependencies.py --input data/dependencies.csv
  
  # Process all CSVs in a directory
  python process_dependencies.py --input data/ --output reports/
  
  # Skip fetching URLs (faster, for testing)
  python process_dependencies.py --input data.csv --skip-urls
  
  # Verbose mode
  python process_dependencies.py --input data.csv --verbose
        """
    )
    
    parser.add_argument(
        '--input', '-i',
        type=Path,
        required=True,
        help='Input CSV file or directory containing CSV files'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=Path,
        default=Path('out'),
        help='Output directory (default: out)'
    )
    
    parser.add_argument(
        '--skip-urls',
        action='store_true',
        help='Skip fetching license URLs (faster processing)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed progress information'
    )
    
    args = parser.parse_args()
    
    # Validate input path
    if not args.input.exists():
        print(f"❌ Error: Input path does not exist: {args.input}")
        sys.exit(1)
    
    # Run orchestrator
    try:
        orchestrator = DependencyReportOrchestrator(
            input_path=args.input,
            output_dir=args.output,
            skip_urls=args.skip_urls,
            verbose=args.verbose
        )
        orchestrator.run()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
