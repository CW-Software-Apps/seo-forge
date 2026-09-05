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

curl -fsSL "$REPO_RAW_BASE/CLAUDE.md" -o "$TARGET_DIR/CLAUDE.md"
curl -fsSL "$REPO_RAW_BASE/AGENTS.md" -o "$TARGET_DIR/AGENTS.md"
curl -fsSL "$REPO_RAW_BASE/.cursor/rules/seo.mdc" -o "$TARGET_DIR/.cursor/rules/seo.mdc"
curl -fsSL "$REPO_RAW_BASE/agents/seo-specialist.md" -o "$TARGET_DIR/.agent/agents/seo-specialist.md"
curl -fsSL "$REPO_RAW_BASE/scripts/seo_checker.py" -o "$TARGET_DIR/.agent/skills/seo-fundamentals/scripts/seo_checker.py"

echo ""
echo "[OK] SEO-Forge installed successfully!"
echo "Audit your project by running: python3 .agent/skills/seo-fundamentals/scripts/seo_checker.py ."
echo ""
