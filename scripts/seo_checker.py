#!/usr/bin/env python3
"""
SEO-FORGE: 360° SEO, Crawlability & GEO Diagnostic Engine
Version: 1.3.0
Audits web applications (Blazor, Razor Pages, ASP.NET Core, HTML, Next.js, React)
and generates detailed diagnostic reports with prioritized AI Action Plans for
coding agents (OpenCode, Claude, Antigravity, Cursor).

Usage:
    python scripts/seo_checker.py [project_path]
    python scripts/seo_checker.py [project_path] --report [report_path.md]
    python scripts/seo_checker.py [project_path] --fix [--host meudominio.com]
    python scripts/seo_checker.py --update
"""

import sys
import os
import json
import re
import argparse
import secrets
from pathlib import Path
from datetime import datetime

VERSION = "1.3.0"
REPO_RAW_BASE = "https://raw.githubusercontent.com/CW-Software-Apps/seo-forge/main"

# Fix Windows console encoding
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

SKIP_DIRS = {
    'node_modules', '.next', 'dist', 'build', '.git', '.github',
    '__pycache__', '.vscode', '.idea', 'coverage', 'test', 'tests',
    '__tests__', 'spec', 'docs', 'documentation', 'examples', 'bin', 'obj', 'data',
    'emailtemplates', 'templates', 'emails', 'mail'
}

SKIP_PATTERNS = [
    'config', 'setup', 'util', 'helper', 'hook', 'context', 'store',
    'service', 'api', 'lib', 'constant', 'type', 'interface', 'mock',
    '.test.', '.spec.', '_test.', '_spec.', 'template', 'partial'
]


def humanize_name(stem: str) -> str:
    """Convert PascalCase or kebab-case to Title Case."""
    s = re.sub(r'([a-z])([A-Z])', r'\1 \2', stem)
    s = s.replace('-', ' ').replace('_', ' ')
    words = [w.capitalize() for w in s.split() if w]
    return " ".join(words) if words else stem


def update_seo_forge(project_path: Path):
    """Auto-update SEO-FORGE to the latest version from GitHub."""
    import urllib.request
    
    print("\n" + "=" * 70)
    print("  🔄 SEO-FORGE - Auto-Update Engine")
    print(f"  Versão Atual: v{VERSION} | CW Software (https://cwsoftware.com.br)")
    print("=" * 70)
    
    # 1. Update Global Skills
    gemini_skills = Path.home() / ".gemini" / "config" / "skills"
    skills = ["technical-seo", "schema-markup", "open-graph-social", "content-seo", "geo-search-optimization"]
    print("\n[*] Atualizando skills globais...")
    for s in skills:
        s_dir = gemini_skills / s
        s_dir.mkdir(parents=True, exist_ok=True)
        target_f = s_dir / "SKILL.md"
        url = f"{REPO_RAW_BASE}/skills/{s}/SKILL.md"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as resp:
                content = resp.read().decode('utf-8')
                target_f.write_text(content, encoding='utf-8')
            print(f"  -> Atualizado: skill {s}")
        except Exception as e:
            print(f"  [!] Aviso: Não foi possível atualizar skill {s}: {e}")
            
    # 2. Update Local Project Files
    print(f"\n[*] Atualizando arquivos do projeto em: {project_path}")
    update_files = [
        ("scripts/seo_checker.py", "scripts/seo_checker.py"),
        (".agent/skills/seo-fundamentals/scripts/seo_checker.py", "scripts/seo_checker.py"),
        ("AGENTS.md", "AGENTS.md"),
        ("CLAUDE.md", "CLAUDE.md"),
        (".cursor/rules/seo.mdc", ".cursor/rules/seo.mdc"),
        (".claude/commands/seo-fix.md", ".claude/commands/seo-fix.md"),
        (".agent/agents/seo-specialist.md", "agents/seo-specialist.md")
    ]
    
    for local_rel, remote_rel in update_files:
        local_path = project_path / local_rel
        if local_path.parent.exists():
            url = f"{REPO_RAW_BASE}/{remote_rel}"
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=10) as resp:
                    content = resp.read().decode('utf-8')
                    local_path.write_text(content, encoding='utf-8')
                print(f"  -> Atualizado: {local_rel}")
            except Exception as e:
                print(f"  [!] Aviso: Não foi possível atualizar {local_rel}: {e}")

    print("\n[OK] SEO-FORGE atualizado com sucesso para a versão mais recente!")
    print("=" * 70 + "\n")
    sys.exit(0)


def _find_web_project(project_path: Path) -> Path | None:
    """Locate the web project directory (csproj) in a .NET solution."""
    csproj_files = []
    for f in project_path.glob("**/*.csproj"):
        if not any(skip in f.parts for skip in SKIP_DIRS):
            csproj_files.append(f)
    if not csproj_files:
        return None
    web = [c for c in csproj_files if "Web" in c.name or "Site" in c.name]
    return (web[0] if web else csproj_files[0]).parent


def _get_template(name: str, script_dir: Path) -> str | None:
    """Read a blazor template from the local seo-forge install, or fetch from GitHub."""
    local = script_dir.parent / "templates" / "blazor" / name
    if local.exists():
        return local.read_text(encoding="utf-8")
    try:
        import urllib.request
        with urllib.request.urlopen(f"{REPO_RAW_BASE}/templates/blazor/{name}") as resp:
            return resp.read().decode("utf-8")
    except Exception as e:
        print(f"  [!] Não foi possível obter o template {name}: {e}")
        return None


INDEXNOW_ENDPOINT_SNIPPET = """
// SEO-FORGE: IndexNow verification endpoint /{key}.txt + Bootstrap API
var indexNowKey = builder.Configuration["IndexNow:Key"];
if (!string.IsNullOrEmpty(indexNowKey))
{
    app.MapGet($"/{indexNowKey}.txt", () => Results.Text(indexNowKey, "text/plain"));

    // One-time bulk submission of existing URLs. Protect with the project's
    // AdminPassword sent in the "x-admin-key" header.
    app.MapPost("/api/seo/indexnow/bootstrap", async (IIndexNowBootstrapService bootstrap, IConfiguration cfg, HttpRequest request, List<string> paths) =>
    {
        var adminKey = cfg["AdminPassword"] ?? Environment.GetEnvironmentVariable("AdminPassword");
        if (string.IsNullOrEmpty(adminKey) || request.Headers["x-admin-key"].FirstOrDefault() != adminKey)
            return Results.Unauthorized();

        var count = await bootstrap.SubmitPathsAsync(paths);
        return Results.Ok(new { submitted = count });
    });
}
""".strip()


# Domains that should never be inferred as the site's production host
_NOISE_HOSTS = (
    "localhost", "127.0.0.1", "0.0.0.0", "example.com", "test.com", "meudominio.com",
    "seusite.com", "yourdomain", "github.com", "raw.githubusercontent", "nuget.org",
    "microsoft.com", "google.com", "googleapis.com", "gstatic.com", "indexnow.org",
    "sitemaps.org", "w3.org", "schema.org", "jquery.com", "jsdelivr.net", "unpkg.com",
    "cdnjs.cloudflare.com", "cloudflare.com", "youtube.com", "youtu.be", "twitter.com",
    "x.com", "instagram.com", "linkedin.com", "facebook.com", "unsplash.com",
    "gravatar.com", "wikipedia.org", "fonts.", "cdn.", "smtp.", "mail.",
)


def _extract_hosts(text: str) -> list:
    """Extract plausible production hostnames from text (URLs)."""
    hosts = re.findall(r'https?://([a-z0-9][a-z0-9.-]*\.[a-z]{2,})(?:[/:\"\s<]|$)', text, re.I)
    return [h.lower().rstrip('.') for h in hosts]


def infer_site_host(project_path: Path) -> str | None:
    """Infer the production host from config keys, robots.txt, sitemap.xml and code.

    Returns None when nothing plausible is found (caller falls back to
    interactive prompt or the --host argument).
    """
    candidates = []

    def add(text: str):
        for h in _extract_hosts(text or ""):
            if not any(n in h for n in _NOISE_HOSTS) and "localhost" not in h:
                candidates.append(h)

    # 1. appsettings*.json common keys (incl. Production variants)
    for af in project_path.glob("**/appsettings*.json"):
        if any(skip in af.parts for skip in SKIP_DIRS):
            continue
        try:
            data = json.loads(af.read_text(encoding="utf-8", errors="ignore"))

            def walk(node, path=""):
                if isinstance(node, dict):
                    for k, v in node.items():
                        yield from walk(v, f"{path}:{k}" if path else k)
                else:
                    yield path, node

            for key, val in walk(data):
                key_last = key.split(":")[-1].lower()
                if key_last in ("host", "baseurl", "siteurl", "domain", "appurl", "applicationurl", "publicurl", "canonicalbase", "canonicalurl", "websiteurl"):
                    if isinstance(val, str) and val:
                        if val.startswith("http"):
                            add(val)
                        else:
                            candidates.append(val.lower().rstrip('/').rstrip('.'))
                elif key_last == "origins":  # CORS origins list
                    for origin in (val if isinstance(val, list) else [val]):
                        if isinstance(origin, str):
                            add(origin)
        except Exception:
            pass

    # 2. Static robots.txt / sitemap.xml often carry absolute URLs
    for pattern in ("**/robots.txt", "**/sitemap.xml"):
        for f in project_path.glob(pattern):
            if any(skip in f.parts for skip in SKIP_DIRS):
                continue
            try:
                add(f.read_text(encoding="utf-8", errors="ignore"))
            except Exception:
                pass

    # 3. Hardcoded absolute URLs in key infrastructure code (sitemap/canonical generation)
    for f in [p for p in project_path.glob("**/*Sitemap*.cs") if not any(s in p.parts for s in SKIP_DIRS)]:
        try:
            add(f.read_text(encoding="utf-8", errors="ignore"))
        except Exception:
            pass

    if not candidates:
        return None

    # Most frequent candidate wins
    best = max(set(candidates), key=candidates.count)
    return best


def fix_indexnow_infrastructure(project_path: Path, host: str | None) -> bool:
    """Auto-fix the IndexNow infrastructure (templates, config, DI, endpoints).

    Returns True if any change was applied. The content-dispatch hook
    (NotifyUrlChangedAsync inside the project's save/publish flow) is
    project-specific and must be wired manually or by an AI agent.
    """
    print("\n" + "=" * 70)
    print("  🛠️  SEO-FORGE - Auto-Fix: IndexNow Infrastructure")
    print("=" * 70)

    script_dir = Path(__file__).resolve().parent
    web_dir = _find_web_project(project_path)
    changed = False

    if web_dir is None:
        print("  [!] Nenhum projeto .NET (csproj) encontrado - auto-fix disponível apenas para Blazor/.NET.")
        return False

    print(f"  Projeto Web detectado: {web_dir.name}\n")

    # 1. Copy service templates
    services_dir = web_dir / "Services"
    services_dir.mkdir(exist_ok=True)
    for tpl_name in ["IIndexNowService.cs", "IndexNowService.cs", "IIndexNowBootstrapService.cs"]:
        dest = services_dir / tpl_name
        if dest.exists():
            print(f"  [SKIP] Services/{tpl_name} já existe")
            continue
        content = _get_template(tpl_name, script_dir)
        if content:
            dest.write_text(content, encoding="utf-8")
            print(f"  [OK] Criado: Services/{tpl_name}")
            changed = True

    # 2. appsettings.json - IndexNow section
    appsettings_path = web_dir / "appsettings.json"
    if appsettings_path.exists():
        try:
            data = json.loads(appsettings_path.read_text(encoding="utf-8"))
            if "IndexNow" not in data or not data["IndexNow"].get("Key"):
                key = data.get("IndexNow", {}).get("Key") or secrets.token_hex(16)
                if not host:
                    host = infer_site_host(project_path)
                    if host:
                        print(f"  [OK] Host inferido automaticamente: {host} (use --host para sobrescrever)")
                if not host:
                    try:
                        host = input("  Host de produção do site (ex: meudominio.com) [localhost]: ").strip()
                    except EOFError:
                        host = ""
                    host = host or "localhost"
                data["IndexNow"] = {"Host": host, "Key": key}
                appsettings_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
                print(f"  [OK] appsettings.json: seção IndexNow adicionada (Host: {host}, Key: {key[:6]}...)")
                print(f"       >>> Registre esta chave no Bing Webmaster / indexnow.org: {key}")
                changed = True
            else:
                print("  [SKIP] appsettings.json: IndexNow já configurado")
        except Exception as e:
            print(f"  [!] appsettings.json não pôde ser modificado: {e}")
    else:
        print("  [!] appsettings.json não encontrado")

    # 3. Program.cs - using, DI and endpoints
    program_candidates = [p for p in web_dir.glob("Program.cs")] or [p for p in web_dir.glob("**/Program.cs") if not any(s in p.parts for s in SKIP_DIRS)]
    program_path = program_candidates[0] if program_candidates else None
    if program_path and program_path.exists():
        content = program_path.read_text(encoding="utf-8")

        if "using CWSoftware.Web.Services;" not in content and "namespace CWSoftware.Web" not in content:
            content = "using CWSoftware.Web.Services;\n" + content
            print("  [OK] Program.cs: using CWSoftware.Web.Services adicionado")
            changed = True

        di_lines = [
            "builder.Services.AddHttpClient<IIndexNowService, IndexNowService>();",
            "builder.Services.AddSingleton<IIndexNowBootstrapService, IndexNowBootstrapService>();",
            "builder.Services.AddHostedService<IndexNowBootstrapService>(p => (IndexNowBootstrapService)p.GetRequiredService<IIndexNowBootstrapService>()); // auto-bootstrap on startup"
        ]
        missing_di = [l for l in di_lines if l not in content]
        if missing_di and "builder.Services" in content:
            # Insert right after the first builder.Services line found
            insert_at = content.index("builder.Services.")
            line_end = content.index("\n", insert_at)
            content = content[:line_end] + "\n" + "\n".join(missing_di) + content[line_end:]
            print(f"  [OK] Program.cs: {len(missing_di)} registro(s) de DI adicionado(s)")
            changed = True
        elif missing_di and "WebApplication.CreateBuilder" in content:
            # Minimal template with no services yet: insert after CreateBuilder line
            insert_at = content.index("WebApplication.CreateBuilder")
            line_end = content.index("\n", insert_at)
            content = content[:line_end] + "\n" + "\n".join(missing_di) + content[line_end:]
            print(f"  [OK] Program.cs: {len(missing_di)} registro(s) de DI adicionado(s)")
            changed = True
        elif not missing_di:
            print("  [SKIP] Program.cs: DI do IndexNow já registrada")
        else:
            print("  [!] Program.cs: padrão 'builder.Services' não encontrado - registre a DI manualmente")

        if "app.Run();" in content and "IndexNow verification endpoint" not in content:
            content = content.replace("app.Run();", INDEXNOW_ENDPOINT_SNIPPET + "\n\napp.Run();", 1)
            print("  [OK] Program.cs: endpoint /{key}.txt + API de bootstrap adicionados")
            changed = True
        elif "IndexNow verification endpoint" in content or "/{indexNowKey}.txt" in content:
            print("  [SKIP] Program.cs: endpoint IndexNow já mapeado")

        if changed or True:
            program_path.write_text(content, encoding="utf-8")
    else:
        print("  [!] Program.cs não encontrado - DI/endpoint devem ser configurados manualmente")

    # Post-fix status: report what remains pending (dispatch is not auto-fixable)
    dispatch_found = False
    cs_all = ""
    for f in [p for p in web_dir.glob("**/*.cs") if not any(s in p.parts for s in SKIP_DIRS)]:
        try:
            cs_all += f.read_text(encoding="utf-8", errors="ignore") + "\n"
        except Exception:
            pass
    for f in [p for p in web_dir.glob("**/*.cs") if not any(s in p.parts for s in SKIP_DIRS)]:
        if "indexnow" in f.name.lower():
            continue
        try:
            if re.search(r'\.NotifyUrls?ChangedAsync\s*\(', f.read_text(encoding="utf-8", errors="ignore")):
                dispatch_found = True
                break
        except Exception:
            pass
    bootstrap_found = "IndexNowBootstrap" in cs_all

    remaining = []
    if not dispatch_found:
        remaining.append(
            "❌ DISPATCH (auto-notify): integração MORTA até o gancho existir.\n"
            "     1. Injete IIndexNowService no serviço que salva conteúdo público (ex: SavePostAsync)\n"
            "     2. Chame NotifyUrlChangedAsync ao publicar/editar (snippet nº 3 em templates/blazor/ProgramSnippets.cs)\n"
            "     3. Ou envie o seo_report.md para sua IA resolver"
        )
    else:
        print("  [OK] Dispatch auto-notify: NotifyUrlChangedAsync já é invocado no fluxo de conteúdo")

    if bootstrap_found:
        print("  [OK] Bootstrap: submissão em lote das URLs existentes configurada (automática no startup)")
    else:
        remaining.append("❌ BOOTSTRAP: submissão one-time das URLs existentes não encontrada (veja snippet nº 4 em templates/blazor/ProgramSnippets.cs)")

    if changed:
        print("""
  [OK] Infraestrutura IndexNow aplicada! Próximos passos:
   1. dotnet build (validar compilação)
   2. Após o deploy, o bootstrap dispara sozinho no primeiro startup.
""")
    elif not remaining:
        print("\n  [OK] Nada a corrigir - infraestrutura IndexNow 100% completa e ativa.")
        print("=" * 70 + "\n")
        return changed

    if remaining:
        print("\n  PENDÊNCIAS que exigem edição de código (não são auto-corrigíveis):")
        for r in remaining:
            print(f"  {r}")

    print("=" * 70 + "\n")
    return changed


def check_technical_infrastructure(project_path: Path) -> dict:
    """Audit Technical SEO: robots.txt, sitemap.xml, IndexNow, DI and Blazor SSR."""
    results = {
        "robots_txt": {"status": False, "detail": "Ausente: arquivo robots.txt ou rota dinâmica não encontrada", "action": "Criar wwwroot/robots.txt apontando para o sitemap.xml"},
        "sitemap_xml": {"status": False, "detail": "Ausente: sitemap.xml não encontrado", "action": "Criar rota dinâmica /sitemap.xml ou arquivo estático"},
        "indexnow_config": {"status": False, "key": None, "host": None, "detail": "IndexNow não configurado no appsettings.json", "action": "Adicionar seção IndexNow com Host e Key no appsettings.json"},
        "indexnow_endpoint": {"status": False, "detail": "Endpoint de validação /{key}.txt não mapeado", "action": "Mapear endpoint GET /{key}.txt retornando a chave em texto puro"},
        "indexnow_di": {"status": False, "detail": "IIndexNowService não registrado na injeção de dependência", "action": "Registrar builder.Services.AddHttpClient<IIndexNowService, IndexNowService>() no Program.cs / Startup.cs"},
        "indexnow_dispatch": {"status": False, "detail": "IIndexNowService registrado mas NotifyUrlChangedAsync nunca é invocado no código (integração morta: nenhum ping é enviado)", "action": "Injetar IIndexNowService no serviço de conteúdo (ex: SavePostAsync) e chamar NotifyUrlChangedAsync ao publicar/editar entidades (ver templates/blazor/ProgramSnippets.cs)"},
        "indexnow_bootstrap": {"status": False, "detail": "Submissão one-time (bootstrap) das URLs existentes não encontrada: conteúdo antigo nunca é reportado ao Bing", "action": "Adicionar IndexNowBootstrapService + botão 'Submit All URLs' no painel admin (ver templates/blazor/ProgramSnippets.cs)"},
        "blazor_headoutlet": {"status": False, "detail": "Nenhum <HeadOutlet /> encontrado em App.razor ou _Host.cshtml", "action": "Adicionar <HeadOutlet /> ou <component type=\"typeof(HeadOutlet)\" /> para suportar SSR de metadados"},
        "schema_jsonld": {"status": False, "count": 0, "detail": "Nenhum schema JSON-LD encontrado", "action": "Adicionar Schema.org (Organization / SoftwareApplication) com componente <JsonLd> ou script"}
    }

    # Gather key infrastructure files
    key_files = []
    for pattern in [
        "**/Program.cs", "**/Startup.cs", "**/Endpoints/*.cs",
        "**/Controllers/*.cs", "**/Middleware/*.cs",
        "**/Components/App.razor", "**/Pages/App.razor",
        "**/Pages/_Host.cshtml", "**/*Host*.cshtml",
        "**/*Sitemap*.*", "**/*Seo*.razor", "**/Components/Layout/*.razor",
        "**/Pages/Shared/_Layout.cshtml", "**/Views/Shared/_Layout.cshtml",
        # Next.js / React / Node
        "**/next.config.js", "**/next.config.ts", "**/next.config.mjs",
        "**/app/robots.ts", "**/app/robots.js", "**/app/sitemap.ts", "**/app/sitemap.js",
        "**/middleware.ts", "**/middleware.js", "**/middleware.py"
    ]:
        for f in project_path.glob(pattern):
            if not any(skip in f.parts for skip in SKIP_DIRS):
                key_files.append(f)

    code_content_all = ""
    for f in key_files:
        try:
            code_content_all += f.read_text(encoding='utf-8', errors='ignore') + "\n"
        except Exception:
            pass

    # 1. Robots.txt (all serving possibilities: static, dynamic route, controller, middleware, framework convention)
    robots_files = [f for f in (
        list(project_path.glob("**/wwwroot/robots.txt")) +
        list(project_path.glob("**/public/robots.txt")) +
        list(project_path.glob("**/robots.txt"))
    ) if not any(skip in f.parts for skip in SKIP_DIRS)]
    if robots_files:
        results["robots_txt"] = {"status": True, "detail": f"Arquivo estático encontrado: {robots_files[0].name}", "action": None}
    elif "robots.txt" in code_content_all:
        results["robots_txt"] = {"status": True, "detail": "Servido dinamicamente (rota/controller/middleware/framework)", "action": None}

    # 2. Sitemap.xml (all serving possibilities: static, dynamic route, controller, middleware, framework convention)
    sitemap_files = [f for f in (
        list(project_path.glob("**/wwwroot/sitemap.xml")) +
        list(project_path.glob("**/public/sitemap.xml")) +
        list(project_path.glob("**/sitemap.xml"))
    ) if not any(skip in f.parts for skip in SKIP_DIRS)]
    if sitemap_files:
        results["sitemap_xml"] = {"status": True, "detail": f"Arquivo estático encontrado: {sitemap_files[0].name}", "action": None}
    elif "sitemap.xml" in code_content_all or "MapSitemapEndpoints" in code_content_all or "generateSitemap" in code_content_all:
        results["sitemap_xml"] = {"status": True, "detail": "Servido dinamicamente (rota/controller/middleware/framework)", "action": None}

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

    # 5b. IndexNow Dispatch (is NotifyUrlChangedAsync actually invoked anywhere?)
    # 5c. IndexNow Bootstrap (one-time bulk submission of existing URLs)
    cs_files = [f for f in project_path.glob("**/*.cs") if not any(skip in f.parts for skip in SKIP_DIRS)]
    cs_content_all = ""
    for f in cs_files:
        try:
            cs_content_all += f.read_text(encoding='utf-8', errors='ignore') + "\n"
        except Exception:
            pass

    indexnow_integrated = results["indexnow_config"]["status"] or results["indexnow_di"]["status"]
    if not indexnow_integrated:
        results["indexnow_dispatch"] = {"status": True, "detail": "IndexNow não configurado - verificação não aplicável", "action": None}
        results["indexnow_bootstrap"] = {"status": True, "detail": "IndexNow não configurado - verificação não aplicável", "action": None}
    else:
        dispatch_found = False
        for f in cs_files:
            if "indexnow" in f.name.lower():
                continue
            try:
                if re.search(r'\.NotifyUrls?ChangedAsync\s*\(', f.read_text(encoding='utf-8', errors='ignore')):
                    dispatch_found = True
                    break
            except Exception:
                pass
        if dispatch_found:
            results["indexnow_dispatch"] = {"status": True, "detail": "NotifyUrlChangedAsync invocado no fluxo de conteúdo (auto-notify ativo)", "action": None}

        if "IndexNowBootstrap" in cs_content_all:
            results["indexnow_bootstrap"] = {"status": True, "detail": "Bootstrap one-time (submissão em lote das URLs existentes) encontrado", "action": None}

    # 6. Blazor HeadOutlet (App.razor or _Host.cshtml)
    host_or_app_files = [f for f in (list(project_path.glob("**/App.razor")) + list(project_path.glob("**/*Host*.cshtml"))) if not any(skip in f.parts for skip in SKIP_DIRS)]
    if host_or_app_files:
        for f in host_or_app_files:
            try:
                content = f.read_text(encoding='utf-8', errors='ignore')
                if "<HeadOutlet" in content or "typeof(HeadOutlet)" in content:
                    results["blazor_headoutlet"] = {"status": True, "detail": f"Presente em {f.name} para SSR de metadados", "action": None}
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
    """Check if file is a routable public or private page."""
    name = file_path.name.lower()
    stem = file_path.stem.lower()
    suffix = file_path.suffix.lower()
    
    if any(skip in name for skip in SKIP_PATTERNS):
        return False
    
    # Ignore partials and layouts starting with underscore
    if name.startswith('_'):
        return False

    # Ignore sitemap xml generators
    if 'sitemap' in stem:
        return False

    # Ignore emails and email templates
    parts = [p.lower() for p in file_path.parts]
    if any(d in parts for d in ['emailtemplates', 'templates', 'emails', 'mail']):
        return False

    if suffix == '.razor':
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                head = "".join([f.readline() for _ in range(25)])
                return '@page' in head
        except Exception:
            return False

    if suffix == '.cshtml':
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                head = "".join([f.readline() for _ in range(25)])
                # Razor Pages use @page
                if '@page' in head:
                    return True
                # MVC views are located in Views/
                if any(p in parts for p in ['views']):
                    return True
        except Exception:
            return False

    page_dirs = ['pages', 'app', 'routes', 'views', 'screens']
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
    """Find routable pages to analyze."""
    patterns = ['**/*.html', '**/*.htm', '**/*.jsx', '**/*.tsx', '**/*.razor', '**/*.cshtml']
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
        return {"file": str(file_path.name), "path": file_path, "is_admin": False, "issues": [f"Erro: {e}"], "suggestions": []}
    
    is_razor = file_path.suffix.lower() == '.razor'
    is_layout = 'Head>' in content or '<head' in content.lower() or 'Layout' in file_path.stem or is_razor or file_path.suffix.lower() == '.cshtml'
    
    # Detect internal admin / private pages
    posix_path = file_path.as_posix().lower()
    is_admin_or_private = any(adm in posix_path for adm in ['/admin/', '/manage/', '/private/', '/internal/', '/dashboard/', '/areas/identity/'])

    # 1. Title tag (Crucial for all pages, including admin tabs)
    has_title = (
        '<title' in content.lower() or 
        'title=' in content.lower() or 
        'ViewData["Title"]' in content or
        'ViewBag.Title' in content or
        'Head>' in content or 
        '<PageTitle>' in content or 
        '<pagetitle' in content.lower() or
        '<seoheader' in content.lower()
    )
    if not has_title and is_layout:
        issues.append("Falta tag <title> ou <PageTitle>")
        if is_admin_or_private:
            ai_suggestions.append(f"Adicionar <PageTitle>{human_title} - Admin</PageTitle> ou ViewData[\"Title\"] = \"{human_title}\"")
        else:
            ai_suggestions.append(f"Adicionar <PageTitle>{human_title} | CW Software</PageTitle> ou usar <SeoHeader Title=\"{human_title}\" />")
    
    # 2. Meta description (Public pages only)
    if not is_admin_or_private:
        has_description = (
            'name="description"' in content.lower() or 
            'name=\'description\'' in content.lower() or
            'description=' in content.lower() or
            'ViewData["Description"]' in content or
            'ViewBag.Description' in content or
            '<seoheader' in content.lower()
        )
        if not has_description and is_layout:
            issues.append("Falta meta description")
            ai_suggestions.append(f"Adicionar meta description de 150-160 caracteres com benefícios e CTA atraente para {human_title}")
    
    # 3. Open Graph tags (Public pages only - admin pages should not generate social cards)
    if not is_admin_or_private:
        has_og = (
            'og:' in content or 
            'property="og:' in content.lower() or
            'ogimage=' in content.lower() or
            'viewdata["ogimage"]' in content.lower() or
            '<seoheader' in content.lower() or
            (file_path.suffix.lower() == '.cshtml' and has_title and has_description)
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
        "is_admin": is_admin_or_private,
        "issues": issues,
        "suggestions": ai_suggestions
    }


def generate_markdown_report(report_path: Path, project_path: Path, tech_audit: dict, pages: list, page_issues: list, score: int, grade: str):
    """Generate a comprehensive Markdown Report with actionable AI prompts."""
    now_str = datetime.now().strftime('%d/%m/%Y às %H:%M:%S')
    
    public_pages = [p for p in pages if not any(adm in p.as_posix().lower() for adm in ['/admin/', '/manage/', '/private/', '/internal/', '/dashboard/', '/areas/identity/'])]
    admin_pages = [p for p in pages if p not in public_pages]

    md = []
    md.append("# 📊 Relatório Diagnóstico SEO 360° & Plano de Ação para IA")
    md.append(f"> **Projeto:** `{project_path.name}` | **Data:** {now_str} | **Auditor:** SEO-FORGE Engine v{VERSION}")
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
        ("indexnow_dispatch", "Disparo IndexNow (NotifyUrlChangedAsync no fluxo de conteúdo)"),
        ("indexnow_bootstrap", "IndexNow Bootstrap (submissão one-time das URLs existentes)"),
        ("blazor_headoutlet", "Blazor SSR (<HeadOutlet /> no App.razor / _Host.cshtml)"),
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
    md.append(f"- **Total de Páginas Analisadas:** `{len(pages)}` (`{len(public_pages)}` públicas, `{len(admin_pages)}` administrativas/internas)")
    md.append(f"- **Páginas com Pendências:** `{len(page_issues)}`")
    md.append("")

    if page_issues:
        md.append("| Arquivo | Tipo | Problemas Detectados | Instrução de Otimização para a IA |")
        md.append("|---|---|---|---|")
        for item in page_issues:
            tipo = "🔒 Admin" if item.get("is_admin") else "🌐 Pública"
            issues_str = "<br>".join([f"• {iss}" for iss in item["issues"]])
            sugg_str = "<br>".join([f"→ {sug}" for sug in item["suggestions"]])
            md.append(f"| `{item['file']}` | {tipo} | {issues_str} | {sugg_str} |")
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
    md.append("2. On-Page: Edite as páginas públicas listadas com pendências inserindo metadados ricos (SeoHeader, PageTitle, meta description de 150-160 caracteres e Open Graph).")
    md.append("3. Semântica: Garanta apenas um <h1> por página e adicione textos alternativos descritivos aos elementos <img>.")
    md.append("4. Ao concluir, execute 'python scripts/seo_checker.py .' no terminal para validar que o score atingiu 100/100.")
    md.append("```")
    md.append("")
    md.append("---")
    md.append(f"<div align=\"center\"><sub>Gerado pelo <b>SEO-FORGE v{VERSION}</b> (CW Software) • <a href=\"https://github.com/CW-Software-Apps/seo-forge\">github.com/CW-Software-Apps/seo-forge</a></sub></div>")

    report_path.write_text("\n".join(md), encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description="SEO-FORGE 360° Diagnostic Engine & AI Task Generator")
    parser.add_argument("project_path", nargs="?", default=".", help="Target project root directory")
    parser.add_argument("--report", nargs="?", const="seo_report.md", default="seo_report.md", help="Path to write Markdown report (default: seo_report.md)")
    parser.add_argument("--version", action="version", version=f"SEO-FORGE v{VERSION}")
    parser.add_argument("--update", action="store_true", help="Atualiza o SEO-FORGE (skills globais, regras de IA e checker) para a versão mais recente do GitHub")
    parser.add_argument("--fix", action="store_true", help="Aplica automaticamente a infraestrutura IndexNow ausente (templates, appsettings, DI, endpoints) em projetos .NET")
    parser.add_argument("--host", help="Host de produção (ex: meudominio.com) usado pelo --fix ao gerar a chave IndexNow")
    args = parser.parse_args()

    project_path = Path(args.project_path).resolve()

    if args.update:
        update_seo_forge(project_path)
        return

    if args.fix:
        fix_indexnow_infrastructure(project_path, args.host)

    print(f"\n{'='*70}")
    print(f"  🚀 SEO-FORGE v{VERSION} - 360° Diagnostic Engine & AI Action Planner")
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
    
    if total_score >= 90:
        grade = "A+ (Excelente)"
        grade_color = "\033[92m"
    elif total_score >= 80:
        grade = "A (Muito Bom)"
        grade_color = "\033[92m"
    elif total_score >= 65:
        grade = "B (Bom)"
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
        ("IndexNow Dispatch (auto-notify)", "indexnow_dispatch"),
        ("IndexNow Bootstrap (bulk submit)", "indexnow_bootstrap"),
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
        for item in page_issues[:8]:
            tag = "[Admin]" if item.get("is_admin") else "[Public]"
            print(f"  - {tag} {item['file']}: {', '.join(item['issues'])}")
        if len(page_issues) > 8:
            print(f"  ... e mais {len(page_issues) - 8} página(s)")

    # Save Markdown Report
    report_file = project_path / args.report
    generate_markdown_report(report_file, project_path, tech_audit, pages, page_issues, total_score, grade)
    print(f"\n📄 Relatório de diagnóstico & Plano de Ação salvo em: {report_file.name}")
    print("💡 Você pode enviar o relatório gerado diretamente para a sua IA resolver as pendências com inteligência contextual.")
    print("🔄 Para atualizar o SEO-FORGE: python scripts/seo_checker.py --update")

    # Interactive offer: auto-fix IndexNow infrastructure when issues were found
    indexnow_pending = any(
        not tech_audit[k]["status"] for k in ("indexnow_config", "indexnow_endpoint", "indexnow_di", "indexnow_dispatch", "indexnow_bootstrap")
    ) and any(
        tech_audit[k].get("detail") != "IndexNow não configurado - verificação não aplicável"
        for k in ("indexnow_dispatch", "indexnow_bootstrap")
    )
    if indexnow_pending and sys.stdin.isatty():
        try:
            answer = input("\n🛠️  Infraestrutura IndexNow pendente. Aplicar auto-fix agora? [s/N]: ").strip().lower()
        except EOFError:
            answer = ""
        if answer in ("s", "sim", "y", "yes"):
            fix_indexnow_infrastructure(project_path, args.host)

    print("=" * 70 + "\n")

    sys.exit(0 if total_score >= 85 else 1)


if __name__ == "__main__":
    main()
