$ErrorActionPreference = 'Stop'
$outDir = 'E:\logo\class10\website\assets\prac'
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

$topics = @(
  @{ slug='heart';      q='human heart diagram labelled' },
  @{ slug='brain';      q='brain lobes diagram labelled' },
  @{ slug='eye';        q='human eye cross section diagram' },
  @{ slug='ear';        q='human ear anatomy diagram labelled' },
  @{ slug='kidney';     q='kidney diagram label nephron' },
  @{ slug='neuron';     q='neuron structure diagram labelled' },
  @{ slug='lungs';      q='respiratory system lungs diagram labelled' },
  @{ slug='digestive';  q='human digestive system diagram labelled' },
  @{ slug='flower';     q='flower parts diagram reproductive labelled' },
  @{ slug='plant';      q='plant parts diagram roots stem leaves' },
  @{ slug='leaf';       q='leaf cross section stomata diagram' },
  @{ slug='animalcell'; q='animal cell diagram labelled' },
  @{ slug='plantcell';  q='plant cell diagram labelled' }
)

$manifest = @()
foreach ($t in $topics) {
  $api = "https://commons.wikimedia.org/w/api.php?action=query&list=search&srsearch=" +
         [uri]::EscapeDataString($t.q) + "&srnamespace=6&srlimit=12&format=json&formatversion=2"
  $res = Invoke-RestMethod -Uri $api -TimeoutSec 25
  $files = $res.query.search | ForEach-Object { $_.title }
  # prefer SVG, then PNG
  $pick = ($files | Where-Object { $_ -match '\.svg$' } | Select-Object -First 1)
  if (-not $pick) { $pick = ($files | Where-Object { $_ -match '\.png$' } | Select-Object -First 1) }
  if (-not $pick) { $pick = $files[0] }
  $dest = Join-Path $outDir ($t.slug + '.png')
  if ($pick) {
    $enc = [uri]::EscapeDataString($pick)
    $url = "https://commons.wikimedia.org/wiki/Special:FilePath/$enc`?width=850"
    try {
      Invoke-WebRequest -Uri $url -OutFile $dest -UseBasicParsing -TimeoutSec 60
      $sz = (Get-Item $dest).Length
      Write-Output ("OK   {0,-10} <- {1}  ({2} bytes)" -f $t.slug, $pick, $sz)
      $manifest += [pscustomobject]@{ slug=$t.slug; title=$pick; bytes=$sz }
    } catch {
      Write-Output ("FAIL {0,-10} <- {1} : {2}" -f $t.slug, $pick, $_.Exception.Message)
    }
  } else {
    Write-Output ("NONE {0}" -f $t.slug)
  }
}
$manifest | ConvertTo-Json | Set-Content -Path (Join-Path $outDir 'manifest.json') -Encoding UTF8
Write-Output '--- manifest saved ---'