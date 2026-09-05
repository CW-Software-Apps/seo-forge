---
name: open-graph-social
description: Open Graph protocol, Twitter Cards, social sharing rich previews, WhatsApp and LinkedIn metadata, and social image optimization. Use for social share cards, click-through-rate enhancement, and dynamic social tags in Blazor.
---

# Open Graph & Social Sharing Metadata

> Definitive specification and best practices for Open Graph, Twitter Cards, and social messaging previews (WhatsApp, LinkedIn, Telegram, Slack) in web applications and Blazor.

---

## 1. Specification Matrix

| Platform | Recommended Card Type | Required Meta Tags | Max Image Size | Aspect Ratio |
|---|---|---|---|---|
| **WhatsApp** | Direct Link Card | `og:title`, `og:description`, `og:image` | `< 300 KB` (strict) | `1.91:1` or `1:1` |
| **LinkedIn** | Large Image Preview | `og:title`, `og:description`, `og:image`, `og:url` | `< 5 MB` | `1.91:1` (1200x627) |
| **X (Twitter)** | `summary_large_image` | `twitter:card`, `twitter:title`, `twitter:image` | `< 5 MB` | `2:1` or `1.91:1` |
| **Facebook** | Standard OG Card | `og:title`, `og:description`, `og:image`, `og:type` | `< 8 MB` | `1.91:1` (1200x630) |
| **Slack / Teams** | Unfurl Card | `og:title`, `og:description`, `og:image` | `< 2 MB` | `1.91:1` |

---

## 2. Image Asset Guidelines (1200 x 630 px)

- **Dimensions**: Exactly `1200 x 630` pixels (Aspect ratio 1.91:1).
- **Safe Zone**: Keep all critical text, logos, and focal elements within the central `1000 x 520` safe area to prevent cropping.
- **Format**: High-quality JPG or optimized PNG.
- **Weight**: Under **300 KB** to guarantee WhatsApp and Telegram instant pre-fetching.
- **Protocol**: Image URL **MUST** be absolute and secure (`https://...`). Relative URLs will fail in crawlers.

---

## 3. Standard Tag Template

```html
<!-- Open Graph Primary -->
<meta property="og:site_name" content="CW Software" />
<meta property="og:title" content="CW Software | Soluções em Software e Automação" />
<meta property="og:description" content="Aumente a produtividade e transforme a gestão da sua empresa com as soluções inteligentes da CW Software." />
<meta property="og:url" content="https://cwsoftware.com.br/solucoes" />
<meta property="og:type" content="website" />
<meta property="og:locale" content="pt_BR" />

<!-- Open Graph Image -->
<meta property="og:image" content="https://cwsoftware.com.br/images/og/solucoes-1200x630.jpg" />
<meta property="og:image:secure_url" content="https://cwsoftware.com.br/images/og/solucoes-1200x630.jpg" />
<meta property="og:image:width" content="1200" />
<meta property="og:image:height" content="630" />

<!-- Twitter Cards -->
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="CW Software | Soluções em Software e Automação" />
<meta name="twitter:description" content="Aumente a produtividade e transforme a gestão da sua empresa com as soluções inteligentes da CW Software." />
<meta name="twitter:image" content="https://cwsoftware.com.br/images/og/solucoes-1200x630.jpg" />
```

