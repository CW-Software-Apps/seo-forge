#!/usr/bin/env python3
"""
SEO-FORGE: Multi-Framework SEO & Metadata Audit + Auto-Fix Tool
Checks and auto-remediates Blazor (.razor), HTML, JSX, and TSX files.

Usage:
    python scripts/seo_checker.py [project_path]
    python scripts/seo_checker.py [project_path] --fix
"""
import sys
import json
import re
import argparse
from pathlib import Path
from datetime import datetime

# Fix Windows console encoding
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except:
    pass

SKIP_DIRS = {
    'node_modules', '.next', 'dist', 'build', '.git', '.github',
    '__pycache__', '.vscode', '.idea', 'coverage', 'test', 'tests',
    '__tests__', 'spec', 'docs', 'documentation', 'examples', 'bin', 'obj'
}

SKIP_PATTERNS = [
    'config', 'setup', 'util', 'helper', 'hook', 'context', 'store',
    'service', 'api', 'lib', 'constant', 'type', 'interface', 'mock',
    '.test.', '.spec.', '_test.', '_spec.'
]


def humanize_name(stem: str) -> str:
    """Convert PascalCase or kebab-case to human readable Title Case."""
    s = re.sub(r'([a-z])([A-Z])', r'\1 \2', stem)
    s = s.replace('-', ' ').replace('_', ' ')
    words = [w.capitalize() for w in s.split() if w]
    return " ".join(words) if words else stem


def is_page_file(file_path: Path) -> bool:
    """Check if this file is likely a public-facing page or layout."""
    name = file_path.name.lower()
    stem = file_path.stem.lower()
    suffix = file_path.suffix.lower()
    
    if any(skip in name for skip in SKIP_PATTERNS):
        return False
    
    parts = [p.lower() for p in file_path.parts]
    page_dirs = ['pages', 'app', 'routes', 'views', 'screens']
    
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
    
    return files[:100]


def check_page(file_path: Path) -> dict:
    """Check a single page for SEO issues."""
    issues = []
    
    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
    except Exception as e:
        return {"file": str(file_path.name), "path": file_path, "issues": [f"Error: {e}"]}
    
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
        "path": file_path,
        "issues": issues
    }


def fix_page(file_path: Path, issues: list) -> bool:
    """Automatically inject SEO tags / components into affected files."""
    if not issues:
        return False
    
    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
    except Exception:
        return False
    
    modified = False
    suffix = file_path.suffix.lower()
    human_title = humanize_name(file_path.stem)
    
    # Fix Blazor files (.razor)
    if suffix == '.razor':
        needs_header = any(iss in issues for iss in [
            "Missing <title> or <PageTitle> tag",
            "Missing meta description",
            "Missing Open Graph tags"
        ])
        
        if needs_header and '<SeoHeader' not in content:
            seo_block = (
                f'\n<SeoHeader \n'
                f'    Title="{human_title}" \n'
                f'    Description="Acesse {human_title} no portal da CW Software com alta segurança e performance." />\n'
            )
            
            # Find directive block at start of razor file
            lines = content.splitlines(keepends=True)
            insert_idx = 0
            for i, line in enumerate(lines):
                stripped = line.strip()
                if (stripped.startswith('@page') or 
                    stripped.startswith('@attribute') or 
                    stripped.startswith('@inject') or 
                    stripped.startswith('@using') or 
                    stripped.startswith('@rendermode') or
                    stripped.startswith('@layout')):
                    insert_idx = i + 1
            
            lines.insert(insert_idx, seo_block)
            content = "".join(lines)
            modified = True
            
    # Fix HTML files (.html / .htm)
    elif suffix in ['.html', '.htm']:
        if '<head>' in content.lower():
            head_tag_match = re.search(r'(<head[^>]*>)', content, re.I)
            if head_tag_match:
                head_tag = head_tag_match.group(1)
                injected_tags = []
                if "Missing <title> or <PageTitle> tag" in issues and '<title>' not in content.lower():
                    injected_tags.append(f'    <title>{human_title} | CW Software</title>')
                if "Missing meta description" in issues and 'name="description"' not in content.lower():
                    injected_tags.append(f'    <meta name="description" content="Soluções empresariais e tecnologia da CW Software." />')
                if "Missing Open Graph tags" in issues and 'property="og:' not in content.lower():
                    injected_tags.append(f'    <meta property="og:title" content="{human_title} | CW Software" />')
                    injected_tags.append(f'    <meta property="og:type" content="website" />')
                
                if injected_tags:
                    replacement = head_tag + "\n" + "\n".join(injected_tags)
                    content = content.replace(head_tag, replacement, 1)
                    modified = True

    # Fix images without alt
    if "Image missing alt attribute" in issues:
        def add_alt(match):
            tag = match.group(0)
            if 'alt=' not in tag.lower():
                return tag[:-1] + f' alt="{human_title} - Imagem ilustrativa">'
            return tag
        new_content = re.sub(r'<img[^>]+>', add_alt, content)
        if new_content != content:
            content = new_content
            modified = True

    if modified:
        try:
            file_path.write_text(content, encoding='utf-8')
            return True
        except Exception:
            return False
            
    return False


def main():
    parser = argparse.ArgumentParser(description="SEO-FORGE Audit & Auto-Fix Tool")
    parser.add_argument("project_path", nargs="?", default=".", help="Target project root directory")
    parser.add_argument("--fix", action="store_true", help="Automatically inject missing SEO headers, meta descriptions, and alt tags")
    args = parser.parse_args()

    project_path = Path(args.project_path).resolve()
    
    print(f"\n{'='*60}")
    print(f"  SEO-FORGE - Search Engine & Social Audit")
    print(f"{'='*60}")
    print(f"Project: {project_path}")
    print(f"Time:    {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Mode:    {'Auto-Fix Enabled (--fix)' if args.fix else 'Audit Only'}")
    print("-" * 60)
    
    pages = find_pages(project_path)
    
    if not pages:
        print("\n[!] No page files found.")
        output = {"script": "seo_checker", "files_checked": 0, "passed": True}
        print("\n" + json.dumps(output, indent=2))
        sys.exit(0)
    
    print(f"Found {len(pages)} page files to analyze\n")
    
    all_issues = []
    fixed_count = 0
    
    for f in pages:
        result = check_page(f)
        if result["issues"]:
            if args.fix:
                if fix_page(f, result["issues"]):
                    fixed_count += 1
                    # Re-check after fix
                    result = check_page(f)
            
            if result["issues"]:
                all_issues.append(result)
    
    if args.fix and fixed_count > 0:
        print(f"[⚡] Auto-remediated {fixed_count} file(s) with missing SEO metadata!\n")

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
            
        print("\nTip: Run with --fix to automatically remediate missing tags:")
        print("  python scripts/seo_checker.py . --fix")
    else:
        print("\n[OK] 100% PERFECT! No SEO issues found across all analyzed pages!")
    
    total_issues = sum(len(item["issues"]) for item in all_issues)
    passed = total_issues == 0
    
    output = {
        "script": "seo_checker",
        "project": str(project_path),
        "files_checked": len(pages),
        "files_with_issues": len(all_issues),
        "issues_found": total_issues,
        "auto_fixed_files": fixed_count,
        "passed": passed
    }
    
    print("\n" + json.dumps(output, indent=2))
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
