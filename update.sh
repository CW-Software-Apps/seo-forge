#!/usr/bin/env bash
# ==============================================================================
# SEO-FORGE: Quick Auto-Updater Script for Linux & macOS
# CW Software (https://cwsoftware.com.br)
# ==============================================================================

set -e
TARGET_DIR="${1:-$(pwd)}"
echo "[*] Updating SEO-Forge in: $TARGET_DIR"

REPO_RAW_BASE="https://raw.githubusercontent.com/CW-Software-Apps/seo-forge/main"

# Re-run install script to pull latest skills and configs
curl -fsSL "$REPO_RAW_BASE/install.sh" | bash -s -- "$TARGET_DIR"

echo "[OK] SEO-Forge updated successfully!"
