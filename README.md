<div align="center">

# 🚀 SEO-FORGE
### Universal SEO & GEO Toolkit for AI Coding Agents
**Win Google Top Rankings & ChatGPT/Perplexity AI Citations in 1 Line of Code**

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/.NET-8%20%7C%209%20%7C%2010-512BD4?logo=dotnet)](https://dotnet.microsoft.com/)
[![Blazor](https://img.shields.io/badge/Blazor-SSR%20%7C%20Interactive-512BD4?logo=blazor)](https://dotnet.microsoft.com/apps/aspnet/web-apps/blazor)
[![Antigravity](https://img.shields.io/badge/Antigravity-Skills%20Ready-4285F4?logo=google)](https://deepmind.google/)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Compatible-D97706?logo=anthropic)](https://claude.ai/)
[![Cursor](https://img.shields.io/badge/Cursor%20%26%20OpenCode-Rules%20Included-000000)](https://cursor.com/)
[![IndexNow](https://img.shields.io/badge/IndexNow-Instant%20Crawl-008080?logo=microsoft-bing)](https://www.bing.com/indexnow)

<p align="center">
  <b>Desenvolvido com excelência pela <a href="https://cwsoftware.com.br">CW Software</a></b>
</p>

[🇧🇷 Português](#-português) • [🇺🇸 English](#-english)

---

</div>

## ⚡ Instalação em 1 Linha (Quickstart)

Abra o terminal na pasta do seu projeto e execute:

### Windows (PowerShell):
```powershell
irm https://raw.githubusercontent.com/CW-Software-Apps/seo-forge/main/install.ps1 | iex
```

### Linux / macOS (Bash):
```bash
curl -fsSL https://raw.githubusercontent.com/CW-Software-Apps/seo-forge/main/install.sh | bash
```

> **O que o instalador faz em 3 segundos:**
> 1. Instala as 5 skills globais do **Antigravity** (`~/.gemini/config/skills/`).
> 2. Detecta se o seu projeto é **Blazor/.NET** e injeta os componentes `<SeoHeader.razor>`, `<JsonLd.razor>` e o serviço C# `IndexNowService.cs`.
> 3. Configura instruções nativas para **Claude Code** (`CLAUDE.md`), **OpenCode/Cursor** (`AGENTS.md`, `.cursor/rules/seo.mdc`) e **GitHub Copilot**.
> 4. Injeta o validador automatizado `seo_checker.py`.

---

# 🇧🇷 Português

O **SEO-FORGE** é o kit definitivo de otimização para motores de busca tradicionais (Google, Bing) e plataformas de busca por Inteligência Artificial (**GEO - Generative Engine Optimization** para ChatGPT Search, Perplexity, Claude, Microsoft Copilot e Google AI Overviews).

### 🎯 Por que o SEO-FORGE é diferente?

A maioria dos pacotes de SEO foca apenas em tags HTML legadas. O **SEO-FORGE** traz:
- ⚡ **IndexNow Nativo**: Notifica o Bing, Copilot e ChatGPT Search instantaneamente quando uma página é criada ou alterada.
- 🌐 **Prerendering & Blazor SSR**: Resolve o problema histórico de páginas Blazor renderizarem vazias para robôs de busca.
- 🤖 **Multi-AI Compatibility**: Funciona nativamente com Google Antigravity, Anthropic Claude Code CLI, Cursor, Windsurf, OpenCode e GitHub Copilot.
- 📊 **GEO Information Gain**: Formatações específicas (definições em blocos, tabelas comparativas, citações) calibradas para que LLMs citem seu software como fonte primária.

---

### 🧩 As 5 Skills Especializadas

| Skill | Escopo | Destaques |
|---|---|---|
| **`technical-seo`** | Infraestrutura & Rastreamento | Protocolo **IndexNow**, Blazor Static SSR, `<HeadOutlet>`, `robots.txt` e `sitemap.xml` dinâmicos, Core Web Vitals (LCP, INP, CLS). |
| **`schema-markup`** | Rich Snippets & Dados Estruturados | Componente `<JsonLd>` e schemas Schema.org: `SoftwareApplication`, `Organization`, `WebSite`, `FAQPage`, `BreadcrumbList`. |
| **`open-graph-social`** | Compartilhamento Social | Cards otimizados para WhatsApp, LinkedIn, Twitter/X, Slack; proporção 1200x630, safe zone central e imagens de alta resolução. |
| **`content-seo`** | Semântica & Redação de Alto CTR | Hierarquia estrita H1-H6, tags HTML5 semânticas (`<main>`, `<article>`), copywriting focado em conversão para Title e Meta Description. |
| **`geo-search-optimization`** | Motores de IA (GEO) | Estratégias para ranquear no ChatGPT Search e Perplexity; pontuação de *information gain*, densidade de entidades e links de autoridade. |

---

### 💻 Exemplo Prático em Blazor (.NET 8/9/10)

Basta usar os componentes gerados pelo **SEO-FORGE** nas suas páginas `.razor`:

```razor
@page "/solucoes/gestao-empresarial"
@using CWSoftware.Web.Components.Shared

<!-- Metadados de SEO, Open Graph e Twitter Cards automáticos -->
<SeoHeader 
    Title="Sistema de Gestão Empresarial ERP"
    Description="Automatize processos, estoque e finanças em tempo real com o ERP em nuvem da CW Software."
    CanonicalUrl="https://cwsoftware.com.br/solucoes/gestao-empresarial"
    OgImage="https://cwsoftware.com.br/images/og/gestao.jpg" />

<!-- Dados Estruturados Schema.org JSON-LD (Rich Snippets) -->
<JsonLd SchemaData="@FaqData" />

<h1>Sistema de Gestão Empresarial ERP em Nuvem</h1>
<p class="lead">Solução integrada para acelerar o crescimento da sua empresa.</p>

@code {
    private object FaqData => new
    {
        context = "https://schema.org",
        type = "FAQPage",
        mainEntity = new[]
        {
            new
            {
                type = "Question",
                name = "Quais os requisitos para utilizar o sistema?",
                acceptedAnswer = new
                {
                    type = "Answer",
                    text = "Acesso através de qualquer navegador moderno em computadores, tablets ou smartphones."
                }
            }
        }
    };
}
```

---

### ⚡ Notificação Instantânea com IndexNow em C#

Quando você criar ou atualizar um produto/artigo no seu banco de dados, dispare a notificação imediata:

```csharp
public class BlogPostService
{
    private readonly IIndexNowService _indexNow;

    public BlogPostService(IIndexNowService indexNow)
    {
        _indexNow = indexNow;
    }

    public async Task PublishPostAsync(BlogPost post)
    {
        // 1. Salva no banco de dados...
        await _db.SaveChangesAsync();

        // 2. Notifica Bing, Copilot e ChatGPT Search instantaneamente!
        await _indexNow.NotifyUrlChangedAsync($"https://cwsoftware.com.br/blog/{post.Slug}");
    }
}
```

---

### 🔍 Auditoria Automatizada

Para rodar uma auditoria completa de SEO e redes sociais no seu código:

```bash
python scripts/seo_checker.py .
```

---

# 🇺🇸 English

**SEO-FORGE** is a unified SEO & GEO (Generative Engine Optimization) toolkit designed for AI coding agents (**Antigravity**, **Claude Code**, **OpenCode**, **Cursor**, **Windsurf**, and **GitHub Copilot**) with first-class support for **Blazor (.NET 8/9/10)** and modern web applications.

### 🌟 Key Highlights
- **IndexNow Protocol**: Instant indexing for Microsoft Bing, Copilot, and ChatGPT Search.
- **Blazor SSR & Prerender First**: Guarantees crawler bots receive fully rendered `<title>`, `<meta>`, and Open Graph tags on the initial HTTP response.
- **Universal Multi-Agent Support**: Out-of-the-box configuration for every major AI coding assistant.
- **GEO Ready**: Optimized for information gain, entity clarity, and direct citations in AI answer engines.

---

## 👥 Compatibilidade de Agentes de IA

| Assistente de IA | Como o SEO-FORGE é Carregado |
|---|---|
| **Google Antigravity** | Skills em `~/.gemini/config/skills/` e agente `@seo-specialist`. |
| **Claude Code CLI** | Regras no `CLAUDE.md` e comandos em `.claude/`. |
| **Cursor / OpenCode** | Regras nativas em `.cursor/rules/seo.mdc` e `AGENTS.md`. |
| **GitHub Copilot** | Instruções de contexto em `.github/copilot-instructions.md`. |

---

## 📄 Licença

Distribuído sob a licença **MIT**. Veja [LICENSE](LICENSE) para mais detalhes.

---

<div align="center">
  <sub>Criado com orgulho pela equipe de engenharia da <b><a href="https://cwsoftware.com.br">CW Software</a></b></sub>
</div>

