# lance_analyse.ps1

Write-Host "Lancement de l'analyse des gros fichiers..." -ForegroundColor Cyan

# Essaie dans cet ordre : py → python → python3
$pythonCommands = @("py", "python", "python3")

$python = $null
foreach ($cmd in $pythonCommands) {
    if (Get-Command $cmd -ErrorAction SilentlyContinue) {
        $python = $cmd
        break
    }
}

if (-not $python) {
    Write-Host "ERREUR : Aucun interpréteur Python (py/python/python3) trouvé dans le PATH" -ForegroundColor Red
    Write-Host "Installez Python ou ajoutez-le au PATH, puis réessayez." -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host "Python détecté : $python" -ForegroundColor Green

# ────────────────────────────────────────────────
# Choix du dossier via le petit script séparé
# ────────────────────────────────────────────────
$dossier = & $python ".\choisir_dossier.py"

if (-not $dossier -or $dossier.Trim() -eq "") {
    Write-Host "Aucun dossier sélectionné." -ForegroundColor Yellow
    pause
    exit
}

if (-not (Test-Path $dossier)) {
    Write-Host "Dossier invalide : $dossier" -ForegroundColor Red
    pause
    exit
}

Write-Host "Dossier choisi : $dossier" -ForegroundColor Green

# ────────────────────────────────────────────────
# Lancement de l'analyse
# ────────────────────────────────────────────────
& $python ".\analyse_fichiers.py" "$dossier"

# Si JSON créé → interface graphique
if (Test-Path ".\gros_fichiers.json") {
    Write-Host "Lancement de l'interface graphique..." -ForegroundColor Cyan
    & $python ".\interface.py"
} else {
    Write-Host "Erreur : gros_fichiers.json n'a pas été créé." -ForegroundColor Red
}

Write-Host "Appuyez sur Entrée pour quitter..."
pause