#!/usr/bin/env python3
"""
SEO-FORGE: Multi-Framework SEO & Metadata Audit Tool
Checks Blazor (.razor), HTML, JSX, and TSX files for SEO best practices.

PURPOSE:
    - Verify meta tags, titles, and descriptions
    - Check Open Graph tags for social sharing
    - Validate heading hierarchy (H1-H6)
    - Check image accessibility (alt attributes)
    - Detect Blazor PageTitle and HeadContent

Usage:
    python seo_checker.py [project_path]
"""
import sys
import json
import re
from pathlib import Path
from datetime import datetime

# Fix Windows console encoding
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except:
    pass

# Directories to skip
SKIP_DIRS = {
    'node_modules', '.next', 'dist', 'build', '.git', '.github',
    '__pycache__', '.vscode', '.idea', 'coverage', 'test', 'tests',
    '__tests__', 'spec', 'docs', 'documentation', 'examples', 'bin', 'obj'
}

# Files to skip (not pages)
SKIP_PATTERNS = [
    'config', 'setup', 'util', 'helper', 'hook', 'context', 'store',
    'service', 'api', 'lib', 'constant', 'type', 'interface', 'mock',
    '.test.', '.spec.', '_test.', '_spec.'
]


def is_page_file(file_path: Path) -> bool:
    """Check if this file is likely a public-facing page."""
    name = file_path.name.lower()
    stem = file_path.stem.lower()
    suffix = file_path.suffix.lower()
    
    # Skip utility/config files
    if any(skip in name for skip in SKIP_PATTERNS):
        return False
    
    parts = [p.lower() for p in file_path.parts]
    page_dirs = ['pages', 'app', 'routes', 'views', 'screens']
    
    # Blazor razor components with @page
    if suffix == '.razor':
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                first_lines = "".join([f.readline() for _ in range(10)])
                if '@page' in first_lines:
                    return True
        except:
            pass
        if any(d in parts for d in page_dirs):
            return True

    if any(d in parts for d in page_dirs):
        return True
    
    page_names = ['page', 'index', 'home', 'about', 'contact', 'blog', 
                  'post', 'article', 'product', 'landing', 'layout']
    
    if any(p in stem for p in page_names):
        return True
    
    if suffix in ['.html', '.htm']:
        return True
    
    return False


def find_pages(project_path: Path) -> list:
    """Find page files to check."""
    patterns = ['**/*.html', '**/*.htm', '**/*.jsx', '**/*.tsx', '**/*.razor']
    
    files = []
    for pattern in patterns:
        for f in project_path.glob(pattern):
            if any(skip in f.parts for skip in SKIP_DIRS):
                continue
            if is_page_file(f):
                files.append(f)
    
    return files[:50]


def check_page(file_path: Path) -> dict:
    """Check a single page for SEO issues."""
    issues = []
    
    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
    except Exception as e:
        return {"file": str(file_path.name), "issues": [f"Error: {e}"]}
    
    is_razor = file_path.suffix.lower() == '.razor'
    is_layout = 'Head>' in content or '<head' in content.lower() or 'Layout' in file_path.stem or is_razor
    
    # 1. Title tag
    has_title = (
        '<title' in content.lower() or 
        'title=' in content.lower() or 
        'Head>' in content or 
        '<PageTitle>' in content or 
        '<pagetitle' in content.lower() or
        '<seoheader' in content.lower()
    )
    if not has_title and is_layout:
        issues.append("Missing <title> or <PageTitle> tag")
    
    # 2. Meta description
    has_description = (
        'name="description"' in content.lower() or 
        'name=\'description\'' in content.lower() or
        'description=' in content.lower() or
        '<seoheader' in content.lower()
    )
    if not has_description and is_layout:
        issues.append("Missing meta description")
    
    # 3. Open Graph tags
    has_og = (
        'og:' in content or 
        'property="og:' in content.lower() or
        'ogimage=' in content.lower() or
        '<seoheader' in content.lower()
    )
    if not has_og and is_layout:
        issues.append("Missing Open Graph tags")
    
    # 4. Heading hierarchy
    h1_matches = re.findall(r'<h1[^>]*>', content, re.I)
    if len(h1_matches) > 1:
        issues.append(f"Multiple H1 tags ({len(h1_matches)})")
    
    # 5. Images without alt
    img_pattern = r'<img[^>]+>'
    imgs = re.findall(img_pattern, content, re.I)
    for img in imgs:
        if 'alt=' not in img.lower():
            issues.append("Image missing alt attribute")
            break
        if 'alt=""' in img or "alt=''" in img:
            issues.append("Image has empty alt attribute")
            break
    
    return {
        "file": str(file_path.name),
        "issues": issues
    }


def main():
    project_path = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    
    print(f"\n{'='*60}")
    print(f"  SEO-FORGE - Search Engine & Social Audit")
    print(f"{'='*60}")
    print(f"Project: {project_path}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)
    
    pages = find_pages(project_path)
    
    if not pages:
        print("\n[!] No page files found.")
        output = {"script": "seo_checker", "files_checked": 0, "passed": True}
        print("\n" + json.dumps(output, indent=2))
        sys.exit(0)
    
    print(f"Found {len(pages)} page files to analyze\n")
    
    all_issues = []
    for f in pages:
        result = check_page(f)
        if result["issues"]:
            all_issues.append(result)
    
    print("=" * 60)
    print("SEO ANALYSIS RESULTS")
    print("=" * 60)
    
    if all_issues:
        issue_counts = {}
        for item in all_issues:
            for issue in item["issues"]:
                issue_counts[issue] = issue_counts.get(issue, 0) + 1
        
        print("\nIssue Summary:")
        for issue, count in sorted(issue_counts.items(), key=lambda x: -x[1]):
            print(f"  [{count}] {issue}")
        
        print(f"\nAffected files ({len(all_issues)}):")
        for item in all_issues[:5]:
            print(f"  - {item['file']}")
        if len(all_issues) > 5:
            print(f"  ... and {len(all_issues) - 5} more")
    else:
        print("\n[OK] No SEO issues found!")
    
    total_issues = sum(len(item["issues"]) for item in all_issues)
    passed = total_issues == 0
    
    output = {
        "script": "seo_checker",
        "project": str(project_path),
        "files_checked": len(pages),
        "files_with_issues": len(all_issues),
        "issues_found": total_issues,
        "passed": passed
    }
    
    print("\n" + json.dumps(output, indent=2))
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
