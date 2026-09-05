#!/usr/bin/env python3
"""
SEO-FORGE: 360° SEO, Crawlability & GEO Diagnostic Engine
Audits web applications (Blazor, HTML, Next.js) and generates detailed diagnostic
reports with prioritized AI Action Plans for coding agents (OpenCode, Claude, Antigravity, Cursor).

Usage:
    python scripts/seo_checker.py [project_path]
    python scripts/seo_checker.py [project_path] --report [report_path.md]
"""

import sys
import os
import json
import re
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
    """Audit Technical SEO: robots.txt, sitemap.xml, IndexNow, DI and Blazor SSR."""
    results = {
        "robots_txt": {"status": False, "detail": "Ausente: arquivo robots.txt ou rota dinâmica não encontrada", "action": "Criar wwwroot/robots.txt apontando para o sitemap.xml"},
        "sitemap_xml": {"status": False, "detail": "Ausente: sitemap.xml não encontrado", "action": "Criar rota dinâmica /sitemap.xml ou arquivo estático"},
        "indexnow_config": {"status": False, "key": None, "host": None, "detail": "IndexNow não configurado no appsettings.json", "action": "Adicionar seção IndexNow com Host e Key no appsettings.json"},
        "indexnow_endpoint": {"status": False, "detail": "Endpoint de validação /{key}.txt não mapeado", "action": "Mapear endpoint GET /{key}.txt retornando a chave em texto puro"},
        "indexnow_di": {"status": False, "detail": "IIndexNowService não registrado na injeção de dependência", "action": "Registrar builder.Services.AddHttpClient<IIndexNowService, IndexNowService>() no Program.cs"},
        "blazor_headoutlet": {"status": False, "detail": "App.razor não possui <HeadOutlet />", "action": "Adicionar <HeadOutlet /> no <head> do App.razor para suportar SSR de metadados"},
        "schema_jsonld": {"status": False, "count": 0, "detail": "Nenhum schema JSON-LD encontrado", "action": "Adicionar Schema.org (Organization / SoftwareApplication) com componente <JsonLd>"}
    }

    # Gather key infrastructure files
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

    # 1. Robots.txt
    robots_files = [f for f in (list(project_path.glob("**/wwwroot/robots.txt")) + list(project_path.glob("**/robots.txt"))) if not any(skip in f.parts for skip in SKIP_DIRS)]
    if robots_files:
        results["robots_txt"] = {"status": True, "detail": f"Arquivo estático encontrado: {robots_files[0].name}", "action": None}
    elif "/robots.txt" in code_content_all or "robots.txt" in code_content_all:
        results["robots_txt"] = {"status": True, "detail": "Rota dinâmica mapeada no código", "action": None}

    # 2. Sitemap.xml
    sitemap_files = [f for f in (list(project_path.glob("**/wwwroot/sitemap.xml")) + list(project_path.glob("**/sitemap.xml"))) if not any(skip in f.parts for skip in SKIP_DIRS)]
    if sitemap_files:
        results["sitemap_xml"] = {"status": True, "detail": f"Arquivo estático encontrado: {sitemap_files[0].name}", "action": None}
    elif "/sitemap.xml" in code_content_all or "MapSitemapEndpoints" in code_content_all or "sitemap.xml" in code_content_all:
        results["sitemap_xml"] = {"status": True, "detail": "Endpoint dinâmico mapeado no código", "action": None}

    # 3. IndexNow appsettings.json
    appsettings_files = [f for f in project_path.glob("**/appsettings*.json") if not any(skip in f.parts for skip in SKIP_DIRS)]
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
                        "detail": f"Configurado (Host: {in_host}, Chave: {in_key[:6]}...)",
                        "action": None
                    }
                    break
        except Exception:
            pass

    # 4. IndexNow Endpoint
    if results["indexnow_config"]["status"]:
        key = results["indexnow_config"]["key"]
        if f"{key}.txt" in code_content_all or "IndexNow:Key" in code_content_all:
            results["indexnow_endpoint"] = {"status": True, "detail": f"Endpoint /{key[:6]}...txt mapeado", "action": None}
    elif "indexnow" in code_content_all.lower() and ".txt" in code_content_all:
        results["indexnow_endpoint"] = {"status": True, "detail": "Endpoint mapeado via padrão de configuração", "action": None}

    # 5. IndexNow DI
    if "IIndexNowService" in code_content_all and ("AddHttpClient<IIndexNowService" in code_content_all or "AddScoped<IIndexNowService" in code_content_all or "AddTransient<IIndexNowService" in code_content_all):
        results["indexnow_di"] = {"status": True, "detail": "Registrado na Injeção de Dependência", "action": None}
    elif "IndexNowService" in code_content_all and ("AddHttpClient" in code_content_all or "AddScoped" in code_content_all):
        results["indexnow_di"] = {"status": True, "detail": "Serviço registrado na DI", "action": None}

    # 6. Blazor HeadOutlet
    app_razor = [f for f in project_path.glob("**/App.razor") if not any(skip in f.parts for skip in SKIP_DIRS)]
    if app_razor:
        for ar in app_razor:
            try:
                content = ar.read_text(encoding='utf-8', errors='ignore')
                if "<HeadOutlet" in content:
                    results["blazor_headoutlet"] = {"status": True, "detail": "Presente no App.razor para SSR de metadados", "action": None}
                    break
            except Exception:
                pass
    else:
        results["blazor_headoutlet"] = {"status": True, "detail": "Projeto não-Blazor ou gerenciado pelo layout", "action": None}

    # 7. JSON-LD Schemas
    jsonld_matches = re.findall(r'application/ld\+json|<JsonLd', code_content_all, re.I)
    if jsonld_matches:
        results["schema_jsonld"] = {"status": True, "count": len(jsonld_matches), "detail": f"{len(jsonld_matches)} integração(ões) de dados estruturados encontradas", "action": None}

    return results


def is_page_file(file_path: Path) -> bool:
    """Check if file is a routable page or layout."""
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
                head = "".join([f.readline() for _ in range(25)])
                return '@page' in head
        except Exception:
            return False

    if any(d in parts for d in page_dirs):
        return True
    
    page_names = ['page', 'index', 'home', 'about', 'contact', 'blog', 
                  'post', 'article', 'product', 'landing']
    
    if any(p in stem for p in page_names):
        return True
    
    if suffix in ['.html', '.htm']:
        return True
    
    return False


def find_pages(project_path: Path) -> list:
    """Find public pages to analyze."""
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
    """Perform in-depth page diagnostics and formulate actionable AI suggestions."""
    issues = []
    ai_suggestions = []
    human_title = humanize_name(file_path.stem)
    
    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
    except Exception as e:
        return {"file": str(file_path.name), "path": file_path, "issues": [f"Erro: {e}"], "suggestions": []}
    
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
        issues.append("Falta tag <title> ou <PageTitle>")
        ai_suggestions.append(f"Adicionar <PageTitle>{human_title} | CW Software</PageTitle> ou usar <SeoHeader Title=\"{human_title}\" />")
    
    # 2. Meta description
    has_description = (
        'name="description"' in content.lower() or 
        'name=\'description\'' in content.lower() or
        'description=' in content.lower() or
        '<seoheader' in content.lower()
    )
    if not has_description and is_layout:
        issues.append("Falta meta description")
        ai_suggestions.append(f"Adicionar meta description de 150-160 caracteres com benefícios e CTA atraente para {human_title}")
    
    # 3. Open Graph tags
    has_og = (
        'og:' in content or 
        'property="og:' in content.lower() or
        'ogimage=' in content.lower() or
        '<seoheader' in content.lower()
    )
    if not has_og and is_layout:
        issues.append("Faltam tags de Open Graph (WhatsApp/LinkedIn/Facebook)")
        ai_suggestions.append("Incluir og:title, og:description, og:image (1200x630px) e twitter:card='summary_large_image'")
    
    # 4. Heading hierarchy
    h1_matches = re.findall(r'<h1[^>]*>', content, re.I)
    if len(h1_matches) > 1:
        issues.append(f"Múltiplos <h1> ({len(h1_matches)} encontrados)")
        ai_suggestions.append("Manter apenas 1 <h1> principal por página e rebaixar os secundários para <h2>")
    
    # 5. Images without alt
    imgs = re.findall(r'<img[^>]+>', content, re.I)
    for img in imgs:
        if 'alt=' not in img.lower():
            issues.append("Imagem sem atributo alt")
            ai_suggestions.append("Adicionar texto descritivo e contextual no atributo alt da imagem para acessibilidade e SEO")
            break
    
    return {
        "file": str(file_path.name),
        "path": file_path,
        "issues": issues,
        "suggestions": ai_suggestions
    }


def generate_markdown_report(report_path: Path, project_path: Path, tech_audit: dict, pages: list, page_issues: list, score: int, grade: str):
    """Generate a comprehensive Markdown Report with actionable AI prompts."""
    now_str = datetime.now().strftime('%d/%m/%Y às %H:%M:%S')
    
    md = []
    md.append("# 📊 Relatório Diagnóstico SEO 360° & Plano de Ação para IA")
    md.append(f"> **Projeto:** `{project_path.name}` | **Data:** {now_str} | **Auditor:** SEO-FORGE Engine")
    md.append("")
    md.append(f"## 🏆 Score Geral de Saúde SEO: **{score}/100** ({grade})")
    md.append("")
    md.append("---")
    md.append("")
    md.append("## 1. 🏗️ Diagnóstico de Infraestrutura Técnica & Rastreamento")
    md.append("")
    md.append("| Recurso | Status | Diagnóstico | Ação Recomendada para a IA |")
    md.append("|---|---|---|---|")
    
    for item_key, item_name in [
        ("robots_txt", "Robots.txt"),
        ("sitemap_xml", "Sitemap.xml"),
        ("indexnow_config", "Configuração IndexNow (appsettings.json)"),
        ("indexnow_endpoint", "Endpoint de Verificação (/{key}.txt)"),
        ("indexnow_di", "Serviço IndexNow em Injeção de Dependência"),
        ("blazor_headoutlet", "Blazor SSR (<HeadOutlet /> no App.razor)"),
        ("schema_jsonld", "Dados Estruturados Schema.org (JSON-LD)")
    ]:
        info = tech_audit[item_key]
        status_icon = "✅ Em Conformidade" if info["status"] else "❌ Requer Ação"
        action_txt = info["action"] if not info["status"] else "Nenhuma ação necessária"
        md.append(f"| **{item_name}** | {status_icon} | {info['detail']} | {action_txt} |")
    
    md.append("")
    md.append("---")
    md.append("")
    md.append("## 2. 📄 Diagnóstico On-Page & Metadados por Página")
    md.append(f"- **Páginas Analisadas:** `{len(pages)}`")
    md.append(f"- **Páginas com Pendências:** `{len(page_issues)}`")
    md.append("")

    if page_issues:
        md.append("| Arquivo | Problemas Detectados | Instrução de Otimização para a IA |")
        md.append("|---|---|---|")
        for item in page_issues:
            issues_str = "<br>".join([f"• {iss}" for iss in item["issues"]])
            sugg_str = "<br>".join([f"→ {sug}" for sug in item["suggestions"]])
            md.append(f"| `{item['file']}` | {issues_str} | {sugg_str} |")
    else:
        md.append("> ✅ **Excelente! Todas as páginas analisadas possuem títulos, meta descriptions, Open Graph e hierarquia de cabeçalhos válidos.**")

    md.append("")
    md.append("---")
    md.append("")
    md.append("## 3. 🤖 Prompt Pronto para Enviar à sua IA (OpenCode / Claude / Antigravity / Cursor)")
    md.append("")
    md.append("Copie e cole o prompt abaixo no chat da sua IA favorita para que ela execute todas as melhorias apontadas neste relatório:")
    md.append("")
    md.append("```text")
    md.append("Olá! Atue como especialista em SEO/GEO e utilize as informações do arquivo seo_report.md para resolver todas as pendências identificadas no projeto:")
    md.append("1. Infraestrutura: Revise a tabela de Infraestrutura Técnica e configure quaisquer itens pendentes (IndexNow, robots.txt, sitemap, DI).")
    md.append("2. On-Page: Edite as páginas listadas com pendências inserindo o componente <SeoHeader> com títulos envolventes (50-60 caracteres) e descrições ricas em benefícios (150-160 caracteres com CTA).")
    md.append("3. Semântica: Garanta apenas um <h1> por página e adicione textos alternativos descritivos aos elementos <img>.")
    md.append("4. Ao concluir, execute 'python scripts/seo_checker.py .' no terminal para validar que o score atingiu 100/100.")
    md.append("```")
    md.append("")
    md.append("---")
    md.append("<div align=\"center\"><sub>Gerado pelo <b>SEO-FORGE</b> (CW Software) • <a href=\"https://github.com/CW-Software-Apps/seo-forge\">github.com/CW-Software-Apps/seo-forge</a></sub></div>")

    report_path.write_text("\n".join(md), encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description="SEO-FORGE 360° Diagnostic Engine & AI Task Generator")
    parser.add_argument("project_path", nargs="?", default=".", help="Target project root directory")
    parser.add_argument("--report", nargs="?", const="seo_report.md", default="seo_report.md", help="Path to write Markdown report (default: seo_report.md)")
    args = parser.parse_args()

    project_path = Path(args.project_path).resolve()

    print(f"\n{'='*70}")
    print(f"  🚀 SEO-FORGE 360° - Diagnostic Engine & AI Action Planner")
    print(f"  CW Software (https://cwsoftware.com.br)")
    print(f"{'='*70}")
    print(f"Projeto: {project_path}")
    print(f"Data:    {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("-" * 70)

    # 1. Technical Audit
    tech_audit = check_technical_infrastructure(project_path)

    # 2. Page Diagnostics
    pages = find_pages(project_path)
    page_issues = []

    for f in pages:
        result = check_page(f)
        if result["issues"]:
            page_issues.append(result)

    # 3. Calculate Score
    tech_score = sum(5 for v in tech_audit.values() if isinstance(v, dict) and v.get("status", False))
    if pages:
        page_ratio = (len(pages) - len(page_issues)) / len(pages)
        page_score = int(page_ratio * 65)
    else:
        page_score = 65

    total_score = min(100, tech_score + page_score)
    
    if total_score >= 95:
        grade = "A+ (Excelente)"
        grade_color = "\033[92m"
    elif total_score >= 85:
        grade = "A (Muito Bom)"
        grade_color = "\033[92m"
    elif total_score >= 70:
        grade = "B (Bom com Alertas)"
        grade_color = "\033[93m"
    else:
        grade = "C (Necessita Atenção)"
        grade_color = "\033[91m"
    end_color = "\033[0m"

    # Terminal Dashboard
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
        detail_txt = tech_audit[key]["detail"][:38]
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

    # Save Markdown Report
    report_file = project_path / args.report
    generate_markdown_report(report_file, project_path, tech_audit, pages, page_issues, total_score, grade)
    print(f"\n📄 Relatório de diagnóstico & Plano de Ação salvo em: {report_file.name}")
    print("💡 Você pode enviar o relatório gerado diretamente para a sua IA resolver as pendências com inteligência contextual.")
    print("=" * 70 + "\n")

    sys.exit(0 if total_score >= 85 else 1)


if __name__ == "__main__":
    main()
