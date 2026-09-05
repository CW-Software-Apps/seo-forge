# Universal Agent Guidelines (AGENTS.md) - SEO-FORGE Engine

> This file instructs all AI coding agents (**OpenCode**, **Claude Code**, **Cursor**, **Windsurf**, **GitHub Copilot**, **Antigravity**) on mandatory SEO, GEO, and automated remediation standards.

---

## ⚡ PROTOCOLO AUTÔNOMO DE AUDITORIA & CORREÇÃO (Zero Comandos para o Usuário)

Quando o usuário disser qualquer variação de:
- *"audite o SEO deste projeto"*
- *"como tá o SEO?"* ou *"qual a nota de SEO?"*
- *"verifique as pendências de SEO"*
- *"corrija todo o SEO até 100%"* ou *"auto seo"* / *"fix seo"*

👉 **NUNCA peça para o usuário abrir o terminal ou rodar comandos manualmente.**
👉 **VOCÊ (Agente de IA) deve executar o fluxo completo de forma autônoma:**

1. **Passo 1 - Executar a Auditoria em Segundo Plano**:
   - Execute o comando `python scripts/seo_checker.py .` usando sua ferramenta nativa de execução de comandos/terminal (`run_command`, `bash`, `execute`, etc.).
2. **Passo 2 - Ler e Interpretar o Diagnóstico**:
   - Leia a saída do console e o arquivo `seo_report.md` gerado na raiz do projeto.
   - Analise o Score de Saúde (0 a 100) e a lista de arquivos com pendências.
3. **Passo 3 - Decidir e Agir**:
   - **Se o usuário pediu apenas diagnóstico/análise**: apresente o Score de Saúde e resuma os pontos críticos de forma clara e amigável.
   - **Se o usuário pediu para corrigir/resolver**: 
     - Para **Blazor (`.razor`)**: injete `<SeoHeader Title="..." Description="..." />` no topo da página (logo após as diretivas `@page` e `@inject`), com títulos atrativos (50-60 caracteres) e descrições envolventes (150-160 caracteres).
     - Para **HTML/Next.js/React**: injete `<title>`, `<meta name="description">` e Open Graph tags.
     - Ajuste hierarquia para conter exatamente um `<h1>` por página.
     - Adicione atributos `alt="..."` descritivos em tags `<img>`.
     - Configure o `appsettings.json` e DI de IndexNow caso apontado no relatório.
4. **Passo 4 - Revalidar Automaticamente**:
   - Execute `python scripts/seo_checker.py .` novamente para verificar a nova nota.
   - Repita o refinamento até atingir **100/100 A+ (Excelente)**.
5. **Passo 5 - Reportar Sucesso**:
   - Informe ao usuário que todas as páginas foram otimizadas e que o score atingiu 100%.

---

## Core Rules & Invariants

### 1. Multi-Framework Metadata
- **Blazor (.NET)**:
  - Every page (`.razor` with `@page`) MUST define `<PageTitle>` and `<meta name="description">` via `<HeadContent>` or `<SeoHeader Title="..." Description="..." />`.
  - In `App.razor`, verify `<HeadOutlet @rendermode="PageRenderMode" />`.
- **HTML / Next.js / React**:
  - Always export metadata (Next.js App Router `metadata` object or Pages Router `<Head>`).
  - Provide `<link rel="canonical" href="..." />`.

### 2. IndexNow Protocol
- When building content management, blog, or product catalog features, always dispatch URL updates to `IIndexNowService.NotifyUrlChangedAsync(url)`.
- Ensure `/{key}.txt` endpoint is accessible.

### 3. Open Graph & Social Cards
- Must include:
  - `og:site_name`, `og:title`, `og:description`, `og:image`, `og:url`, `og:type`
  - `twitter:card` (`summary_large_image`), `twitter:title`, `twitter:description`, `twitter:image`
- All images must use absolute URLs (`https://...`) and `1200x630px` resolution.

### 4. Structured Data (JSON-LD)
- Inject `<script type="application/ld+json">` for entities (`Organization`, `SoftwareApplication`, `FAQPage`, `BreadcrumbList`).
- In Blazor, use `<JsonLd SchemaData="@schema" />`.

### 5. Content Hierarchy
- Exactly **one `<h1>`** per page.
- Do not jump heading levels (e.g. `<h2>` directly to `<h4>`).
- Every `<img>` requires a meaningful `alt` attribute describing the content. Purely decorative images must use `alt=""` and `aria-hidden="true"`.
