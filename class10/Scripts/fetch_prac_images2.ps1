$ErrorActionPreference = 'Stop'
$outDir = 'E:\logo\class10\website\assets\prac'

function Get-Candidate($title) {
  $enc = [uri]::EscapeDataString($title)
  $url = "https://commons.wikimedia.org/wiki/Special:FilePath/$enc`?width=850"
  try {
    $dest = Join-Path $outDir ($slug + '.png')
    Invoke-WebRequest -Uri $url -OutFile $dest -UseBasicParsing -TimeoutSec 60
    return $true
  } catch { return $false }
}

$targets = @(
  @{ slug='neuron';   cands=@('Neuron.svg','Neuron Hand-tuned.svg','Complete neuron cell diagram en.svg','Neuron (diagram).svg') },
  @{ slug='plant';    cands=@('Simple plant diagram.svg','Plant morphology diagram.svg','Flowering plant parts diagram.svg','Parts of a plant.svg','Plant roots stem leaves diagram.svg') },
  @{ slug='flower';   cands=@('Mature flower diagram.svg','Flower diagram (English).svg','Floral parts diagram.svg') },
  @{ slug='brain';    cands=@('Brain lobes (lateral).svg','Human brain lateral view.jpg','Brain diagram en.svg','Cerebrum lobes.svg') },
  @{ slug='eye';      cands=@('Diagram of human eye.svg','Schematic diagram of the human eye en.svg','Eye diagram labelled.svg') },
  @{ slug='animalcell'; cands=@('Animal cell structure en.svg','Animal cell diagram-labeled.svg','Biological cell anatomy.svg','Animal Cell.svg') },
  @{ slug='plantcell';  cands=@('Plant cell structure en.svg','Plant cell diagram-labeled.svg','Plant Cell.svg') }
)

$manifestPath = Join-Path $outDir 'manifest.json'
$manifest = @()
if (Test-Path $manifestPath) { $manifest = @(Get-Content $manifestPath -Raw | ConvertFrom-Json) }

foreach ($t in $targets) {
  $slug = $t.slug
  $ok = $false
  foreach ($c in $t.cands) {
    if (Get-Candidate $c) { Write-Output ("OK   {0,-10} <- {1}" -f $slug, $c); $ok = $true; break }
    Start-Sleep -Milliseconds 900
  }
  if (-not $ok) { Write-Output ("MISS {0}" -f $slug) }
  Start-Sleep -Seconds 2
}

# refresh manifest entries for downloaded slugs
foreach ($f in Get-ChildItem $outDir -Filter *.png) {
  $slugBase = $f.BaseName
  $i = [array]::IndexOf($manifest.slug, $slugBase)
  $bytes = $f.Length
  if ($i -ge 0) { $manifest[$i].bytes = $bytes } else { $manifest += [pscustomobject]@{ slug=$slugBase; title=$f.Name; bytes=$bytes } }
}
$manifest | ConvertTo-Json | Set-Content $manifestPath -Encoding UTF8
Write-Output '--- done ---'