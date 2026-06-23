[CmdletBinding()]
param(
    [string]$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
)

$ErrorActionPreference = "Stop"

function Normalize-Slug {
    param(
        [Parameter(Mandatory = $true)][string]$Text
    )

    $slug = $Text.ToLowerInvariant()
    $slug = $slug -replace '\.[^.]+$', ''
    $slug = $slug -replace '(?i)(^|[_\-\s])(e\d{3}|ep\d{2,3})', ' '
    $slug = $slug -replace '^\d{2,3}[_\-]?', ' '
    $slug = $slug -replace '[^a-z0-9]+', '_'
    $slug = $slug.Trim('_')
    if ([string]::IsNullOrWhiteSpace($slug)) {
        return "episode"
    }
    return $slug
}

function Title-FromSlug {
    param(
        [Parameter(Mandatory = $true)][string]$Slug
    )

    $ti = [System.Globalization.CultureInfo]::InvariantCulture.TextInfo
    return $ti.ToTitleCase(($Slug -replace '_', ' '))
}

function Get-EpisodeIdsFromName {
    param(
        [Parameter(Mandatory = $true)][string]$Name
    )

    $ids = New-Object System.Collections.Generic.HashSet[string]([System.StringComparer]::OrdinalIgnoreCase)

    [regex]::Matches($Name, '(?i)(?<![a-z0-9])e(\d{3})(?!\d)') | ForEach-Object {
        [void]$ids.Add(("E" + $_.Groups[1].Value))
    }

    [regex]::Matches($Name, '(?i)(?<![a-z0-9])ep(\d{2,3})(?!\d)') | ForEach-Object {
        [void]$ids.Add(("EP" + $_.Groups[1].Value.PadLeft(3, '0')))
    }

    if ($ids.Count -eq 0) {
        $m = [regex]::Match($Name, '^(?<n>\d{2,3})[_\-]')
        if ($m.Success) {
            [void]$ids.Add(("EP" + $m.Groups['n'].Value.PadLeft(3, '0')))
        }
    }

    return @($ids)
}

function Get-Bucket {
    param(
        [Parameter(Mandatory = $true)][string]$Channel,
        [Parameter(Mandatory = $true)][string]$RelativePath
    )

    $parts = $RelativePath -split '[\\/]'

    if ($Channel -eq 'podcast') {
        if ($parts.Length -eq 0) { return 'root' }
        if ($parts[0] -eq 'episodes') {
            if ($parts.Length -ge 2) { return "episodes_{0}" -f (Normalize-Slug $parts[1]) }
            return "episodes"
        }
        if ($parts[0] -eq 'archive') {
            if ($parts.Length -ge 3) { return "archive_{0}" -f (Normalize-Slug $parts[2]) }
            if ($parts.Length -ge 2) { return "archive_{0}" -f (Normalize-Slug $parts[1]) }
            return "archive"
        }
        if ($parts[0] -eq 'cheatsheets') {
            if ($parts.Length -ge 2) { return "cheatsheets_{0}" -f (Normalize-Slug $parts[1]) }
            return "cheatsheets"
        }
        return (Normalize-Slug $parts[0])
    }

    if ($parts.Length -ge 1) {
        return (Normalize-Slug $parts[0])
    }
    return "root"
}

function Copy-WithDedup {
    param(
        [Parameter(Mandatory = $true)][string]$SourcePath,
        [Parameter(Mandatory = $true)][string]$TargetDir
    )

    New-Item -ItemType Directory -Path $TargetDir -Force | Out-Null

    $name = [System.IO.Path]::GetFileName($SourcePath)
    $base = [System.IO.Path]::GetFileNameWithoutExtension($SourcePath)
    $ext = [System.IO.Path]::GetExtension($SourcePath)
    $candidate = Join-Path $TargetDir $name

    if (-not (Test-Path -LiteralPath $candidate)) {
        Copy-Item -LiteralPath $SourcePath -Destination $candidate -Force
        return $candidate
    }

    $i = 2
    while ($true) {
        $candidate = Join-Path $TargetDir ("{0}__{1}{2}" -f $base, $i, $ext)
        if (-not (Test-Path -LiteralPath $candidate)) {
            Copy-Item -LiteralPath $SourcePath -Destination $candidate -Force
            return $candidate
        }
        $i++
    }
}

function Get-ExistingEpisodeMap {
    param(
        [Parameter(Mandatory = $true)][string]$EpisodesRoot
    )

    $map = @{}
    if (-not (Test-Path -LiteralPath $EpisodesRoot)) {
        return $map
    }

    Get-ChildItem -Path $EpisodesRoot -Directory -Force | ForEach-Object {
        if ($_.Name -match '^(?<id>E\d{3}|EP\d{3})_(?<slug>.+)$') {
            $map[$matches['id'].ToUpperInvariant()] = $matches['slug']
        }
    }

    return $map
}

function New-EpisodeLayout {
    param(
        [Parameter(Mandatory = $true)][string]$EpisodeDir
    )

    $dirs = @(
        "source",
        "source\scripts",
        "source\notes",
        "assets\figures",
        "assets\code",
        "outputs\podcast\imports",
        "outputs\beautiful_ai\imports",
        "outputs\pdf",
        "qa"
    )

    foreach ($d in $dirs) {
        New-Item -ItemType Directory -Path (Join-Path $EpisodeDir $d) -Force | Out-Null
    }
}

function Write-Metadata {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$EpisodeId,
        [Parameter(Mandatory = $true)][string]$Slug,
        [Parameter(Mandatory = $true)][string]$Title,
        [Parameter(Mandatory = $true)][string[]]$Channels,
        [Parameter(Mandatory = $true)][string[]]$Languages,
        [Parameter(Mandatory = $true)][int]$SourceCount,
        [Parameter(Mandatory = $true)][string[]]$Buckets,
        [Parameter(Mandatory = $true)][string]$DateStamp
    )

    $lines = @(
        ("episode_id: {0}" -f $EpisodeId),
        ("slug: {0}" -f $Slug),
        ("title: {0}" -f $Title),
        "status: migrated_auto",
        ("last_updated: {0}" -f $DateStamp),
        "languages:"
    )

    foreach ($lang in $Languages) {
        $lines += ("  - {0}" -f $lang)
    }

    $lines += "channels:"
    foreach ($ch in $Channels) {
        $lines += ("  - {0}" -f $ch)
    }

    $lines += ("source_file_count: {0}" -f $SourceCount)
    $lines += "source_buckets:"
    foreach ($b in $Buckets) {
        $lines += ("  - {0}" -f $b)
    }

    Set-Content -Path $Path -Value $lines -Encoding UTF8
}

$episodesRoot = Join-Path $Root "episodes"
New-Item -ItemType Directory -Path $episodesRoot -Force | Out-Null

$sourceRoots = @(
    @{ Path = (Join-Path $Root "podcasts"); Channel = "podcast" },
    @{ Path = (Join-Path $Root "beautiful_ai"); Channel = "beautiful_ai" }
)

$episodes = @{}

foreach ($src in $sourceRoots) {
    if (-not (Test-Path -LiteralPath $src.Path)) { continue }

    $files = Get-ChildItem -Path $src.Path -Recurse -File -Force -ErrorAction SilentlyContinue
    foreach ($f in $files) {
        $ids = Get-EpisodeIdsFromName -Name $f.Name
        if ($ids.Count -eq 0) { continue }

        $rel = $f.FullName.Substring($src.Path.Length).TrimStart('\', '/')
        foreach ($id in $ids) {
            $idKey = $id.ToUpperInvariant()
            if (-not $episodes.ContainsKey($idKey)) {
                $episodes[$idKey] = [ordered]@{
                    Id            = $idKey
                    Files         = New-Object System.Collections.Generic.List[object]
                    SlugCandidates = New-Object System.Collections.Generic.List[string]
                }
            }

            $entry = [PSCustomObject]@{
                Channel  = $src.Channel
                FullPath = $f.FullName
                RelPath  = $rel
                Name     = $f.Name
            }
            [void]$episodes[$idKey].Files.Add($entry)
            [void]$episodes[$idKey].SlugCandidates.Add((Normalize-Slug $f.Name))
        }
    }
}

$existingMap = Get-ExistingEpisodeMap -EpisodesRoot $episodesRoot
$today = (Get-Date).ToString("yyyy-MM-dd")
$indexRows = New-Object System.Collections.Generic.List[object]
$migratedFiles = 0

$sortedIds = $episodes.Keys | Sort-Object
foreach ($id in $sortedIds) {
    $ep = $episodes[$id]
    if ($existingMap.ContainsKey($id)) {
        $slug = $existingMap[$id]
    }
    else {
        $slug = (
            $ep.SlugCandidates |
            Where-Object { $_ -and $_ -ne 'episode' } |
            Group-Object |
            Sort-Object -Property @{ Expression = 'Count'; Descending = $true }, @{ Expression = 'Name'; Descending = $false } |
            Select-Object -First 1 -ExpandProperty Name
        )
        if ([string]::IsNullOrWhiteSpace($slug)) {
            $slug = "episode"
        }
    }

    $episodeDir = Join-Path $episodesRoot ("{0}_{1}" -f $id, $slug)
    New-EpisodeLayout -EpisodeDir $episodeDir

    $channels = New-Object System.Collections.Generic.HashSet[string]([System.StringComparer]::OrdinalIgnoreCase)
    $buckets = New-Object System.Collections.Generic.HashSet[string]([System.StringComparer]::OrdinalIgnoreCase)
    $langSet = New-Object System.Collections.Generic.HashSet[string]([System.StringComparer]::OrdinalIgnoreCase)
    [void]$langSet.Add("en")

    foreach ($item in $ep.Files) {
        [void]$channels.Add($item.Channel)

        $bucket = Get-Bucket -Channel $item.Channel -RelativePath $item.RelPath
        [void]$buckets.Add($bucket)

        if ($item.Name -match '(?i)([_\-\.]fa([_\-\.]|$)|farsi)') {
            [void]$langSet.Add("fa")
        }

        if ($item.Channel -eq "podcast") {
            $targetDir = Join-Path $episodeDir ("outputs\podcast\imports\{0}" -f $bucket)
        }
        else {
            $targetDir = Join-Path $episodeDir ("outputs\beautiful_ai\imports\{0}" -f $bucket)
        }

        Copy-WithDedup -SourcePath $item.FullPath -TargetDir $targetDir | Out-Null
        $migratedFiles++
    }

    $title = Title-FromSlug -Slug $slug
    $metaPath = Join-Path $episodeDir "metadata.yaml"
    Write-Metadata -Path $metaPath `
        -EpisodeId $id `
        -Slug $slug `
        -Title $title `
        -Channels @($channels | Sort-Object) `
        -Languages @($langSet | Sort-Object) `
        -SourceCount $ep.Files.Count `
        -Buckets @($buckets | Sort-Object) `
        -DateStamp $today

    $primary = if ($channels.Count -gt 1) { "multi-channel" } else { @($channels)[0] }
    $langs = (@($langSet | Sort-Object) -join "|")

    [void]$indexRows.Add([PSCustomObject]@{
        episode_id      = $id
        slug            = $slug
        title           = $title
        status          = "migrated_auto"
        primary_channel = $primary
        languages       = $langs
        last_updated    = $today
    })
}

$indexPath = Join-Path $episodesRoot "INDEX.csv"
$indexRows | Sort-Object episode_id | Export-Csv -Path $indexPath -NoTypeInformation -Encoding UTF8

Write-Output ("Episodes migrated: {0}" -f $episodes.Count)
Write-Output ("Files copied into episode hubs: {0}" -f $migratedFiles)
Write-Output ("Index path: {0}" -f $indexPath)
