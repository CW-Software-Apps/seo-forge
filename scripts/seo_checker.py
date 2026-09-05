#!/usr/bin/env python3
"""
SEO-FORGE: 360° SEO, Crawlability, and GEO Audit Engine
Analyzes:
  1. Technical Infrastructure (Robots.txt, Sitemap.xml, IndexNow Key & DI, Key Verification Endpoint)
  2. Blazor SSR Architecture (HeadOutlet, Static Prerendering)
  3. Structured Data (Schema.org JSON-LD, SoftwareApplication, Organization)
  4. On-Page & Semantic Architecture (PageTitle, Meta Descriptions, H1-H6 Hierarchy)
  5. Social Cards & Media (Open Graph, Twitter Cards, Image Alt Attributes)

Usage:
    python scripts/seo_checker.py [project_path]
    python scripts/seo_checker.py [project_path] --fix
    python scripts/seo_checker.py [project_path] --report [report_path.md]
"""

import sys
import os
import json
import re
import secrets
import argparse
from pathlib import Path
from datetime import datetime

# Fix Windows console encoding
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

SKIP_DIRS = {
    'node_modules', '.next', 'dist', 'build', '.git', '.github',
    '__pycache__', '.vscode', '.idea', 'coverage', 'test', 'tests',
    '__tests__', 'spec', 'docs', 'documentation', 'examples', 'bin', 'obj', 'data'
}

SKIP_PATTERNS = [
    'config', 'setup', 'util', 'helper', 'hook', 'context', 'store',
    'service', 'api', 'lib', 'constant', 'type', 'interface', 'mock',
    '.test.', '.spec.', '_test.', '_spec.'
]


def humanize_name(stem: str) -> str:
    """Convert PascalCase or kebab-case to Title Case."""
    s = re.sub(r'([a-z])([A-Z])', r'\1 \2', stem)
    s = s.replace('-', ' ').replace('_', ' ')
    words = [w.capitalize() for w in s.split() if w]
    return " ".join(words) if words else stem


def check_technical_infrastructure(project_path: Path) -> dict:
    """Audit Technical SEO: robots.txt, sitemap.xml, IndexNow and DI."""
    results = {
        "robots_txt": {"status": False, "detail": "Missing robots.txt"},
        "sitemap_xml": {"status": False, "detail": "Missing sitemap.xml"},
        "indexnow_config": {"status": False, "key": None, "host": None, "detail": "IndexNow not configured in appsettings"},
        "indexnow_endpoint": {"status": False, "detail": "IndexNow key verification endpoint (/{key}.txt) not mapped"},
        "indexnow_di": {"status": False, "detail": "IIndexNowService not registered in dependency injection"},
        "blazor_headoutlet": {"status": False, "detail": "App.razor missing <HeadOutlet />"},
        "schema_jsonld": {"status": False, "count": 0, "detail": "No JSON-LD schemas found"}
    }

    # Gather key files fast without scanning deep dependency folders
    key_files = []
    for pattern in ["**/Program.cs", "**/Endpoints/*.cs", "**/Components/App.razor", "**/*Sitemap*.cs", "**/*Seo*.razor", "**/Components/Layout/*.razor"]:
        for f in project_path.glob(pattern):
            if not any(skip in f.parts for skip in SKIP_DIRS):
                key_files.append(f)

    code_content_all = ""
    for f in key_files:
        try:
            code_content_all += f.read_text(encoding='utf-8', errors='ignore') + "\n"
        except Exception:
            pass

    # 1. Check robots.txt (file or route in Program.cs/Endpoints)
    robots_files = list(project_path.glob("**/wwwroot/robots.txt")) + list(project_path.glob("**/robots.txt"))
    robots_files = [f for f in robots_files if not any(skip in f.parts for skip in SKIP_DIRS)]

    if robots_files:
        results["robots_txt"] = {"status": True, "detail": f"Static file found: {robots_files[0].name}"}
    elif "/robots.txt" in code_content_all or "robots.txt" in code_content_all:
        results["robots_txt"] = {"status": True, "detail": "Dynamic route mapped in code"}

    # 2. Check sitemap.xml (file or route)
    sitemap_files = list(project_path.glob("**/wwwroot/sitemap.xml")) + list(project_path.glob("**/sitemap.xml"))
    sitemap_files = [f for f in sitemap_files if not any(skip in f.parts for skip in SKIP_DIRS)]
    if sitemap_files:
        results["sitemap_xml"] = {"status": True, "detail": f"Static file found: {sitemap_files[0].name}"}
    elif "/sitemap.xml" in code_content_all or "MapSitemapEndpoints" in code_content_all or "sitemap.xml" in code_content_all:
        results["sitemap_xml"] = {"status": True, "detail": "Dynamic endpoint mapped in code"}

    # 3. Check IndexNow in appsettings.json
    appsettings_files = list(project_path.glob("**/appsettings*.json"))
    appsettings_files = [f for f in appsettings_files if not any(skip in f.parts for skip in SKIP_DIRS)]
    
    for af in appsettings_files:
        try:
            data = json.loads(af.read_text(encoding='utf-8', errors='ignore'))
            if "IndexNow" in data and isinstance(data["IndexNow"], dict):
                in_key = data["IndexNow"].get("Key")
                in_host = data["IndexNow"].get("Host")
                if in_key and in_key != "YOUR_HEXADECIMAL_INDEXNOW_KEY_HERE":
                    results["indexnow_config"] = {
                        "status": True,
                        "key": in_key,
                        "host": in_host,
                        "file": str(af.name),
                        "detail": f"Configured (Host: {in_host}, Key: {in_key[:6]}...)"
                    }
                    break
        except Exception:
            pass

    # 4. Check IndexNow Verification Endpoint (/{key}.txt)
    if results["indexnow_config"]["status"]:
        key = results["indexnow_config"]["key"]
        if f"{key}.txt" in code_content_all or "IndexNow:Key" in code_content_all:
            results["indexnow_endpoint"] = {"status": True, "detail": "Verification endpoint mapped for /{key}.txt"}
    elif "indexnow" in code_content_all.lower() and ".txt" in code_content_all:
        results["indexnow_endpoint"] = {"status": True, "detail": "Endpoint mapped via configuration pattern"}

    # 5. Check IndexNow DI registration
    if "IIndexNowService" in code_content_all and ("AddHttpClient<IIndexNowService" in code_content_all or "AddScoped<IIndexNowService" in code_content_all or "AddTransient<IIndexNowService" in code_content_all):
        results["indexnow_di"] = {"status": True, "detail": "Registered in Dependency Injection"}
    elif "IndexNowService" in code_content_all and ("AddHttpClient" in code_content_all or "AddScoped" in code_content_all):
        results["indexnow_di"] = {"status": True, "detail": "Service registered in DI"}

    # 6. Check Blazor HeadOutlet in App.razor
    app_razor = [f for f in project_path.glob("**/App.razor") if not any(skip in f.parts for skip in SKIP_DIRS)]
    if app_razor:
        for ar in app_razor:
            try:
                content = ar.read_text(encoding='utf-8', errors='ignore')
                if "<HeadOutlet" in content:
                    results["blazor_headoutlet"] = {"status": True, "detail": "Present in App.razor for SSR meta rendering"}
                    break
            except Exception:
                pass
    else:
        results["blazor_headoutlet"] = {"status": True, "detail": "Non-Blazor project or layout handles <head>"}

    # 7. Check Structured Data (JSON-LD)
    jsonld_count = len(re.findall(r'application/ld\+json|<JsonLd', code_content_all, re.I))
    if jsonld_count > 0:
        results["schema_jsonld"] = {"status": True, "count": jsonld_count, "detail": f"{jsonld_count} JSON-LD schema integration(s) found"}

    return results


def is_page_file(file_path: Path) -> bool:
    """Check if this file is a public-facing routable page or layout."""
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
        except Exception:
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
    """Find public page files."""
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
    """Check a single page for SEO, heading, and social compliance."""
    issues = []
    warnings = []
    
    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
    except Exception as e:
        return {"file": str(file_path.name), "path": file_path, "issues": [f"Error: {e}"], "warnings": []}
    
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
    imgs = re.findall(r'<img[^>]+>', content, re.I)
    for img in imgs:
        if 'alt=' not in img.lower():
            issues.append("Image missing alt attribute")
            break
        if 'alt=""' in img or "alt=''" in img:
            warnings.append("Image has empty alt attribute (purely decorative)")
            break
    
    return {
        "file": str(file_path.name),
        "path": file_path,
        "issues": issues,
        "warnings": warnings
    }


def fix_page(file_path: Path, issues: list) -> bool:
    """Automatically remediate on-page SEO issues."""
    if not issues:
        return False
    
    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
    except Exception:
        return False
    
    modified = False
    suffix = file_path.suffix.lower()
    human_title = humanize_name(file_path.stem)
    
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


def remediate_technical_infrastructure(project_path: Path, tech_audit: dict) -> list:
    """Auto-remediate robots.txt, IndexNow appsettings, and endpoints."""
    remediations = []

    # 1. Auto-create robots.txt if missing
    if not tech_audit["robots_txt"]["status"]:
        web_dirs = list(project_path.glob("**/wwwroot"))
        target_dir = web_dirs[0] if web_dirs else project_path
        robots_file = target_dir / "robots.txt"
        robots_content = """User-agent: *
Allow: /
Disallow: /admin/
Disallow: /api/

Sitemap: https://cwsoftware.com.br/sitemap.xml
"""
        try:
            robots_file.write_text(robots_content, encoding='utf-8')
            remediations.append("Created wwwroot/robots.txt")
            tech_audit["robots_txt"] = {"status": True, "detail": "Created static robots.txt"}
        except Exception as ex:
            remediations.append(f"Failed to create robots.txt: {ex}")

    # 2. Auto-configure IndexNow in appsettings.json if missing
    if not tech_audit["indexnow_config"]["status"]:
        appsettings_files = list(project_path.glob("**/appsettings.json"))
        appsettings_files = [f for f in appsettings_files if not any(skip in f.parts for skip in SKIP_DIRS)]
        if appsettings_files:
            target_appsettings = appsettings_files[0]
            try:
                data = json.loads(target_appsettings.read_text(encoding='utf-8', errors='ignore'))
                gen_key = secrets.token_hex(16)
                data["IndexNow"] = {
                    "Host": "cwsoftware.com.br",
                    "Key": gen_key
                }
                target_appsettings.write_text(json.dumps(data, indent=4), encoding='utf-8')
                remediations.append(f"Injected IndexNow key into {target_appsettings.name} (Key: {gen_key[:8]}...)")
                tech_audit["indexnow_config"] = {
                    "status": True,
                    "key": gen_key,
                    "host": "cwsoftware.com.br",
                    "detail": f"Configured (Host: cwsoftware.com.br, Key: {gen_key[:6]}...)"
                }
            except Exception as ex:
                remediations.append(f"Failed to update appsettings.json: {ex}")

    # 3. Wire IIndexNowService in Program.cs if missing
    if not tech_audit["indexnow_di"]["status"]:
        program_files = list(project_path.glob("**/Program.cs"))
        program_files = [f for f in program_files if not any(skip in f.parts for skip in SKIP_DIRS)]
        if program_files:
            prog = program_files[0]
            content = prog.read_text(encoding='utf-8', errors='ignore')
            if "AddHttpClient<IIndexNowService" not in content and "builder.Services." in content:
                inject_di = "builder.Services.AddHttpClient<IIndexNowService, IndexNowService>();\n"
                match = re.search(r'(builder\.Services\.[^\n]+;\n)', content)
                if match:
                    content = content[:match.end()] + inject_di + content[match.end():]
                    prog.write_text(content, encoding='utf-8')
                    remediations.append("Registered IIndexNowService in Program.cs DI")
                    tech_audit["indexnow_di"] = {"status": True, "detail": "Registered in Program.cs DI"}

    return remediations


def generate_markdown_report(report_path: Path, project_path: Path, tech_audit: dict, pages: list, page_issues: list, score: int, grade: str):
    """Generate a comprehensive, beautiful Markdown SEO Audit Report."""
    now_str = datetime.now().strftime('%d/%m/%Y às %H:%M:%S')
    
    md = []
    md.append("# 📊 Relatório Completo de Auditoria 360° SEO & Crawlability")
    md.append(f"> **Projeto:** `{project_path.name}` | **Data:** {now_str} | **Engine:** SEO-FORGE v2.0")
    md.append("")
    md.append(f"## 🏆 Score Geral de Saúde SEO: **{score}/100** ({grade})")
    md.append("")
    md.append("---")
    md.append("")
    md.append("## 1. 🏗️ Infraestrutura Técnica & Rastreamento (IndexNow & Bots)")
    md.append("")
    md.append("| Recurso | Status | Detalhes |")
    md.append("|---|---|---|")
    
    for item_key, item_name in [
        ("robots_txt", "Robots.txt"),
        ("sitemap_xml", "Sitemap.xml"),
        ("indexnow_config", "Configuração do IndexNow (appsettings.json)"),
        ("indexnow_endpoint", "Endpoint de Validação de Chave (/{key}.txt)"),
        ("indexnow_di", "Serviço C# IndexNow em Injeção de Dependência"),
        ("blazor_headoutlet", "Blazor SSR (<HeadOutlet /> no App.razor)"),
        ("schema_jsonld", "Dados Estruturados Schema.org (JSON-LD)")
    ]:
        info = tech_audit[item_key]
        status_icon = "✅ Ativo / Em Conformidade" if info["status"] else "❌ Ausente / Pendente"
        md.append(f"| **{item_name}** | {status_icon} | {info['detail']} |")
    
    md.append("")
    md.append("---")
    md.append("")
    md.append("## 2. 📄 Auditoria On-Page & Metadados Sociais")
    md.append(f"- **Páginas e Rotas Analisadas:** `{len(pages)}`")
    md.append(f"- **Páginas com Pendências:** `{len(page_issues)}`")
    md.append("")

    if page_issues:
        md.append("| Arquivo | Pendências Identificadas |")
        md.append("|---|---|")
        for item in page_issues:
            issues_str = "<br>".join([f"• {iss}" for iss in item["issues"]])
            md.append(f"| `{item['file']}` | {issues_str} |")
    else:
        md.append("> ✅ **100% das páginas analisadas estão em conformidade com PageTitle, Meta Description e Open Graph.**")

    md.append("")
    md.append("---")
    md.append("")
    md.append("## 3. 🎯 Recomendações e Próximos Passos")
    if score >= 90:
        md.append("1. **Indexação Instantânea:** O protocolo IndexNow está configurado para avisar Bing, Copilot e ChatGPT Search automaticamente a cada alteração.")
        md.append("2. **Monitoramento:** Acompanhe o Google Search Console e o Bing Webmaster Tools semanalmente para acompanhar a indexação das URLs.")
        md.append("3. **GEO:** Mantenha tabelas comparativas e dados objetivos nas páginas para facilitar citações diretas por inteligências artificiais.")
    else:
        md.append("Execute o modo de auto-remediação para sanar as pendências restantes:")
        md.append("```bash\npython scripts/seo_checker.py . --fix\n```")

    md.append("")
    md.append("---")
    md.append("<div align=\"center\"><sub>Relatório gerado automaticamente pelo <b>SEO-FORGE</b> (CW Software).</sub></div>")

    report_path.write_text("\n".join(md), encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description="SEO-FORGE 360° Comprehensive SEO & Crawlability Audit Engine")
    parser.add_argument("project_path", nargs="?", default=".", help="Target project root directory")
    parser.add_argument("--fix", action="store_true", help="Automatically remediate missing technical configs and on-page tags")
    parser.add_argument("--report", nargs="?", const="seo_report.md", default="seo_report.md", help="Generate detailed Markdown report (default: seo_report.md)")
    args = parser.parse_args()

    project_path = Path(args.project_path).resolve()

    print(f"\n{'='*70}")
    print(f"  🚀 SEO-FORGE 360° - Comprehensive SEO, Crawlability & GEO Audit")
    print(f"  CW Software (https://cwsoftware.com.br)")
    print(f"{'='*70}")
    print(f"Projeto: {project_path}")
    print(f"Data:    {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"Modo:    {'Auto-Remediação Ativada (--fix)' if args.fix else 'Auditoria Completa 360°'}")
    print("-" * 70)

    # 1. Run Technical Infrastructure Audit
    tech_audit = check_technical_infrastructure(project_path)
    
    if args.fix:
        remedies = remediate_technical_infrastructure(project_path, tech_audit)
        if remedies:
            print("\n[⚡ Auto-Remediação Técnica]")
            for rem in remedies:
                print(f"  -> {rem}")

    # 2. Run Page-level Audit
    pages = find_pages(project_path)
    page_issues = []
    fixed_pages = 0

    for f in pages:
        result = check_page(f)
        if result["issues"]:
            if args.fix:
                if fix_page(f, result["issues"]):
                    fixed_pages += 1
                    result = check_page(f)
            if result["issues"]:
                page_issues.append(result)

    # 3. Calculate 360° Score
    # Technical: 35 pts (5 pts per item, total 7 items)
    tech_score = sum(5 for v in tech_audit.values() if isinstance(v, dict) and v.get("status", False))
    
    # Page compliance: 65 pts
    if pages:
        page_ratio = (len(pages) - len(page_issues)) / len(pages)
        page_score = int(page_ratio * 65)
    else:
        page_score = 65

    total_score = min(100, tech_score + page_score)
    
    if total_score >= 95:
        grade = "A+ (Excelente)"
        grade_color = "\033[92m" # Green
    elif total_score >= 85:
        grade = "A (Muito Bom)"
        grade_color = "\033[92m"
    elif total_score >= 70:
        grade = "B (Bom com Alertas)"
        grade_color = "\033[93m" # Yellow
    else:
        grade = "C (Necessita Atenção)"
        grade_color = "\033[91m" # Red
    end_color = "\033[0m"

    # Display Terminal Dashboard
    print(f"\n📊 SCORE GERAL DE SAÚDE SEO: {grade_color}{total_score}/100 - {grade}{end_color}\n")
    
    print("┌" + "─" * 68 + "┐")
    print(f"│ 🏗️  INFRAESTRUTURA TÉCNICA & CRAWLABILITY (Peso: 35%)              │")
    print("├" + "─" * 68 + "┤")
    for name, key in [
        ("Robots.txt", "robots_txt"),
        ("Sitemap.xml", "sitemap_xml"),
        ("IndexNow (appsettings.json)", "indexnow_config"),
        ("IndexNow Endpoint (/{key}.txt)", "indexnow_endpoint"),
        ("IndexNow C# DI Service", "indexnow_di"),
        ("Blazor SSR (<HeadOutlet />)", "blazor_headoutlet"),
        ("Dados Estruturados (JSON-LD)", "schema_jsonld")
    ]:
        status_sym = "✅" if tech_audit[key]["status"] else "❌"
        detail_txt = tech_audit[key]["detail"][:40]
        print(f"│  {status_sym} {name:<32} {detail_txt:<30} │")
    print("└" + "─" * 68 + "┘")

    print("\n┌" + "─" * 68 + "┐")
    print(f"│ 🏷️  AUDITORIA ON-PAGE & REDES SOCIAIS (Peso: 65%)                  │")
    print("├" + "─" * 68 + "┤")
    print(f"│  Páginas Analisadas: {len(pages):<5} | Em Conformidade: {len(pages) - len(page_issues):<5} | Com Falhas: {len(page_issues):<5} │")
    print("└" + "─" * 68 + "┘")

    if page_issues:
        print(f"\n[!] Páginas com pendências ({len(page_issues)}):")
        for item in page_issues[:5]:
            print(f"  - {item['file']}: {', '.join(item['issues'])}")
        if len(page_issues) > 5:
            print(f"  ... e mais {len(page_issues) - 5} página(s)")

    # Generate Markdown Report
    report_file = project_path / args.report
    generate_markdown_report(report_file, project_path, tech_audit, pages, page_issues, total_score, grade)
    print(f"\n📄 Relatório detalhado salvo em: {report_file.name}")
    print("=" * 70 + "\n")

    sys.exit(0 if total_score >= 85 else 1)


if __name__ == "__main__":
    main()
