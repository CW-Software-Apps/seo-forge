#!/usr/bin/env bash
# ==============================================================================
# SEO-FORGE: Universal SEO & GEO Installer for Antigravity, Claude, & OpenCode
# CW Software (https://cwsoftware.com.br)
# ==============================================================================

set -e

REPO_RAW_BASE="https://raw.githubusercontent.com/CW-Software-Apps/seo-forge/main"

echo ""
echo "==========================================================="
echo "  SEO-FORGE: Universal SEO & GEO Toolkit for AI Agents     "
echo "  CW Software (https://cwsoftware.com.br)                  "
echo "==========================================================="
echo ""

TARGET_DIR="${1:-$(pwd)}"
echo "[*] Setting up SEO-Forge in: $TARGET_DIR"

# 1. Global Skills Setup (~/.gemini/config/skills/)
GEMINI_SKILLS="$HOME/.gemini/config/skills"
mkdir -p "$GEMINI_SKILLS"

SKILLS=("technical-seo" "schema-markup" "open-graph-social" "content-seo" "geo-search-optimization")

for skill in "${SKILLS[@]}"; do
    mkdir -p "$GEMINI_SKILLS/$skill"
    curl -fsSL "$REPO_RAW_BASE/skills/$skill/SKILL.md" -o "$GEMINI_SKILLS/$skill/SKILL.md"
    echo "  -> Installed global skill: $skill"
done

# 2. Local Project Setup
mkdir -p "$TARGET_DIR/.agent/agents"
mkdir -p "$TARGET_DIR/.cursor/rules"
mkdir -p "$TARGET_DIR/.agent/skills/seo-fundamentals/scripts"
mkdir -p "$TARGET_DIR/.claude/commands"
mkdir -p "$TARGET_DIR/scripts"

curl -fsSL "$REPO_RAW_BASE/CLAUDE.md" -o "$TARGET_DIR/CLAUDE.md"
curl -fsSL "$REPO_RAW_BASE/AGENTS.md" -o "$TARGET_DIR/AGENTS.md"
curl -fsSL "$REPO_RAW_BASE/.cursor/rules/seo.mdc" -o "$TARGET_DIR/.cursor/rules/seo.mdc"
curl -fsSL "$REPO_RAW_BASE/.claude/commands/seo-fix.md" -o "$TARGET_DIR/.claude/commands/seo-fix.md"
curl -fsSL "$REPO_RAW_BASE/agents/seo-specialist.md" -o "$TARGET_DIR/.agent/agents/seo-specialist.md"
curl -fsSL "$REPO_RAW_BASE/scripts/seo_checker.py" -o "$TARGET_DIR/.agent/skills/seo-fundamentals/scripts/seo_checker.py"
curl -fsSL "$REPO_RAW_BASE/scripts/seo_checker.py" -o "$TARGET_DIR/scripts/seo_checker.py"

echo ""
echo "==========================================================="
echo "  [OK] SEO-FORGE configurado com sucesso!                  "
echo "==========================================================="
echo ""
echo "  🤖 Agora você NÃO precisa rodar comandos manuais no terminal!"
echo "  Abra o chat da sua IA (OpenCode, Claude Code, Antigravity, Cursor) e digite:"
echo ""
echo "    👉 \"audite o SEO deste projeto\""
echo "       ↳ A IA roda o diagnóstico em segundo plano e te mostra a nota 0-100."
echo ""
echo "    👉 \"corrija todo o SEO até 100%\""
echo "       ↳ A IA audita, injeta tags, otimiza páginas e revalida até 100% autônomo."
echo ""
echo "  🔄 Para atualizar o kit futuramente:"
echo "     python3 scripts/seo_checker.py --update"
echo ""

