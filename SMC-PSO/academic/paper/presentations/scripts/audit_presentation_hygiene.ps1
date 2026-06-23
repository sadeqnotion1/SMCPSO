[CmdletBinding()]
param(
    [string]$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path,
    [switch]$FailOnFindings,
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

$artifactPatterns = @(
    ".aux", ".log", ".out", ".toc", ".nav", ".snm", ".vrb",
    ".bbl", ".blg", ".bcf", ".fls", ".fdb_latexmk", ".run.xml", ".synctex.gz"
)

$reservedNames = @(
    "CON", "PRN", "AUX", "NUL",
    "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
    "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"
)

$files = Get-ChildItem -Path $Root -Recurse -Force -File -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -notmatch "\\\.git\\" }

$artifactFindings = $files | Where-Object {
    $tag = Get-ArtifactTag -File $_
    $artifactPatterns -contains $tag
}

$items = Get-ChildItem -Path $Root -Recurse -Force -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -notmatch "\\\.git\\" }

$reservedFindings = $items | Where-Object {
    $candidate = $_.BaseName.ToUpperInvariant().TrimEnd(' ', '.')
    $reservedNames -contains $candidate
}

Write-Output "Presentation hygiene audit"
Write-Output "Root: $Root"
Write-Output ""

Write-Output ("Artifact findings: {0}" -f $artifactFindings.Count)
if ($artifactFindings.Count -gt 0) {
    $artifactSummary = $artifactFindings |
        Group-Object { Get-ArtifactTag -File $_ } |
        Sort-Object Count -Descending |
        Select-Object @{Name = "Type"; Expression = { $_.Name } }, Count
    $artifactSummary | Format-Table -AutoSize | Out-String | Write-Output

    Write-Output ("Artifact sample paths (up to {0}):" -f $ListLimit)
    $artifactFindings |
        Select-Object -First $ListLimit |
        ForEach-Object { To-RelativePath -BasePath $Root -TargetPath $_.FullName } |
        Write-Output
    Write-Output ""
}

Write-Output ("Reserved-name findings: {0}" -f $reservedFindings.Count)
if ($reservedFindings.Count -gt 0) {
    Write-Output ("Reserved-name sample paths (up to {0}):" -f $ListLimit)
    $reservedFindings |
        Select-Object -First $ListLimit |
        ForEach-Object { To-RelativePath -BasePath $Root -TargetPath $_.FullName } |
        Write-Output
    Write-Output ""
}

$total = $artifactFindings.Count + $reservedFindings.Count
if ($FailOnFindings -and $total -gt 0) {
    Write-Output ("FAIL: {0} hygiene finding(s) detected." -f $total)
    exit 1
}

Write-Output ("PASS: audit completed with {0} finding(s)." -f $total)
exit 0
