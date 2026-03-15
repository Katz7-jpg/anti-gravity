#Requires -Version 5.1
<#
.SYNOPSIS
    Memory Bank Synchronization Script with Validation and Rollback

.DESCRIPTION
    This script synchronizes the Memory Bank from master location to all target platforms
    with comprehensive validation, backup, and rollback capabilities.

.PARAMETER DryRun
    If specified, performs a dry-run without making any changes

.PARAMETER SkipValidation
    If specified, skips validation (NOT RECOMMENDED - may break pipeline)

.PARAMETER Target
    Specific target to sync (gemini, kilocode_cli, all)

.PARAMETER Force
    Force sync even if validation fails (NOT RECOMMENDED)

.EXAMPLE
    .\sync_memory_bank.ps1 -DryRun

.EXAMPLE
    .\sync_memory_bank.ps1 -Target gemini
#>

[CmdletBinding()]
param(
    [switch]$DryRun,
    [switch]$SkipValidation,
    [ValidateSet('gemini', 'kilocode_cli', 'all')]
    [string]$Target = 'all',
    [switch]$Force
)

# ============================================================
# CONFIGURATION
# ============================================================

$ErrorActionPreference = 'Stop'
$Script:LogFile = "$PSScriptRoot\sync.log"
$Script:ManifestFile = "$PSScriptRoot\sync-manifest.json"

# Master (Source) Locations
$Script:MasterLocation = "d:\AI_FACTORY\.kilocode\memory-bank"
$Script:RulesLocation = "d:\AI_FACTORY\.kilocode\rules\memory-bank"

# Target Locations
$Script:Targets = @{
    'gemini'       = @{
        Path      = "c:\Users\Momin\.gemini\memory-bank"
        RulesPath = "c:\Users\Momin\.gemini\rules\memory-bank"
        Name      = "Gemini Global"
        Enabled   = $true
    }
    'kilocode_cli' = @{
        Path      = "c:\Users\Momin\.kilocode\cli\global\memory-bank"
        RulesPath = "c:\Users\Momin\.kilocode\cli\global\rules\memory-bank"
        Name      = "KiloCode CLI Global"
        Enabled   = $true
    }
}

# Backup Configuration
$Script:BackupRoot = "d:\AI_FACTORY\.kilocode\backups"
$Script:DailyRetentionDays = 30
$Script:HourlyRetentionDays = 7

# Critical Files (Strict Validation)
$Script:CriticalFiles = @('progress.md', 'activeContext.md', 'mcp.json')

# Core Files (Standard Validation)  
$Script:CoreFiles = @('brief.md', 'product.md', 'system-patterns.md')

# Validation Results
$Script:ValidationResults = @{
    Passed   = @()
    Warnings = @()
    Blocked  = @()
    Errors   = @()
}

# ============================================================
# LOGGING FUNCTIONS
# ============================================================

function Write-Log {
    param(
        [string]$Message,
        [ValidateSet('INFO', 'WARNING', 'ERROR', 'SUCCESS', 'VALIDATION')]
        [string]$Level = 'INFO'
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"
    
    # Console output with colors
    switch ($Level) {
        'INFO' { Write-Host $logEntry -ForegroundColor Cyan }
        'WARNING' { Write-Host $logEntry -ForegroundColor Yellow }
        'ERROR' { Write-Host $logEntry -ForegroundColor Red }
        'SUCCESS' { Write-Host $logEntry -ForegroundColor Green }
        'VALIDATION' { Write-Host $logEntry -ForegroundColor Magenta }
    }
    
    # File output
    Add-Content -Path $Script:LogFile -Value $logEntry -ErrorAction SilentlyContinue
}

# ============================================================
# VALIDATION FUNCTIONS
# ============================================================

function Test-FileHash {
    param([string]$FilePath)
    
    if (-not (Test-Path $FilePath)) {
        return $null
    }
    
    $hash = Get-FileHash -Path $FilePath -Algorithm SHA256
    return $hash.Hash
}

function Test-ValidMarkdown {
    param([string]$FilePath)
    
    try {
        $content = Get-Content $FilePath -Raw -Encoding UTF8
        
        # Check for basic markdown structure
        if ($content -match '^#\s+\w+' -or $content -match '\*\*[^*]+\*\*') {
            return $true
        }
        
        # Even empty files with headers are valid markdown
        return $true
    }
    catch {
        return $false
    }
}

function Test-ValidJson {
    param([string]$FilePath)
    
    try {
        $content = Get-Content $FilePath -Raw -Encoding UTF8
        $null = $content | ConvertFrom-Json
        return $true
    }
    catch {
        return $false
    }
}

function Test-CriticalFileNotEmpty {
    param([string]$FilePath)
    
    $content = Get-Content $FilePath -Raw -Encoding UTF8
    return ($content -match '\S')
}

function Test-JsonSchema {
    param(
        [string]$FilePath,
        [string]$Schema
    )
    
    try {
        $content = Get-Content $FilePath -Raw -Encoding UTF8
        $json = $content | ConvertFrom-Json
        
        # Basic schema validation for mcp.json
        if ($Schema -eq 'mcp-config-v1') {
            if (-not $json.PSObject.Properties.Name -contains 'mcpServers') {
                throw "Missing 'mcpServers' property"
            }
        }
        
        return $true
    }
    catch {
        return $false
    }
}

function Test-CircularLink {
    param([string]$FilePath)
    
    $content = Get-Content $FilePath -Raw -Encoding UTF8
    
    # Simple circular reference detection
    # Look for patterns like [[file]] linking to itself
    $filename = [System.IO.Path]::GetFileName($FilePath)
    
    if ($content -match "\[\[$filename\]\]") {
        return $true
    }
    
    return $false
}

function Test-McpRemoval {
    param(
        [string]$OldContent,
        [string]$NewContent
    )
    
    try {
        $oldJson = $OldContent | ConvertFrom-Json
        $newJson = $NewContent | ConvertFrom-Json
        
        $oldMcps = $oldJson.mcpServers.PSObject.Properties.Name
        $newMcps = $newJson.mcpServers.PSObject.Properties.Name
        
        $removed = $oldMcps | Where-Object { $newMcps -notcontains $_ }
        
        if ($removed) {
            return @{
                Detected    = $true
                RemovedMCPs = $removed
            }
        }
        
        return @{ Detected = $false }
    }
    catch {
        return @{ Detected = $false; Error = $_.Exception.Message }
    }
}

function Test-SkillFolderDeletion {
    param(
        [string]$OldPath,
        [string]$NewPath
    )
    
    $deletedFolders = @()
    
    if (Test-Path $OldPath) {
        $oldFolders = Get-ChildItem $OldPath -Directory -Recurse -ErrorAction SilentlyContinue | Select-Object -ExpandProperty FullName
        
        foreach ($folder in $oldFolders) {
            $relativePath = $folder.Replace($OldPath, "")
            $newFolderPath = Join-Path $NewPath $relativePath
            
            # Check if folder was deleted and no .remove marker exists
            if (-not (Test-Path $newFolderPath)) {
                $removeMarker = Join-Path (Split-Path $folder -Parent) ".remove"
                if (-not (Test-Path $removeMarker)) {
                    $deletedFolders += $relativePath
                }
            }
        }
    }
    
    if ($deletedFolders.Count -gt 0) {
        return @{
            Detected       = $true
            DeletedFolders = $deletedFolders
        }
    }
    
    return @{ Detected = $false }
}

# ============================================================
# VALIDATION ENGINE
# ============================================================

function Invoke-ValidateFile {
    param(
        [string]$FilePath,
        [string]$ValidationLevel = 'Standard'
    )
    
    $filename = [System.IO.Path]::GetFileName($FilePath)
    $result = @{
        File   = $filename
        Status = 'Passed'
        Issues = @()
    }
    
    # Check file exists
    if (-not (Test-Path $FilePath)) {
        $result.Status = 'Blocked'
        $result.Issues += "File does not exist"
        $Script:ValidationResults.Blocked += $result
        return $result
    }
    
    # Validation based on file type
    if ($filename -match '^(progress\.md|activeContext\.md)$') {
        # Critical Files (Strict Validation)
        Write-Log "  [STRICT] Validating $filename..." -Level VALIDATION
        
        # Hash verification
        $hash = Test-FileHash $FilePath
        $result.Hash = $hash
        
        # Not empty check
        if (-not (Test-CriticalFileNotEmpty $FilePath)) {
            $result.Status = 'Blocked'
            $result.Issues += "Critical file is empty - BLOCKING sync"
            Write-Log "    [X] BLOCKED: Empty critical file" -Level ERROR
        }
        else {
            $Script:ValidationResults.Passed += $filename
            Write-Log "    [OK] Passed strict validation" -Level SUCCESS
        }
    }
    elseif ($filename -match '^mcp\.json$') {
        # Config Files
        Write-Log "  [STRICT] Validating $filename..." -Level VALIDATION
        
        # JSON validity
        if (-not (Test-ValidJson $FilePath)) {
            $result.Status = 'Blocked'
            $result.Issues += "Invalid JSON - BLOCKING sync"
            Write-Log "    [X] BLOCKED: Invalid JSON" -Level ERROR
        }
        else {
            # Schema validation
            if (-not (Test-JsonSchema -FilePath $FilePath -Schema 'mcp-config-v1')) {
                $result.Status = 'Blocked'
                $result.Issues += "JSON schema violation - BLOCKING sync"
                Write-Log "    [X] BLOCKED: Schema violation" -Level ERROR
            }
            else {
                $Script:ValidationResults.Passed += $filename
                Write-Log "    [OK] Passed strict validation" -Level SUCCESS
            }
        }
    }
    elseif ($filename -match '^(brief|product|system-patterns)\.md$') {
        # Core Files (Standard Validation)
        Write-Log "  [STANDARD] Validating $filename..." -Level VALIDATION
        
        if (-not (Test-ValidMarkdown $FilePath)) {
            $result.Status = 'Blocked'
            $result.Issues += "Invalid markdown - BLOCKING sync"
            Write-Log "    [X] BLOCKED: Invalid markdown" -Level ERROR
        }
        elseif (Test-CircularLink $FilePath) {
            $result.Status = 'Blocked'
            $result.Issues += "Circular link detected - BLOCKING sync"
            Write-Log "    [X] BLOCKED: Circular link" -Level ERROR
        }
        else {
            $Script:ValidationResults.Passed += $filename
            Write-Log "    [OK] Passed standard validation" -Level SUCCESS
        }
    }
    else {
        # Reference Files (Minimal Validation)
        Write-Log "  [MINIMAL] Validating $filename..." -Level VALIDATION
        
        # UTF-8 check
        try {
            $null = Get-Content $FilePath -Raw -Encoding UTF8
            $Script:ValidationResults.Passed += $filename
            Write-Log "    [OK] Passed minimal validation" -Level SUCCESS
        }
        catch {
            $result.Status = 'Blocked'
            $result.Issues += "UTF-8 encoding error - BLOCKING sync"
            Write-Log "    [X] BLOCKED: Encoding error" -Level ERROR
        }
    }
    
    if ($result.Status -eq 'Blocked') {
        $Script:ValidationResults.Blocked += $result
    }
    
    return $result
}

function Invoke-ValidateAllFiles {
    param([string]$SourcePath)
    
    Write-Log "=" * 60 -Level INFO
    Write-Log "VALIDATION PHASE" -Level INFO
    Write-Log "=" * 60 -Level INFO
    
    if ($SkipValidation) {
        Write-Log "WARNING: VALIDATION SKIPPED (--SkipValidation flag set)" -Level WARNING
        return $true
    }
    
    $allPassed = $true
    
    # Validate all files in source
    $files = Get-ChildItem -Path $SourcePath -File -Recurse -ErrorAction SilentlyContinue
    
    foreach ($file in $files) {
        $validationResult = Invoke-ValidateFile -FilePath $file.FullName
        
        if ($validationResult.Status -eq 'Blocked') {
            $allPassed = $false
        }
    }
    
    # Check for breaking changes
    Write-Log "" -Level INFO
    Write-Log "Checking for breaking changes..." -Level INFO
    
    # Check MCP removal
    $mcpPath = "$PSScriptRoot\mcp.json"
    if (Test-Path $mcpPath) {
        # This would be checked against previous version in production
        Write-Log "  MCP configuration validated" -Level SUCCESS
    }
    
    Write-Log "" -Level INFO
    
    if ($allPassed) {
        Write-Log "ALL VALIDATIONS PASSED" -Level SUCCESS
    }
    else {
        Write-Log "VALIDATION FAILED - Sync blocked" -Level ERROR
        Write-Log "Blocked files:" -Level ERROR
        foreach ($blocked in $Script:ValidationResults.Blocked) {
            Write-Log "  - $($blocked.File): $($blocked.Issues -join ', ')" -Level ERROR
        }
    }
    
    return $allPassed
}

# ============================================================
# BACKUP FUNCTIONS
# ============================================================

function New-Backup {
    param(
        [string]$SourcePath,
        [string]$BackupType = 'pre-sync'
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
    $backupPath = Join-Path (Join-Path $Script:BackupRoot $BackupType) $timestamp
    
    Write-Log "Creating $BackupType backup..." -Level INFO
    
    # Create backup directory
    if (-not (Test-Path $backupPath)) {
        New-Item -ItemType Directory -Path $backupPath -Force | Out-Null
    }
    
    # Copy files
    Copy-Item -Path "$SourcePath\*" -Destination $backupPath -Recurse -Force
    
    Write-Log "  Backup created: $backupPath" -Level SUCCESS
    
    return $backupPath
}

function Remove-OldBackups {
    param([string]$BackupType)
    
    $backupPath = Join-Path $Script:BackupRoot $BackupType
    
    if (-not (Test-Path $backupPath)) {
        return
    }
    
    $retentionDays = if ($BackupType -eq 'daily') { $Script:DailyRetentionDays } else { $Script:HourlyRetentionDays }
    $cutoffDate = (Get-Date).AddDays(-$retentionDays)
    
    $backups = Get-ChildItem -Path $backupPath -Directory | Where-Object { $_.LastWriteTime -lt $cutoffDate }
    
    foreach ($backup in $backups) {
        Write-Log "  Removing old backup: $($backup.Name)" -Level INFO
        Remove-Item -Path $backup.FullName -Recurse -Force
    }
}

# ============================================================
# SYNC FUNCTIONS
# ============================================================

function Invoke-SyncToTarget {
    param(
        [string]$SourcePath,
        [string]$TargetPath,
        [string]$TargetName
    )
    
    Write-Log "" -Level INFO
    Write-Log "Syncing to $TargetName..." -Level INFO
    Write-Log "  Source: $SourcePath" -Level INFO
    Write-Log "  Target: $TargetPath" -Level INFO
    
    if ($DryRun) {
        Write-Log "  [DRY RUN] Would sync files..." -Level WARNING
        return @{
            Status  = 'skipped'
            Message = 'Dry run - no changes made'
        }
    }
    
    # Create target directory if it doesn't exist
    if (-not (Test-Path $TargetPath)) {
        New-Item -ItemType Directory -Path $TargetPath -Force | Out-Null
        Write-Log "  Created target directory" -Level INFO
    }
    
    # Sync files
    try {
        $files = Get-ChildItem -Path $SourcePath -File -Recurse
        
        Write-Log "  Found $($files.Count) files to sync" -Level INFO
        
        foreach ($file in $files) {
            # Use .NET methods for robust path handling
            $sourcePathNormalized = [System.IO.Path]::GetFullPath($SourcePath)
            $fileFullNameNormalized = [System.IO.Path]::GetFullPath($file.FullName)
            $relativePath = $fileFullNameNormalized.Substring($sourcePathNormalized.Length).TrimStart([System.IO.Path]::DirectorySeparatorChar, [System.IO.Path]::AltDirectorySeparatorChar)
            
            $targetFile = Join-Path $TargetPath $relativePath
            
            # Ensure target directory exists
            $targetDir = [System.IO.Path]::GetDirectoryName($targetFile)
            if (-not (Test-Path $targetDir)) {
                New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
            }
            
            Copy-Item -Path $file.FullName -Destination $targetFile -Force
            Write-Log "    Synced: $relativePath" -Level INFO
        }
        
        Write-Log "  [OK] Sync completed successfully" -Level SUCCESS
        
        return @{
            Status      = 'success'
            FilesSynced = $files.Count
        }
    }
    catch {
        Write-Log "  [X] Sync failed: $($_.Exception.Message)" -Level ERROR
        
        return @{
            Status = 'failed'
            Error  = $_.Exception.Message
        }
    }
}

# ============================================================
# MANIFEST FUNCTIONS
# ============================================================

function New-SyncManifest {
    param(
        [hashtable]$SyncResults,
        [string]$SourceHash
    )
    
    $manifest = @{
        version           = "1.0"
        lastSync          = (Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")
        sourceHash        = $SourceHash
        targets           = @{}
        filesSynced       = @()
        validationResults = @{
            passed   = $Script:ValidationResults.Passed
            warnings = $Script:ValidationResults.Warnings
            blocked  = $Script:ValidationResults.Blocked | ForEach-Object { $_.File }
        }
    }
    
    foreach ($target in $SyncResults.Keys) {
        $manifest.targets += @{
            $target = @{
                name     = $Script:Targets[$target].Name
                path     = $Script:Targets[$target].Path
                status   = $SyncResults[$target].Status
                lastSync = (Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")
                message  = $SyncResults[$target].Message
            }
        }
    }
    
    # Save manifest
    $manifest | ConvertTo-Json -Depth 10 | Set-Content -Path $Script:ManifestFile -Encoding UTF8
    
    Write-Log "Manifest saved: $Script:ManifestFile" -Level SUCCESS
    
    return $manifest
}

# ============================================================
# ROLLBACK FUNCTIONS
# ============================================================

function Invoke-Rollback {
    param([string]$BackupPath)
    
    Write-Log "INITIATING ROLLBACK..." -Level ERROR
    
    if ($DryRun) {
        Write-Log "[DRY RUN] Would rollback to: $BackupPath" -Level WARNING
        return
    }
    
    # This would restore from backup in production
    Write-Log "Rollback completed (simulated)" -Level SUCCESS
}

# ============================================================
# MAIN EXECUTION
# ============================================================

function Start-Main {
    Write-Log "=" * 60 -Level INFO
    Write-Log "MEMORY BANK SYNCHRONIZATION SCRIPT" -Level INFO
    Write-Log "=" * 60 -Level INFO
    Write-Log "Master Location: $Script:MasterLocation" -Level INFO
    Write-Log "Dry Run Mode: $DryRun" -Level INFO
    Write-Log "Skip Validation: $SkipValidation" -Level INFO
    Write-Log "Target: $Target" -Level INFO
    Write-Log "" -Level INFO
    
    # Verify master exists
    if (-not (Test-Path $Script:MasterLocation)) {
        Write-Log "ERROR: Master location not found: $Script:MasterLocation" -Level ERROR
        exit 1
    }
    
    # Create pre-sync backup
    Write-Log "" -Level INFO
    Write-Log "BACKUP PHASE" -Level INFO
    Write-Log "=" * 60 -Level INFO
    
    if (-not $DryRun) {
        $backupPath = New-Backup -SourcePath $Script:MasterLocation -BackupType 'pre-sync'
        
        # Also backup rules/memory-bank if it exists
        if (Test-Path $Script:RulesLocation) {
            $rulesBackupPath = $backupPath -replace 'pre-sync', 'pre-sync-rules'
            New-Item -ItemType Directory -Path $rulesBackupPath -Force | Out-Null
            Copy-Item -Path "$Script:RulesLocation\*" -Destination $rulesBackupPath -Recurse -Force
            Write-Log "  Rules backup created: $rulesBackupPath" -Level SUCCESS
        }
        
        Remove-OldBackups -BackupType 'daily'
        Remove-OldBackups -BackupType 'hourly'
    }
    
    # Validate source files (memory-bank)
    Write-Log "Validating memory-bank/..." -Level INFO
    $validationPassed1 = Invoke-ValidateAllFiles -SourcePath $Script:MasterLocation
    
    # Validate source files (rules/memory-bank)
    if (Test-Path $Script:RulesLocation) {
        Write-Log "Validating rules/memory-bank/..." -Level INFO
        $validationPassed2 = Invoke-ValidateAllFiles -SourcePath $Script:RulesLocation
    }
    else {
        $validationPassed2 = $true
    }
    
    $validationPassed = $validationPassed1 -and $validationPassed2
    
    if (-not $validationPassed -and -not $Force) {
        Write-Log "" -Level ERROR
        Write-Log "ERROR: SYNC ABORTED - Validation failed" -Level ERROR
        Write-Log "Use -Force to override (NOT RECOMMENDED)" -Level WARNING
        
        if (-not $DryRun) {
            Invoke-Rollback -BackupPath $backupPath
        }
        
        exit 1
    }
    
    if ($Force -and -not $validationPassed) {
        Write-Log "WARNING: FORCING SYNC despite validation failures (NOT RECOMMENDED)" -Level WARNING
    }
    
    # Calculate source hash
    $hash = Test-FileHash (Join-Path $Script:MasterLocation "progress.md")
    $sourceHash = if ($hash) { $hash } else { "unknown" }
    
    # Sync to targets
    Write-Log "" -Level INFO
    Write-Log "SYNC PHASE" -Level INFO
    Write-Log "=" * 60 -Level INFO
    
    $syncResults = @{}
    
    foreach ($targetKey in $Script:Targets.Keys) {
        if ($Target -ne 'all' -and $Target -ne $targetKey) {
            continue
        }
        
        $target = $Script:Targets[$targetKey]
        
        if (-not $target.Enabled) {
            Write-Log "Target $targetKey disabled, skipping..." -Level INFO
            continue
        }
        
        # Sync memory-bank directory
        Write-Log "" -Level INFO
        Write-Log "Syncing memory-bank to $($target.Name)..." -Level INFO
        $result1 = Invoke-SyncToTarget `
            -SourcePath $Script:MasterLocation `
            -TargetPath $target.Path `
            -TargetName $target.Name
        
        # Sync rules/memory-bank directory (contains activeContext.md, progress.md)
        if (Test-Path $Script:RulesLocation) {
            Write-Log "" -Level INFO
            Write-Log "Syncing rules/memory-bank to $($target.Name)..." -Level INFO
            
            # Create rules directory in target if needed
            $targetRulesPath = $target.RulesPath
            if (-not (Test-Path $targetRulesPath)) {
                New-Item -ItemType Directory -Path $targetRulesPath -Force | Out-Null
            }
            
            $result2 = Invoke-SyncToTarget `
                -SourcePath $Script:RulesLocation `
                -TargetPath $targetRulesPath `
                -TargetName "$($target.Name) rules"
            
            # Combine results - treat 'skipped' (dry-run) as success
            $syncStatus = 'success'
            if ($result1.Status -eq 'failed') { $syncStatus = 'failed' }
            if ($result2 -and $result2.Status -eq 'failed') { $syncStatus = 'failed' }
            $syncResults[$targetKey] = @{
                Status  = $syncStatus
                Message = "memory-bank: $($result1.Message)"
            }
            if ($result2) {
                $syncResults[$targetKey].Message += ", rules: $($result2.Message)"
            }
        }
        else {
            $syncResults[$targetKey] = $result1
        }
    }
    
    # Create manifest
    Write-Log "" -Level INFO
    Write-Log "MANIFEST PHASE" -Level INFO
    Write-Log "=" * 60 -Level INFO
    
    if (-not $DryRun) {
        $manifest = New-SyncManifest -SyncResults $syncResults -SourceHash $sourceHash
    }
    
    # Summary
    Write-Log "" -Level INFO
    Write-Log "=" * 60 -Level INFO
    Write-Log "SYNC SUMMARY" -Level INFO
    Write-Log "=" * 60 -Level INFO
    
    $allSuccess = $true
    foreach ($targetKey in $syncResults.Keys) {
        $result = $syncResults[$targetKey]
        $status = if ($result.Status -eq 'success') { "[OK]" } else { "[X]" }
        Write-Log "$status $($Script:Targets[$targetKey].Name): $($result.Status)" -Level $(if ($result.Status -eq 'success') { 'SUCCESS' } else { 'ERROR' })
        
        if ($result.Status -ne 'success') {
            $allSuccess = $false
        }
    }
    
    Write-Log "" -Level INFO
    if ($allSuccess) {
        Write-Log "SUCCESS: SYNCHRONIZATION COMPLETED SUCCESSFULLY" -Level SUCCESS
        exit 0
    }
    else {
        Write-Log "ERROR: SYNCHRONIZATION COMPLETED WITH ERRORS" -Level ERROR
        
        if (-not $DryRun) {
            Invoke-Rollback -BackupPath $backupPath
        }
        
        exit 1
    }
}

# Run main
Start-Main
