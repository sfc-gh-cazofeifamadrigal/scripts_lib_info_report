# Dependency Report Generator

Automated tool to generate open-source library reports from Snyk API.

## Quick Start

### Option 1: Fully Automated End-to-End (Recommended)

Run everything with a single command:

```bash
# Set Snyk credentials as environment variables
export SNYK_ORG_ID=your-org-id
export SNYK_API_TOKEN=your-api-token

# Run complete pipeline (fetches from Snyk API + generates report)
./generate_report.sh

# With verbose output
./generate_report.sh --verbose
```

The script will automatically:
1. Check/create conda environment
2. Fetch dependencies from Snyk API (npm + nuget)
3. Generate reports
4. Fix review URLs
5. Clean up temporary files

### Option 2: Use Existing CSV Files

If you already have CSV files:

```bash
./generate_report.sh --skip-fetch

# Or with custom paths
./generate_report.sh input_nuget/ input_npm/ --skip-fetch
```

### Option 3: Manual Step-by-Step

1. **Create and activate conda environment**
   ```bash
   conda create -n dep-report python=3.11
   conda activate dep-report
   pip install -r requirements.txt
   ```

2. **Fetch dependencies from Snyk API**
   
   ```bash
   # Fetch npm dependencies
   python src/fetch_from_snyk_rest_api.py \
     --org <YOUR_ORG_ID> \
     --token <YOUR_API_TOKEN> \
     --type npm \
     --output input_npm/npm-dependencies.csv
   
   # Fetch nuget dependencies
   python src/fetch_from_snyk_rest_api.py \
     --org <YOUR_ORG_ID> \
     --token <YOUR_API_TOKEN> \
     --type nuget \
     --output input_nuget/nuget-dependencies.csv
   ```

3. **Generate the report**
   ```bash
   ./generate_report.sh input_nuget/ input_npm/ --skip-fetch
   ```

4. **Check the results in `out/`**
   - Main file: `out/open-source-libraries.md`
   - Fixed version: `out/open-source-libraries-fixed.md`
   - Also generates CSV, Excel, and individual MD files

## What It Does

The `generate_report.sh` script runs a complete automated pipeline:

**Step 0: Fetch from Snyk API (optional)**
- Auto-detects `SNYK_ORG_ID` and `SNYK_API_TOKEN` environment variables
- Fetches npm and nuget dependencies using Snyk REST API v3
- Creates `input_npm/` and `input_nuget/` directories with CSVs
- Can be skipped with `--skip-fetch` flag to use existing files

**Step 1: Process Dependencies**
1. Merges CSV files from both directories
2. Removes unnecessary columns
3. Deduplicates keeping highest version
4. Filters internal packages (configurable prefixes)
5. Splits NuGet and NPM packages
6. Fetches license URLs from GitHub
7. Exports to CSV, Excel, and Markdown formats

**Step 2: Fix Review URLs**
- Automatically compares with reference file
- Replaces `[REVIEW URL]` placeholders with known URLs
- Generates `open-source-libraries-fixed.md`

**Step 3: Cleanup**
- Removes temporary files
- Shows summary of generated files

## Output Structure

```
out/
├── dependencies_nuget.csv
├── dependencies_nuget.xlsx
├── dependencies_nuget.md
├── dependencies_npm.csv
├── dependencies_npm.xlsx
├── dependencies_npm.md
├── open-source-libraries.md        ⭐ Generated report
└── open-source-libraries-fixed.md  ✨ Fixed URLs version
```

The `open-source-libraries.md` file includes:
- YAML frontmatter
- Separate sections for .NET and Node libraries
- License URLs as markdown links

The `open-source-libraries-fixed.md` is the enhanced version with all known license URLs resolved.

## Command Line Usage

### Main Script: `generate_report.sh`

```bash
./generate_report.sh [nuget_input_dir] [npm_input_dir] [output_dir] [reference_file] [flags]
```

**Arguments:**
- `nuget_input_dir` - Directory with NuGet CSV files (default: `input_nuget/`)
- `npm_input_dir` - Directory with NPM CSV files (default: `input_npm/`)
- `output_dir` - Output directory (default: `out/`)
- `reference_file` - Reference file for URL fixing (default: `expected/open-source-libraries.md`)

**Flags:**
- `--verbose`, `-v` - Enable verbose output
- `--skip-fetch` - Skip Snyk API fetch and use existing CSV files

**Environment Variables:**
- `SNYK_ORG_ID` - Snyk organization ID (required for API fetch)
- `SNYK_API_TOKEN` - Snyk API token (required for API fetch)

**Examples:**

```bash
# Full end-to-end with Snyk API fetch
export SNYK_ORG_ID=your-org-id
export SNYK_API_TOKEN=your-token
./generate_report.sh

# Use existing CSV files (skip API fetch)
./generate_report.sh --skip-fetch

# Custom paths with verbose output
./generate_report.sh sc/ sma/ out/ expected/open-source-libraries.md --verbose

# Skip fetch + verbose
./generate_report.sh input_nuget/ input_npm/ --skip-fetch --verbose
```

### Individual Scripts

If you need more control, you can run the individual Python scripts:

### Individual Scripts

If you need more control, you can run the individual Python scripts:

**Fetch from Snyk API:**
```bash
python src/fetch_from_snyk_rest_api.py \
  --org <ORG_ID> \
  --token <API_TOKEN> \
  --type npm \
  --output input_npm/npm-dependencies.csv
```

**Process dependencies:**
```bash
# Basic usage
python src/process_dependencies.py --input sc/dependencies.csv

# Custom output directory
python src/process_dependencies.py --input sc/ --output reports/2025-11-20

# Skip URL fetching (faster, for testing)
python src/process_dependencies.py --input sc/ --skip-urls

# Verbose output
python src/process_dependencies.py --input sc/ --verbose

# Help
python src/process_dependencies.py --help
```

**Fix review URLs:**
```bash
python src/fix_review_urls.py \
  --input out/open-source-libraries.md \
  --reference expected/open-source-libraries.md \
  --output out/open-source-libraries-fixed.md
```

## Configuration

Edit `src/config.py` to customize:

```python
# Report title
REPORT_TITLE = "SnowConvert AI - Open Source Libraries"

# Packages to filter out (internal packages)
FILTER_PREFIXES = [
    'Mobilize.', 'Artinsoft.', 'Snowflake.',
    '@snowflake/', '@mobilize/', ...
]

# Request delays (to avoid rate limiting)
REQUEST_DELAY_NUGET = 2
REQUEST_DELAY_NPM = 1

# License file variations to search
LICENSE_FILES = ["LICENSE.md", "LICENSE", "LICENSE.txt", ...]

# Known license URLs (avoids HTTP requests for common packages)
KNOWN_LICENSE_URLS = {
    'typescript': 'https://github.com/microsoft/TypeScript/blob/main/LICENSE.txt',
    'react': 'https://github.com/facebook/react/blob/master/LICENSE',
    # ... 100+ pre-configured packages
}
```

## Post-Processing: Fix Review URLs

The `generate_report.sh` script automatically runs this step, but you can also run it manually:

```bash
# Fix URLs using a reference file
python src/fix_review_urls.py \
  --input out/open-source-libraries.md \
  --reference expected/open-source-libraries.md \
  --output out/open-source-libraries-fixed.md
```

This will:
- Load known license URLs from the reference file
- Replace `[REVIEW URL]` placeholders with actual URLs where available
- Generate a report showing how many URLs were fixed
- Save the fixed version to the output file

The tool matches packages by name and type (nuget/npm), so it works even if versions differ.

## Validation

After generating reports, validate the results:

```bash
python validate.py --file out/dependencies_nuget.csv
python validate.py --file out/dependencies_npm.csv
```

## Project Structure

```
scripts_lib_info_report/
├── src/
│   ├── config.py                   # Configuration (filters, URLs, delays)
│   ├── fetch_from_snyk_rest_api.py # Fetch from Snyk REST API v3
│   ├── processors.py               # Processing logic (CSV, URLs, Export)
│   ├── process_dependencies.py     # Main orchestrator
│   └── fix_review_urls.py          # Fix [REVIEW URL] placeholders
├── input_nuget/                    # NuGet CSV files (auto-created)
├── input_npm/                      # NPM CSV files (auto-created)
├── out/                            # Generated reports
├── expected/                       # Reference files for URL fixing
├── generate_report.sh              # ⭐ Main end-to-end script
├── requirements.txt                # Python dependencies
└── validate.py                     # Validation script
```

## Requirements

- Python 3.8+
- pandas
- requests
- beautifulsoup4
- tqdm
- openpyxl

## Troubleshooting

**"Module not found" error**
```bash
conda activate dep-report
pip install -r requirements.txt
```

**Conda environment not created automatically**
- The `generate_report.sh` script will create it automatically on first run
- Or create manually: `conda create -n dep-report python=3.11 -y`

**Snyk API fetch not working**
- Check environment variables: `echo $SNYK_ORG_ID $SNYK_API_TOKEN`
- Verify credentials are correct
- Try with `--verbose` flag to see detailed error messages
- Use `--skip-fetch` to bypass and use existing CSVs

**Dependency conflicts**
Using conda environment isolates dependencies from system packages like ggshield

**License URLs not found**
- Increase delays in `config.py` if hitting rate limits
- Some packages may not have GitHub repositories
- Add known URLs to `KNOWN_LICENSE_URLS` in `config.py`
- Use `--verbose` to see details

**"No CSV files found"**
```bash
# Check if files exist
ls -la input_nuget/*.csv
ls -la input_npm/*.csv

# Or fetch from Snyk
export SNYK_ORG_ID=your-org-id
export SNYK_API_TOKEN=your-token
./generate_report.sh
```

## Tips

- **Recommended workflow**: Use `generate_report.sh` with environment variables for full automation
- Set `SNYK_ORG_ID` and `SNYK_API_TOKEN` in your shell profile for convenience
- Use `--skip-fetch` when iterating on report formatting to save API calls
- Keep reference file (`expected/open-source-libraries.md`) updated with known URLs
- Add frequently used packages to `KNOWN_LICENSE_URLS` in `config.py`
- Use `--verbose` when debugging issues
- Version control the generated `open-source-libraries-fixed.md`
- The script automatically creates conda environment on first run
- Input directories (`input_nuget/`, `input_npm/`) are auto-created by the script
