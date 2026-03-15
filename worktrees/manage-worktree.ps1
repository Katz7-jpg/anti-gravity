# Kilo Code Worktree Manager
# PowerShell script for managing Git worktrees in Kilo Code Agent Manager

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("create", "remove", "list", "prune")]
    [string]$Action,

    [Parameter(Mandatory=$false)]
    [string]$Name,

    [Parameter(Mandatory=$false)]
    [string]$Branch,

    [Parameter(Mandatory=$false)]
    [switch]$Force
)

$WorktreesDir = "D:\AI_FACTORY\worktrees"
$RepoRoot = "D:\AI_FACTORY"

function New-Worktree {
    param([string]$Name, [string]$Branch)

    if (-not $Name) {
        Write-Host "Error: -Name is required for create action" -ForegroundColor Red
        exit 1
    }

    if (-not $Branch) {
        $Branch = $Name.Replace(" ", "-").ToLower()
    }

    $WorktreePath = Join-Path $WorktreesDir $Name

    if (Test-Path $WorktreePath) {
        Write-Host "Error: Worktree '$Name' already exists at $WorktreePath" -ForegroundColor Red
        exit 1
    }

    Write-Host "Creating worktree: $Name" -ForegroundColor Cyan
    Write-Host "  Path: $WorktreePath" -ForegroundColor Gray
    Write-Host "  Branch: $Branch" -ForegroundColor Gray

    Push-Location $RepoRoot
    try {
        git worktree add $WorktreePath -b $Branch
        Write-Host "Success! Worktree created at: $WorktreePath" -ForegroundColor Green
        Write-Host "To navigate: cd $WorktreePath" -ForegroundColor Yellow
    }
    catch {
        Write-Host "Error creating worktree: $_" -ForegroundColor Red
        exit 1
    }
    finally {
        Pop-Location
    }
}

function Remove-Worktree {
    param([string]$Name, [bool]$Force)

    if (-not $Name) {
        Write-Host "Error: -Name is required for remove action" -ForegroundColor Red
        exit 1
    }

    $WorktreePath = Join-Path $WorktreesDir $Name

    if (-not (Test-Path $WorktreePath)) {
        Write-Host "Error: Worktree '$Name' does not exist at $WorktreePath" -ForegroundColor Red
        exit 1
    }

    Write-Host "Removing worktree: $Name" -ForegroundColor Cyan

    Push-Location $RepoRoot
    try {
        if ($Force) {
            git worktree remove --force $WorktreePath
        }
        else {
            git worktree remove $WorktreePath
        }
        Write-Host "Success! Worktree removed: $Name" -ForegroundColor Green
    }
    catch {
        Write-Host "Error removing worktree: $_" -ForegroundColor Red
        Write-Host "Try with -Force flag if worktree has uncommitted changes" -ForegroundColor Yellow
        exit 1
    }
    finally {
        Pop-Location
    }
}

function Get-Worktree {
    Write-Host "Listing all worktrees..." -ForegroundColor Cyan
    Write-Host ""

    Push-Location $RepoRoot
    try {
        git worktree list
    }
    finally {
        Pop-Location
    }
}

function Clear-Worktree {
    Write-Host "Pruning dead worktree references..." -ForegroundColor Cyan

    Push-Location $RepoRoot
    try {
        git worktree prune
        Write-Host "Pruning complete!" -ForegroundColor Green
    }
    finally {
        Pop-Location
    }
}

# Main execution
switch ($Action) {
    "create" { New-Worktree -Name $Name -Branch $Branch }
    "remove" { Remove-Worktree -Name $Name -Force $Force }
    "list"   { Get-Worktree }
    "prune"  { Clear-Worktree }
}
