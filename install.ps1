<#
.SYNOPSIS
    SEO-FORGE: Universal SEO & GEO Installer for Antigravity, Claude Code, OpenCode, Cursor, and Blazor/.NET.

.DESCRIPTION
    Installs SEO skills globally and scaffolds SEO components and agent configurations into the target project.

.EXAMPLE
    irm https://raw.githubusercontent.com/CW-Software-Apps/seo-forge/main/install.ps1 | iex
    .\install.ps1 -Global
    .\install.ps1 -Project
#>

[CmdletBinding()]
param(
    [switch]$Global,
    [switch]$Project,
    [string]$TargetDir = (Get-Location).Path
)

$ErrorActionPreference = "Stop"
$RepoRawBase = "https://raw.githubusercontent.com/CW-Software-Apps/seo-forge/main"

function Write-BrandHeader {
    Write-Host ""
    Write-Host " ===========================================================" -ForegroundColor Cyan
    Write-Host "   SEO-FORGE: Universal SEO & GEO Toolkit for AI Agents      " -ForegroundColor Yellow
    Write-Host "   CW Software (https://cwsoftware.com.br)                   " -ForegroundColor DarkGray
    Write-Host " ===========================================================" -ForegroundColor Cyan
    Write-Host ""
}

Write-BrandHeader

# Default to both if none specified
if (-not $Global -and -not $Project) {
    $Global = $true
    $Project = $true
}

# -------------------------------------------------------------
# 1. Global Installation (Antigravity ~/.gemini/config/skills/)
# -------------------------------------------------------------
if ($Global) {
    Write-Host "[*] Installing SEO-Forge skills globally..." -ForegroundColor Green
    $geminiSkillsPath = Join-Path $env:USERPROFILE ".gemini\config\skills"
    
    $skills = @(
        "technical-seo",
        "schema-markup",
        "open-graph-social",
        "content-seo",
        "geo-search-optimization"
    )

    foreach ($skill in $skills) {
        $skillDir = Join-Path $geminiSkillsPath $skill
        if (-not (Test-Path $skillDir)) {
            New-Item -ItemType Directory -Path $skillDir -Force | Out-Null
        }
        
        $targetFile = Join-Path $skillDir "SKILL.md"
        $localSkillPath = Join-Path $PSScriptRoot "skills\$skill\SKILL.md"

        if (Test-Path $localSkillPath) {
            Copy-Item $localSkillPath $targetFile -Force
        } else {
            $remoteUrl = "$RepoRawBase/skills/$skill/SKILL.md"
            Invoke-RestMethod -Uri $remoteUrl -OutFile $targetFile
        }
        Write-Host "  -> Installed skill: $skill" -ForegroundColor DarkCyan
    }
    Write-Host "[OK] Global skills installed in $geminiSkillsPath" -ForegroundColor Green
    Write-Host ""
}

# -------------------------------------------------------------
# 2. Project Scaffolding
# -------------------------------------------------------------
if ($Project) {
    Write-Host "[*] Scaffolding project at: $TargetDir" -ForegroundColor Green

    # Detect Blazor / .NET project
    $csprojFiles = Get-ChildItem -Path $TargetDir -Filter "*.csproj" -Recurse -Depth 3 -ErrorAction SilentlyContinue
    $isDotNet = ($csprojFiles.Count -gt 0)

    if ($isDotNet) {
        Write-Host "  -> Detected .NET / Blazor solution ($($csprojFiles.Count) project(s) found)" -ForegroundColor Yellow
        
        # Look for Web project or use target
        $webProj = $csprojFiles | Where-Object { $_.Name -like "*Web*" } | Select-Object -First 1
        $baseProjDir = if ($webProj) { $webProj.Directory.FullName } else { $csprojFiles[0].Directory.FullName }

        # 2.1 Copy Blazor Components
        $sharedCompDir = Join-Path $baseProjDir "Components\Shared"
        if (-not (Test-Path $sharedCompDir)) {
            New-Item -ItemType Directory -Path $sharedCompDir -Force | Out-Null
        }

        # 2.2 Copy Services
        $servicesDir = Join-Path $baseProjDir "Services"
        if (-not (Test-Path $servicesDir)) {
            New-Item -ItemType Directory -Path $servicesDir -Force | Out-Null
        }

        $templates = @(
            @{ Name = "SeoHeader.razor"; Dest = (Join-Path $sharedCompDir "SeoHeader.razor"); Remote = "$RepoRawBase/templates/blazor/SeoHeader.razor"; Local = "templates/blazor/SeoHeader.razor" },
            @{ Name = "JsonLd.razor"; Dest = (Join-Path $sharedCompDir "JsonLd.razor"); Remote = "$RepoRawBase/templates/blazor/JsonLd.razor"; Local = "templates/blazor/JsonLd.razor" },
            @{ Name = "IIndexNowService.cs"; Dest = (Join-Path $servicesDir "IIndexNowService.cs"); Remote = "$RepoRawBase/templates/blazor/IIndexNowService.cs"; Local = "templates/blazor/IIndexNowService.cs" },
            @{ Name = "IndexNowService.cs"; Dest = (Join-Path $servicesDir "IndexNowService.cs"); Remote = "$RepoRawBase/templates/blazor/IndexNowService.cs"; Local = "templates/blazor/IndexNowService.cs" }
        )

        foreach ($t in $templates) {
            $localTPath = if ($PSScriptRoot) { Join-Path $PSScriptRoot $t.Local } else { "" }
            if ($localTPath -and (Test-Path $localTPath)) {
                Copy-Item $localTPath $t.Dest -Force
            } else {
                Invoke-RestMethod -Uri $t.Remote -OutFile $t.Dest
            }
            Write-Host "  -> Injected component/service: $($t.Name)" -ForegroundColor DarkCyan
        }
    }

    # 2.3 Setup Multi-AI Agent Rules (Antigravity, Claude, Cursor, OpenCode)
    $agentDir = Join-Path $TargetDir ".agent\agents"
    $skillsTargetDir = Join-Path $TargetDir ".agent\skills"
    $cursorDir = Join-Path $TargetDir ".cursor\rules"
    $scriptsDir = Join-Path $TargetDir ".agent\skills\seo-fundamentals\scripts"
    $rootScriptsDir = Join-Path $TargetDir "scripts"

    @($agentDir, $skillsTargetDir, $cursorDir, $scriptsDir, $rootScriptsDir) | ForEach-Object {
        if (-not (Test-Path $_)) { New-Item -ItemType Directory -Path $_ -Force | Out-Null }
    }

    # Copy / download multi-agent files
    $agentConfigs = @(
        @{ Dest = (Join-Path $TargetDir "CLAUDE.md"); Remote = "$RepoRawBase/CLAUDE.md"; Local = "CLAUDE.md" },
        @{ Dest = (Join-Path $TargetDir "AGENTS.md"); Remote = "$RepoRawBase/AGENTS.md"; Local = "AGENTS.md" },
        @{ Dest = (Join-Path $cursorDir "seo.mdc"); Remote = "$RepoRawBase/.cursor/rules/seo.mdc"; Local = ".cursor/rules/seo.mdc" },
        @{ Dest = (Join-Path $agentDir "seo-specialist.md"); Remote = "$RepoRawBase/agents/seo-specialist.md"; Local = "agents/seo-specialist.md" },
        @{ Dest = (Join-Path $scriptsDir "seo_checker.py"); Remote = "$RepoRawBase/scripts/seo_checker.py"; Local = "scripts/seo_checker.py" },
        @{ Dest = (Join-Path $rootScriptsDir "seo_checker.py"); Remote = "$RepoRawBase/scripts/seo_checker.py"; Local = "scripts/seo_checker.py" }
    )

    foreach ($cfg in $agentConfigs) {
        $localCfgPath = if ($PSScriptRoot) { Join-Path $PSScriptRoot $cfg.Local } else { "" }
        if ($localCfgPath -and (Test-Path $localCfgPath)) {
            Copy-Item $localCfgPath $cfg.Dest -Force
        } else {
            Invoke-RestMethod -Uri $cfg.Remote -OutFile $cfg.Dest
        }
        Write-Host "  -> Injected AI config: $(Split-Path $cfg.Dest -Leaf)" -ForegroundColor DarkCyan
    }

    Write-Host ""
    Write-Host "[OK] Project configured successfully for Antigravity, Claude Code, Cursor, and OpenCode!" -ForegroundColor Green
    Write-Host ""
    Write-Host "To audit your project now, run:" -ForegroundColor Yellow
    Write-Host "  python .agent/skills/seo-fundamentals/scripts/seo_checker.py ." -ForegroundColor White
    Write-Host ""
}

