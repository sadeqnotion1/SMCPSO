[CmdletBinding()]
param(
    [string]$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path,
    [switch]$Apply,
    [switch]$IncludeReservedNames,
    [switch]$IncludeTrackedArtifacts,
    [int]$ListLimit = 50
)

$ErrorActionPreference = "Stop"

function To-RelativePath {
    param(
        [Parameter(Mandatory = $true)][string]$BasePath,
        [Parameter(Mandatory = $true)][string]$TargetPath
    )

    if ($TargetPath.StartsWith($BasePath, [System.StringComparison]::OrdinalIgnoreCase)) {
        return $TargetPath.Substring($BasePath.Length).TrimStart('\', '/')
    }

    return $TargetPath
}

function Get-ArtifactTag {
    param(
        [Parameter(Mandatory = $true)][System.IO.FileInfo]$File
    )

    $name = $File.Name.ToLowerInvariant()
    if ($name.EndsWith(".run.xml")) { return ".run.xml" }
    if ($name.EndsWith(".synctex.gz")) { return ".synctex.gz" }
    if ($name.EndsWith(".fdb_latexmk")) { return ".fdb_latexmk" }
    return $File.Extension.ToLowerInvariant()
}

function Get-TrackedPathSet {
    param(
        [Parameter(Mandatory = $true)][string]$RepoRoot
    )

    $set = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)

    try {
        $inside = (git -C $RepoRoot rev-parse --is-inside-work-tree 2>$null).Trim()
        if ($LASTEXITCODE -ne 0 -or $inside -ne "true") {
            return $set
        }

        git -C $RepoRoot ls-files | ForEach-Object {
            if ([string]::IsNullOrWhiteSpace($_)) { return }
            [void]$set.Add($_.Trim())
        }
    }
    catch {
        return $set
    }

    return $set
}

function Show-Sample {
    param(
        [Parameter(Mandatory = $true)][string]$Header,
        [AllowEmptyCollection()][object[]]$Items = @(),
        [Parameter(Mandatory = $true)][int]$Limit
    )

    if ($Items.Count -le 0) { return }
    Write-Output $Header
    $Items | Select-Object -First $Limit | ForEach-Object { $_.RelPath } | Write-Output
    Write-Output ""
}

function Remove-ReservedPath {
    param(
        [Parameter(Mandatory = $true)][string]$FullPath,
        [Parameter(Mandatory = $true)][string]$Kind
    )

    try {
        Remove-Item -LiteralPath $FullPath -Force -Recurse -ErrorAction Stop
        return $true
    }
    catch {
        # Fall back to extended-path deletion for reserved names on Windows.
    }

    $extended = "\\?\$FullPath"
    if ($Kind -eq "Directory") {
        cmd /c "rmdir /s /q ""$extended""" | Out-Null
    }
    else {
        cmd /c "del /f /q ""$extended""" | Out-Null
    }

    return ($LASTEXITCODE -eq 0)
}

$artifactTags = @(
    ".aux", ".log", ".out", ".toc", ".nav", ".snm", ".vrb",
    ".bbl", ".blg", ".bcf", ".fls", ".fdb_latexmk", ".run.xml", ".synctex.gz"
)

$reservedNames = @(
    "CON", "PRN", "AUX", "NUL",
    "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
    "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"
)

$tracked = Get-TrackedPathSet -RepoRoot $Root
$isRepo = $tracked.Count -gt 0

$files = Get-ChildItem -Path $Root -Recurse -Force -File -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -notmatch "\\\.git\\" }

$artifactCandidates = $files | Where-Object {
    $tag = Get-ArtifactTag -File $_
    $artifactTags -contains $tag
}

$artifactTargets = New-Object System.Collections.Generic.List[object]
$artifactSkippedTracked = New-Object System.Collections.Generic.List[object]

foreach ($file in $artifactCandidates) {
    $rel = To-RelativePath -BasePath $Root -TargetPath $file.FullName
    $relGit = $rel.Replace('\', '/')
    $trackedFile = $isRepo -and $tracked.Contains($relGit)
    $row = [PSCustomObject]@{
        FullName = $file.FullName
        RelPath  = $rel
        Tag      = (Get-ArtifactTag -File $file)
        Tracked  = $trackedFile
    }

    if ($trackedFile -and -not $IncludeTrackedArtifacts) {
        [void]$artifactSkippedTracked.Add($row)
    }
    else {
        [void]$artifactTargets.Add($row)
    }
}

$items = Get-ChildItem -Path $Root -Recurse -Force -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -notmatch "\\\.git\\" }

$reservedCandidates = $items | Where-Object {
    $candidate = $_.BaseName.ToUpperInvariant().TrimEnd(' ', '.')
    $reservedNames -contains $candidate
}

$reservedTargets = @()
if ($IncludeReservedNames) {
    $reservedTargets = $reservedCandidates |
        Sort-Object { $_.FullName.Length } -Descending |
        ForEach-Object {
            [PSCustomObject]@{
                FullName = $_.FullName
                RelPath  = (To-RelativePath -BasePath $Root -TargetPath $_.FullName)
                Kind     = $(if ($_.PSIsContainer) { "Directory" } else { "File" })
            }
        }
}

Write-Output "Presentation artifact cleanup"
Write-Output "Root: $Root"
Write-Output ("Repository detected: {0}" -f $isRepo)
Write-Output ("Apply mode: {0}" -f $Apply.IsPresent)
Write-Output ("Include reserved-name removal: {0}" -f $IncludeReservedNames.IsPresent)
Write-Output ("Include tracked artifact removal: {0}" -f $IncludeTrackedArtifacts.IsPresent)
Write-Output ""

Write-Output ("Artifact candidates: {0}" -f $artifactCandidates.Count)
Write-Output ("Artifact removal targets: {0}" -f $artifactTargets.Count)
if ($artifactSkippedTracked.Count -gt 0) {
    Write-Output ("Artifact skipped (tracked): {0}" -f $artifactSkippedTracked.Count)
}

$artifactSummary = $artifactTargets |
    Group-Object Tag |
    Sort-Object Count -Descending |
    Select-Object @{Name = "Type"; Expression = { $_.Name } }, Count

if ($artifactSummary.Count -gt 0) {
    $artifactSummary | Format-Table -AutoSize | Out-String | Write-Output
}

Show-Sample -Header ("Artifact target sample paths (up to {0}):" -f $ListLimit) -Items $artifactTargets.ToArray() -Limit $ListLimit
Show-Sample -Header ("Artifact tracked-skip sample paths (up to {0}):" -f $ListLimit) -Items $artifactSkippedTracked.ToArray() -Limit $ListLimit

Write-Output ("Reserved-name findings: {0}" -f $reservedCandidates.Count)
if (-not $IncludeReservedNames -and $reservedCandidates.Count -gt 0) {
    Write-Output "Reserved-name deletion is disabled by default. Re-run with -IncludeReservedNames to remove those paths."
    Write-Output ""
}

if ($IncludeReservedNames -and $reservedTargets.Count -gt 0) {
    Show-Sample -Header ("Reserved-name target sample paths (up to {0}):" -f $ListLimit) -Items $reservedTargets -Limit $ListLimit
}

if (-not $Apply) {
    Write-Output "Preview only. Re-run with -Apply to perform deletion."
    exit 0
}

$artifactRemoved = 0
$artifactFailed = New-Object System.Collections.Generic.List[string]

foreach ($target in $artifactTargets) {
    try {
        Remove-Item -LiteralPath $target.FullName -Force -ErrorAction Stop
        $artifactRemoved++
    }
    catch {
        [void]$artifactFailed.Add($target.RelPath)
    }
}

$reservedRemoved = 0
$reservedFailed = New-Object System.Collections.Generic.List[string]

if ($IncludeReservedNames) {
    foreach ($target in $reservedTargets) {
        try {
            if (Remove-ReservedPath -FullPath $target.FullName -Kind $target.Kind) {
                $reservedRemoved++
            }
            else {
                [void]$reservedFailed.Add($target.RelPath)
            }
        }
        catch {
            [void]$reservedFailed.Add($target.RelPath)
        }
    }
}

Write-Output ("Removed artifacts: {0}" -f $artifactRemoved)
Write-Output ("Failed artifact removals: {0}" -f $artifactFailed.Count)
if ($artifactFailed.Count -gt 0) {
    Show-Sample -Header ("Failed artifact removals (up to {0}):" -f $ListLimit) -Items ($artifactFailed | ForEach-Object { [PSCustomObject]@{ RelPath = $_ } }) -Limit $ListLimit
}

if ($IncludeReservedNames) {
    Write-Output ("Removed reserved-name paths: {0}" -f $reservedRemoved)
    Write-Output ("Failed reserved-name removals: {0}" -f $reservedFailed.Count)
    if ($reservedFailed.Count -gt 0) {
        Show-Sample -Header ("Failed reserved-name removals (up to {0}):" -f $ListLimit) -Items ($reservedFailed | ForEach-Object { [PSCustomObject]@{ RelPath = $_ } }) -Limit $ListLimit
    }
}

$failed = $artifactFailed.Count + $reservedFailed.Count
if ($failed -gt 0) {
    Write-Output ("Cleanup completed with failures: {0}" -f $failed)
    exit 1
}

Write-Output "Cleanup completed successfully."
exit 0
