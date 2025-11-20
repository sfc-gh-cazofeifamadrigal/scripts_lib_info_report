#!/bin/bash
# Convenience script to generate report and fix review URLs in one step

set -e  # Exit on error

echo "================================================"
echo "  Dependency Report Generator with URL Fix"
echo "================================================"
echo ""

# Check if conda environment exists
if ! conda env list | grep -q "dep-report"; then
    echo "⚠️  Conda environment 'dep-report' not found"
    echo "Creating environment..."
    conda create -n dep-report python=3.11 -y
    echo "📦 Installing dependencies..."
    conda run -n dep-report pip install -r requirements.txt
    echo "✅ Environment 'dep-report' created successfully"
else
    echo "✅ Using existing conda environment 'dep-report'"
fi
echo ""

# Parse arguments
SNYK_ORG_ID="${SNYK_ORG_ID:-}"
SNYK_API_TOKEN="${SNYK_API_TOKEN:-}"
VERBOSE=""
SKIP_FETCH=false

# First pass: extract flags
for arg in "$@"; do
    if [ "$arg" = "--verbose" ] || [ "$arg" = "-v" ]; then
        VERBOSE="--verbose"
        echo "🔍 Verbose mode enabled"
    fi
    if [ "$arg" = "--skip-fetch" ]; then
        SKIP_FETCH=true
        echo "⏭️  Skipping Snyk API fetch"
    fi
done

# Second pass: extract positional arguments (skip flags)
POSITIONAL_ARGS=()
for arg in "$@"; do
    if [ "$arg" != "--verbose" ] && [ "$arg" != "-v" ] && [ "$arg" != "--skip-fetch" ]; then
        POSITIONAL_ARGS+=("$arg")
    fi
done

# Set defaults for positional arguments
INPUT_NUGET_DIR="${POSITIONAL_ARGS[0]:-input_nuget/}"
INPUT_NPM_DIR="${POSITIONAL_ARGS[1]:-input_npm/}"
OUTPUT_DIR="${POSITIONAL_ARGS[2]:-out/}"
REFERENCE_FILE="${POSITIONAL_ARGS[3]:-expected/open-source-libraries.md}"

echo "📊 Configuration:"
echo "   NuGet Input: $INPUT_NUGET_DIR"
echo "   NPM Input:   $INPUT_NPM_DIR"
echo "   Output:      $OUTPUT_DIR"
echo "   Reference:   $REFERENCE_FILE"
echo ""

# Step 0: Fetch from Snyk API (if not skipped)
if [ "$SKIP_FETCH" = false ]; then
    echo "🌐 Step 0: Fetching dependencies from Snyk API..."
    
    # Check if Snyk credentials are provided
    if [ -z "$SNYK_ORG_ID" ] || [ -z "$SNYK_API_TOKEN" ]; then
        echo "⚠️  Snyk credentials not found in environment variables"
        echo "   Set SNYK_ORG_ID and SNYK_API_TOKEN to enable automatic fetching"
        echo "   Or use --skip-fetch to use existing CSV files"
        echo ""
        echo "   Skipping Snyk API fetch..."
    else
        echo "   Fetching NuGet dependencies..."
        mkdir -p "$INPUT_NUGET_DIR"
        conda run -n dep-report python src/fetch_from_snyk_rest_api.py \
            --org "$SNYK_ORG_ID" \
            --token "$SNYK_API_TOKEN" \
            --type nuget \
            --output "$INPUT_NUGET_DIR/dependencies-nuget.csv" || {
                echo "⚠️  Warning: Failed to fetch NuGet dependencies"
            }
        
        echo "   Fetching NPM dependencies..."
        mkdir -p "$INPUT_NPM_DIR"
        conda run -n dep-report python src/fetch_from_snyk_rest_api.py \
            --org "$SNYK_ORG_ID" \
            --token "$SNYK_API_TOKEN" \
            --type npm \
            --output "$INPUT_NPM_DIR/npm-dependencies.csv" || {
                echo "⚠️  Warning: Failed to fetch NPM dependencies"
            }
        
        echo "✅ Snyk API fetch completed"
    fi
    echo ""
else
    echo "⏭️  Skipping Snyk API fetch (using existing CSV files)"
    echo ""
fi

# Create temporary merged directory
TEMP_DIR=$(mktemp -d)
echo "📁 Creating temporary merged directory: $TEMP_DIR"

# Copy nuget files
if [ -d "$INPUT_NUGET_DIR" ] && [ "$(ls -A $INPUT_NUGET_DIR/*.csv 2>/dev/null)" ]; then
    echo "   Copying NuGet dependencies..."
    cp "$INPUT_NUGET_DIR"/*.csv "$TEMP_DIR/"
fi

# Copy npm files
if [ -d "$INPUT_NPM_DIR" ] && [ "$(ls -A $INPUT_NPM_DIR/*.csv 2>/dev/null)" ]; then
    echo "   Copying NPM dependencies..."
    cp "$INPUT_NPM_DIR"/*.csv "$TEMP_DIR/"
fi

# Step 1: Generate report
echo ""
echo "🔄 Step 1: Generating dependency report..."
conda run -n dep-report python src/process_dependencies.py \
    --input "$TEMP_DIR" \
    --output "$OUTPUT_DIR" \
    $VERBOSE

if [ $? -ne 0 ]; then
    echo "❌ Error generating report"
    exit 1
fi

# Step 2: Fix review URLs
echo ""
echo "🔧 Step 2: Fixing [REVIEW URL] placeholders..."

COMBINED_FILE="$OUTPUT_DIR/open-source-libraries.md"
FIXED_FILE="$OUTPUT_DIR/open-source-libraries-fixed.md"

if [ ! -f "$COMBINED_FILE" ]; then
    echo "❌ Error: Combined report not found at $COMBINED_FILE"
    exit 1
fi

if [ ! -f "$REFERENCE_FILE" ]; then
    echo "⚠️  Warning: Reference file not found at $REFERENCE_FILE"
    echo "   Skipping URL fix step"
else
    conda run -n dep-report python src/fix_review_urls.py \
        --input "$COMBINED_FILE" \
        --reference "$REFERENCE_FILE" \
        --output "$FIXED_FILE" \
        $VERBOSE
    
    if [ $? -ne 0 ]; then
        echo "❌ Error fixing URLs"
        exit 1
    fi
fi

# Clean up temporary directory
echo ""
echo "🧹 Cleaning up temporary files..."
rm -rf "$TEMP_DIR"

echo ""
echo "✅ Complete! Files generated in: $OUTPUT_DIR"
echo ""
echo "📄 Generated files:"
ls -lh "$OUTPUT_DIR"

echo ""
echo "🎉 All done!"
echo ""
echo "Usage: $0 [nuget_input_dir] [npm_input_dir] [output_dir] [reference_file] [flags]"
echo ""
echo "Flags:"
echo "  --verbose, -v     Enable verbose output"
echo "  --skip-fetch      Skip Snyk API fetch and use existing CSV files"
echo ""
echo "Environment Variables:"
echo "  SNYK_ORG_ID       Snyk organization ID (required for API fetch)"
echo "  SNYK_API_TOKEN    Snyk API token (required for API fetch)"
echo ""
echo "Examples:"
echo "  # Full end-to-end with Snyk API fetch"
echo "  export SNYK_ORG_ID=your-org-id"
echo "  export SNYK_API_TOKEN=your-token"
echo "  $0"
echo ""
echo "  # Use existing CSV files (skip API fetch)"
echo "  $0 input_nuget/ input_npm/ --skip-fetch"
echo ""
echo "  # Custom paths with verbose output"
echo "  $0 sc/ sma/ out/ expected/open-source-libraries.md --verbose"
