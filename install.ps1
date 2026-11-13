# codex-workforce installer (Windows PowerShell)
#
# One command installs, and the same command updates:
#   irm https://raw.githubusercontent.com/odysseyalive/codex-workforce/main/install.ps1 | iex
#
# Scope (default: personal). Set before running, or pass as parameters when running the file:
#   $env:CWF_SCOPE = "project"     # or: .\install.ps1 -Project
#   personal: one copy in $env:CODEX_HOME (default ~\.codex)\codex-workforce, hooks in
#             ~\.codex\hooks.json, skills in ~\.agents\skills. Serves every project.
#   project:  a copy inside the current git repository (.codex\codex-workforce), hooks in
#             .codex\hooks.json, skills in .agents\skills. Travels with the repo.
# Other options: -Uninstall (or $env:CWF_UNINSTALL = "1"), -Force (or $env:CWF_FORCE = "1")
#
# Linux / macOS: use the bash installer instead:
#   bash -c "$(curl -fsSL https://raw.githubusercontent.com/odysseyalive/codex-workforce/main/install)"
#
# The shipped files are listed in manifest.txt (shared with install). Nothing is ever written
# under ~\.claude or .claude, so this installs beside claude-workforce safely.
#
# Test seam: install from a local checkout with no network:
#   $env:CWF_REPO_URL = "file:///C:/path/to/codex-workforce"; .\install.ps1 -User

param(
    [switch]$User,
    [switch]$Project,
    [switch]$Uninstall,
    [switch]$Force
)

$ErrorActionPreference = "Stop"

$RepoUrl = if ($env:CWF_REPO_URL) { $env:CWF_REPO_URL } else { "https://raw.githubusercontent.com/odysseyalive/codex-workforce/main" }
$Scope = if ($Project) { "project" } elseif ($User) { "user" } elseif ($env:CWF_SCOPE) { $env:CWF_SCOPE } else { "user" }
$DoUninstall = $Uninstall -or ($env:CWF_UNINSTALL -eq "1")
$DoForce = $Force -or ($env:CWF_FORCE -eq "1")

function Say($msg) { Write-Host "codex-workforce: $msg" }
function Die($msg) { Write-Host "codex-workforce: $msg" -ForegroundColor Red; exit 1 }

# hooks.json is edited with ConvertFrom-Json -AsHashtable, which PowerShell 7 added.
if ($PSVersionTable.PSVersion.Major -lt 7) {
    Die "PowerShell 7 or newer is required (run this from pwsh, not Windows PowerShell 5.1). Get it with: winget install Microsoft.PowerShell"
}

# ── requirements ──────────────────────────────────────────────────────────────
$Py = $null
foreach ($cand in @("py", "python3", "python")) {
    if (Get-Command $cand -ErrorAction SilentlyContinue) {
        $args3 = if ($cand -eq "py") { @("-3", "-c") } else { @("-c") }
        & $cand @args3 "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)" 2>$null
        if ($LASTEXITCODE -eq 0) { $Py = $cand; break }
    }
}
if (-not $Py) { Die "Python 3.8 or newer is required (the senses are Python 3 scripts)." }
if (-not (Get-Command git -ErrorAction SilentlyContinue)) { Die "git is required." }
if (-not (Get-Command codex -ErrorAction SilentlyContinue)) { Say "note: codex is not on PATH; install OpenAI Codex CLI to use this." }

# ── where things go ───────────────────────────────────────────────────────────
$HomeDir = [Environment]::GetFolderPath("UserProfile")
if ($Scope -eq "project") {
    $Root = (& git rev-parse --show-toplevel 2>$null)
    if (-not $Root) { Die "project scope must be run inside a git repository." }
    $Root = $Root.Trim()
    $ConfDir = Join-Path $Root ".codex"
    $SkillsDir = Join-Path $Root ".agents\skills"
    $InstallDir = Join-Path $ConfDir "codex-workforce"
    # Resolved from the git root at run time, so the hook works wherever the repo is cloned.
    $HookBinPosix = '$(git rev-parse --show-toplevel)/.codex/codex-workforce/cwf/bin/cwf-hook'
    $HookBinWin = '.codex\codex-workforce\cwf\bin\cwf-hook'
} else {
    $ConfDir = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HomeDir ".codex" }
    $SkillsDir = Join-Path $HomeDir ".agents\skills"
    $InstallDir = Join-Path $ConfDir "codex-workforce"
    $HookBinPosix = (Join-Path $InstallDir "cwf/bin/cwf-hook") -replace '\\', '/'
    $HookBinWin = Join-Path $InstallDir "cwf\bin\cwf-hook"
}
$HooksJson = Join-Path $ConfDir "hooks.json"

# ── hooks.json: add or remove only our own entries ───────────────────────────
# Our entries are recognised by their command running cwf-hook; every other hook in the
# file is left exactly as it was.
function Edit-Hooks([string]$Mode) {
    $data = [ordered]@{}
    if (Test-Path $HooksJson) {
        $text = (Get-Content -Raw $HooksJson)
        if ($text -and $text.Trim()) { $data = $text | ConvertFrom-Json -AsHashtable }
    }
    if (-not $data.Contains("hooks")) { $data["hooks"] = [ordered]@{} }
    $hooks = $data["hooks"]
    foreach ($event in @($hooks.Keys)) {
        $groups = @()
        foreach ($group in $hooks[$event]) {
            $kept = @($group["hooks"] | Where-Object { -not ("$($_["command"])" -like "*cwf-hook*") })
            if ($kept.Count -gt 0) { $group["hooks"] = $kept; $groups += ,$group }
        }
        if ($groups.Count -gt 0) { $hooks[$event] = $groups } else { $hooks.Remove($event) }
    }
    if ($Mode -eq "add") {
        function New-Handler($arg, $timeout, $extra) {
            $h = [ordered]@{
                type           = "command"
                command        = "python3 `"$HookBinPosix`" $arg"
                commandWindows = "py -3 `"$HookBinWin`" $arg"
                timeout        = $timeout
            }
            foreach ($k in $extra.Keys) { $h[$k] = $extra[$k] }
            return [ordered]@{ hooks = @($h) }
        }
        foreach ($event in @("UserPromptSubmit", "SubagentStart")) {
            if (-not $hooks.Contains($event)) { $hooks[$event] = @() }
            $hooks[$event] = @($hooks[$event]) + (New-Handler "prompt" 30 @{ additionalContextLimit = 6000 })
        }
        if (-not $hooks.Contains("Stop")) { $hooks["Stop"] = @() }
        $hooks["Stop"] = @($hooks["Stop"]) + (New-Handler "stop" 300 @{ statusMessage = "Checking the turn's claims against its evidence" })
        if (-not $hooks.Contains("SubagentStop")) { $hooks["SubagentStop"] = @() }
        $hooks["SubagentStop"] = @($hooks["SubagentStop"]) + (New-Handler "stop" 300 @{})
    }
    if ($hooks.Count -eq 0) { $data.Remove("hooks") }
    New-Item -ItemType Directory -Force -Path (Split-Path $HooksJson) | Out-Null
    $tmp = "$HooksJson.cwf-tmp"
    ($data | ConvertTo-Json -Depth 20) | Set-Content -Encoding utf8 $tmp
    Move-Item -Force $tmp $HooksJson
}

function Read-Version($path) {
    if (Test-Path $path) { return (Get-Content -Raw $path).Trim() } else { return "unknown" }
}

function Get-Remote([string]$Rel, [string]$Dest) {
    $url = "$RepoUrl/$Rel"
    New-Item -ItemType Directory -Force -Path (Split-Path $Dest) | Out-Null
    if ($url -like "file://*") {
        Copy-Item -Force ([Uri]$url).LocalPath $Dest
    } else {
        Invoke-WebRequest -UseBasicParsing -Uri $url -OutFile $Dest
    }
}

# ── uninstall ────────────────────────────────────────────────────────────────
if ($DoUninstall) {
    $list = Join-Path $InstallDir "installed-skills.txt"
    if (Test-Path $list) {
        # A name must be a single plain cwf-* component that resolves to a direct child of
        # the skills folder: a tampered list could otherwise name ..\ paths and turn this
        # into a recursive delete outside it.
        $skillsFull = [IO.Path]::GetFullPath($SkillsDir)
        foreach ($name in Get-Content $list) {
            if ($name -notmatch '^cwf-[A-Za-z0-9._-]+$' -or $name.Contains("..")) { continue }
            $target = [IO.Path]::GetFullPath((Join-Path $SkillsDir $name))
            if ([IO.Path]::GetDirectoryName($target) -ne $skillsFull) { continue }
            $item = Get-Item -Force -ErrorAction SilentlyContinue $target
            if ($item -and -not ($item.Attributes -band [IO.FileAttributes]::ReparsePoint)) {
                Remove-Item -Recurse -Force $target
            }
        }
    }
    $agentList = Join-Path $InstallDir "installed-agents.txt"
    if (Test-Path $agentList) {
        $agentsFull = [IO.Path]::GetFullPath((Join-Path $ConfDir "agents"))
        foreach ($name in Get-Content $agentList) {
            if ($name -notmatch '^[A-Za-z0-9._-]+\.toml$' -or $name.Contains("..")) { continue }
            $target = [IO.Path]::GetFullPath((Join-Path $agentsFull $name))
            if ([IO.Path]::GetDirectoryName($target) -eq $agentsFull) {
                Remove-Item -Force -ErrorAction SilentlyContinue $target
            }
        }
    }
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue $InstallDir
    if (Test-Path $HooksJson) { Edit-Hooks "remove" }
    Say "removed from $Scope scope ($InstallDir). Other hooks in $HooksJson were kept."
    exit 0
}

# ── fetch ────────────────────────────────────────────────────────────────────
$Stage = Join-Path ([IO.Path]::GetTempPath()) ("cwf-" + [Guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Force -Path $Stage | Out-Null
try {
    try { Get-Remote "manifest.txt" (Join-Path $Stage "manifest.txt") } catch { Die "could not download manifest.txt from $RepoUrl" }

    $Incoming = "unknown"
    try { Get-Remote "VERSION" (Join-Path $Stage "VERSION.in"); $Incoming = Read-Version (Join-Path $Stage "VERSION.in") } catch { }
    $Current = Read-Version (Join-Path $InstallDir "VERSION")
    if (-not $DoForce -and $Incoming -ne "unknown" -and $Current -ne "unknown") {
        if ([version]$Incoming -lt [version]$Current) {
            Die "this would downgrade $Current to $Incoming. Re-run with -Force to do it anyway."
        }
    }

    $files = Join-Path $Stage "files"
    foreach ($line in Get-Content (Join-Path $Stage "manifest.txt")) {
        $path = $line.Trim()
        if (-not $path -or $path.StartsWith("#")) { continue }
        try { Get-Remote $path (Join-Path $files $path) } catch { Die "could not download $path" }
    }

    # ── install ──────────────────────────────────────────────────────────────
    # Replace the install directory whole, so a file dropped from the manifest disappears.
    $New = "$InstallDir.cwf-new"
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue $New
    New-Item -ItemType Directory -Force -Path $New, $SkillsDir | Out-Null
    Get-ChildItem -Force $files | ForEach-Object {
        Copy-Item -Recurse -Force $_.FullName $New
    }
    # cwf\skills is the visible SOURCE for <skills-root>\<name>\, not install-dir content.
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue (Join-Path $New "cwf\skills")
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue $InstallDir
    Move-Item $New $InstallDir

    # The installer directory is a whole replacement, so agents arrive inside it. Capture
    # their names from this staged copy before pruning or moving anything.
    $srcAgents = Join-Path $files "cwf\agents"
    $installedAgents = @()
    if (Test-Path $srcAgents) {
        $installedAgents = @(Get-ChildItem -File $srcAgents -Filter "*.toml" | ForEach-Object { $_.Name })
    }

    $installed = @()
    $srcSkills = Join-Path $files "cwf\skills"
    if (Test-Path $srcSkills) {
        foreach ($skill in Get-ChildItem -Directory $srcSkills) {
            $dest = Join-Path $SkillsDir $skill.Name
            Remove-Item -Recurse -Force -ErrorAction SilentlyContinue $dest
            Copy-Item -Recurse -Force $skill.FullName $dest
            $installed += $skill.Name
        }
    }
    Set-Content -Encoding utf8 (Join-Path $InstallDir "installed-skills.txt") $installed
    # Custom agents are not skills: Codex discovers them only in .codex/agents/.
    if (Test-Path $srcAgents) {
        $agentDir = Join-Path $ConfDir "agents"
        New-Item -ItemType Directory -Force -Path $agentDir | Out-Null
        Get-ChildItem -File $srcAgents -Filter "*.toml" | ForEach-Object {
            Copy-Item -Force $_.FullName (Join-Path $agentDir $_.Name)
            $installedAgents += $_.Name
        }
    }
    Set-Content -Encoding utf8 (Join-Path $InstallDir "installed-agents.txt") $installedAgents

    Edit-Hooks "add"
} finally {
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue $Stage
}

# Make the shipped OpenRouter models selectable. Writes a profile and a merged catalog
# beside config.toml; never changes the default model or provider, and never writes a key.
$catalogTool = Join-Path $InstallDir "cwf\bin\cwf-model-catalog"
if (Test-Path $catalogTool) {
    $args3 = if ($Py -eq "py") { @("-3", $catalogTool, "install", "--config", $ConfDir) } else { @($catalogTool, "install", "--config", $ConfDir) }
    & $Py @args3
    if ($LASTEXITCODE -ne 0) { Say "note: the model catalog step failed; run cwf-model-catalog install by hand" }
}

if ($Current -eq "unknown") { Say "installed $Incoming ($Scope scope) in $InstallDir" }
elseif ($Current -eq $Incoming) { Say "reinstalled $Incoming ($Scope scope) in $InstallDir" }
else { Say "updated $Current -> $Incoming ($Scope scope) in $InstallDir" }
Say "hooks added to $HooksJson; skills in $SkillsDir"
Say "models: select the shipped OpenRouter set with: codex --profile openrouter"
Say "        set `$env:OPENROUTER_API_KEY first; the installer never writes your key"
Say "next: start codex, open /hooks and trust the codex-workforce hooks. They don't run until you do."
