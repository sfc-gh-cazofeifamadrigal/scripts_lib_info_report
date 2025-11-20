#!/usr/bin/env python3
"""
Script to fix [REVIEW URL] placeholders in the generated markdown report
by looking up license URLs from a reference file.

Usage:
    python src/fix_review_urls.py --input reports/2025-11-17-01/open-source-libraries.md --reference expected/open-source-libraries.md
"""

import argparse
import re
from pathlib import Path
from typing import Dict, Tuple


class URLFixer:
    """Fixes [REVIEW URL] placeholders by looking up URLs from reference file."""
    
    def __init__(self, verbose: bool = False):
        self.reference_urls: Dict[Tuple[str, str], str] = {}  # (name, type) -> url
        self.verbose = verbose
        
    def load_reference_urls(self, reference_file: Path) -> None:
        """Load license URLs from reference markdown file."""
        print(f"📖 Loading reference URLs from {reference_file.name}...")
        
        content = reference_file.read_text(encoding='utf-8')
        
        # Find all markdown table rows (skip header rows)
        # Format: | name | version | type | licenses | license urls |
        pattern = r'\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*(nuget|npm)\s*\|\s*([^|]+?)\s*\|\s*\[([^\]]+)\]\(([^)]+)\)\s*\|'
        
        matches = re.finditer(pattern, content)
        count = 0
        
        for match in matches:
            name = match.group(1).strip()
            pkg_type = match.group(3).strip()
            url = match.group(6).strip()
            
            # Store by (name, type) as key
            key = (name, pkg_type)
            self.reference_urls[key] = url
            count += 1
            
            if self.verbose and count <= 5:
                print(f"      • {name} ({pkg_type}): {url}")
        
        if self.verbose and count > 5:
            print(f"      ... and {count - 5} more")
            
        print(f"   ✓ Loaded {count} reference URLs")
        
    def fix_review_urls(self, input_file: Path, output_file: Path) -> None:
        """Fix [REVIEW URL] placeholders in the input file and save to output."""
        print(f"\n🔧 Fixing [REVIEW URL] placeholders in {input_file.name}...")
        
        content = input_file.read_text(encoding='utf-8')
        
        # Find all rows with [REVIEW URL]
        # Format: | name | version | type | licenses | [REVIEW URL] |
        pattern = r'(\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*(nuget|npm)\s*\|\s*([^|]+?)\s*\|\s*)\[REVIEW URL\](\s*\|)'
        
        fixed_count = 0
        not_found_count = 0
        not_found_packages = []
        
        def replace_url(match):
            nonlocal fixed_count, not_found_count
            
            prefix = match.group(1)  # Everything before [REVIEW URL]
            name = match.group(2).strip()
            pkg_type = match.group(4).strip()
            suffix = match.group(6)  # Everything after [REVIEW URL]
            
            key = (name, pkg_type)
            
            if key in self.reference_urls:
                url = self.reference_urls[key]
                fixed_count += 1
                if self.verbose:
                    print(f"   ✓ {name} ({pkg_type}): {url}")
                # Return with proper markdown link format
                return f"{prefix}[{url}]({url}){suffix}"
            else:
                not_found_count += 1
                not_found_packages.append(f"{name} ({pkg_type})")
                if self.verbose:
                    print(f"   ✗ {name} ({pkg_type}): not found in reference")
                # Keep [REVIEW URL] if not found
                return match.group(0)
        
        # Replace all occurrences
        fixed_content = re.sub(pattern, replace_url, content)
        
        # Save to output file
        output_file.write_text(fixed_content, encoding='utf-8')
        
        print(f"   ✓ Fixed {fixed_count} URLs")
        if not_found_count > 0:
            print(f"   ⚠️  Could not find reference URLs for {not_found_count} packages:")
            for pkg in not_found_packages[:10]:  # Show first 10
                print(f"      - {pkg}")
            if len(not_found_packages) > 10:
                print(f"      ... and {len(not_found_packages) - 10} more")
        
        print(f"\n✅ Fixed file saved to: {output_file}")
        print(f"   Total [REVIEW URL] remaining: {fixed_content.count('[REVIEW URL]')}")


def main():
    parser = argparse.ArgumentParser(
        description='Fix [REVIEW URL] placeholders by looking up URLs from reference file.'
    )
    parser.add_argument(
        '--input',
        required=True,
        help='Path to the input markdown file with [REVIEW URL] placeholders'
    )
    parser.add_argument(
        '--reference',
        required=True,
        help='Path to the reference markdown file with correct URLs'
    )
    parser.add_argument(
        '--output',
        help='Path to save the fixed file (defaults to input-fixed.md)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed progress information'
    )
    
    args = parser.parse_args()
    
    # Parse paths
    input_file = Path(args.input)
    reference_file = Path(args.reference)
    
    if args.output:
        output_file = Path(args.output)
    else:
        # Default: add -fixed before .md extension
        output_file = input_file.parent / f"{input_file.stem}-fixed{input_file.suffix}"
    
    # Validate inputs
    if not input_file.exists():
        print(f"❌ Error: Input file not found: {input_file}")
        return 1
    
    if not reference_file.exists():
        print(f"❌ Error: Reference file not found: {reference_file}")
        return 1
    
    # Process
    try:
        fixer = URLFixer(verbose=args.verbose)
        fixer.load_reference_urls(reference_file)
        fixer.fix_review_urls(input_file, output_file)
        return 0
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main())
