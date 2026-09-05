---
name: schema-markup
description: Structured data, Schema.org JSON-LD generation, Rich Snippets, SoftwareApplication, Organization, WebSite, FAQPage, and Breadcrumbs. Use for search visibility, rich results, entity definition, and Blazor JSON-LD integration.
---

# Schema Markup & Structured Data (JSON-LD)

> Comprehensive guide for implementing Schema.org structured data using **JSON-LD** in modern web applications and **Blazor (.NET 8/9/10)** to win Google Rich Snippets and establish machine-readable entity authority.

---

## 1. Core Principles

1. **Format**: Always use **JSON-LD** (JavaScript Object Notation for Linked Data) in `<script type="application/ld+json">`. Do NOT use microdata or RDFa.
2. **Placement**: Inject inside `<HeadContent>` in Blazor or `<head>` in HTML.
3. **Accuracy**: The structured data MUST match the visible content on the page (Google penalizes deceptive markup).
4. **Validation**: Validate with [Google Rich Results Test](https://search.google.com/test/rich-results) and [Schema.org Validator](https://validator.schema.org/).

---

## 2. Essential Schemas for SaaS & Web

### 2.1 `SoftwareApplication`
```json
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "CW Software Suite",
  "operatingSystem": "All modern browsers, Windows, Linux",
  "applicationCategory": "BusinessApplication",
  "description": "Solução inteligente de gestão, automação e software corporativo.",
  "offers": {
    "@type": "Offer",
    "price": "0",
    "priceCurrency": "BRL"
  },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.9",
    "reviewCount": "128"
  }
}
```

### 2.2 `Organization` (Global Root Schema)
```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "CW Software",
  "url": "https://cwsoftware.com.br",
  "logo": "https://cwsoftware.com.br/images/logo.png",
  "contactPoint": {
    "@type": "ContactPoint",
    "telephone": "+55-11-99999-9999",
    "contactType": "customer service",
    "areaServed": "BR",
    "availableLanguage": ["Portuguese"]
  },
  "sameAs": [
    "https://www.linkedin.com/company/cwsoftware",
    "https://github.com/CW-Software-Apps"
  ]
}
```

### 2.3 `WebSite` with Sitelinks SearchBox
```json
{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": "CW Software",
  "url": "https://cwsoftware.com.br",
  "potentialAction": {
    "@type": "SearchAction",
    "target": {
      "@type": "EntryPoint",
      "urlTemplate": "https://cwsoftware.com.br/busca?q={search_term_string}"
    },
    "query-input": "required name=search_term_string"
  }
}
```

### 2.4 `FAQPage` (Maximizes SERP Height)
```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "Como funciona a integração com o CW Software?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "A integração é realizada via API RESTful e conectores nativos, permitindo sincronização automática em tempo real."
      }
    }
  ]
}
```

### 2.5 `BreadcrumbList` (Hierarchical Navigation)
```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {
      "@type": "ListItem",
      "position": 1,
      "name": "Início",
      "item": "https://cwsoftware.com.br/"
    },
    {
      "@type": "ListItem",
      "position": 2,
      "name": "Soluções",
      "item": "https://cwsoftware.com.br/solucoes"
    }
  ]
}
```

---

## 3. Blazor (.NET) JSON-LD Implementation

Use the reusable `<JsonLd>` component:
```razor
<JsonLd SchemaData="@FaqSchema" />

@code {
    private object FaqSchema => new
    {
        context = "https://schema.org",
        type = "FAQPage",
        mainEntity = new[]
        {
            new
            {
                type = "Question",
                name = "Quais os requisitos do sistema?",
                acceptedAnswer = new
                {
                    type = "Answer",
                    text = "Por ser 100% web, basta qualquer navegador moderno com conexão à internet."
                }
            }
        }
    };
}
```
