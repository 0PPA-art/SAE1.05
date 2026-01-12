# lance_analyse.ps1
# ------------------------------------------------------------------------------
# Place ce fichier dans le même dossier que : choisir_dossier.py, analyse_fichiers.py, interface.py
# ------------------------------------------------------------------------------

# === FORCER le dossier du script comme dossier courant ===
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -Path $scriptDir -ErrorAction Stop

Write-Host "Dossier du script (devrait être U:\Bureau\SAE1.05) : $(Get-Location)" -ForegroundColor Magenta

Write-Host "Lancement de l'analyse des gros fichiers..." -ForegroundColor Cyan

# Détection Python
$pythonCommands = @("py", "python", "python3")
$python = $null

foreach ($cmd in $pythonCommands) {
    if (Get-Command $cmd -ErrorAction SilentlyContinue) {
        $python = $cmd
        break
    }
}

if (-not $python) {
    Write-Host "ERREUR : Aucun interpréteur Python trouvé" -ForegroundColor Red
    pause
    exit 1
}

Write-Host "Python détecté : $python" -ForegroundColor Green

# ------------------------------------------------------------------------------
# Choix du dossier
# ------------------------------------------------------------------------------
Write-Host "Ouverture du sélecteur de dossier..." -ForegroundColor Yellow

$dossierRaw = & $python ".\choisir_dossier.py" 2>$null
$dossier = $dossierRaw.Trim()

if (-not $dossier -or $dossier -eq "") {
    Write-Host "Aucun dossier sélectionné." -ForegroundColor Yellow
    pause
    exit
}

if (-not (Test-Path $dossier -PathType Container)) {
    Write-Host "Erreur : dossier invalide → $dossier" -ForegroundColor Red
    pause
    exit
}

Write-Host "Dossier choisi : $dossier" -ForegroundColor Green

# ------------------------------------------------------------------------------
# Lancement analyse (avec chemin ABSOLU pour éviter tout problème)
# ------------------------------------------------------------------------------
Write-Host "Lancement de l'analyse..." -ForegroundColor Cyan

# Chemin absolu du script d'analyse
$analyseScript = Join-Path -Path $scriptDir -ChildPath "analyse_fichiers.py"

Write-Host "Exécution : $python `"$analyseScript`" `"$dossier`"" -ForegroundColor DarkGray

& $python $analyseScript $dossier

# ------------------------------------------------------------------------------
# Vérification + interface
# ------------------------------------------------------------------------------
$jsonPath = Join-Path -Path $scriptDir -ChildPath "gros_fichiers.json"

if (Test-Path $jsonPath -PathType Leaf) {
    Write-Host "gros_fichiers.json créé avec succès !" -ForegroundColor Green
    Write-Host "Lancement de l'interface graphique..." -ForegroundColor Cyan
    
    $interfaceScript = Join-Path -Path $scriptDir -ChildPath "interface.py"
    & $python $interfaceScript
} else {
    Write-Host "ERREUR : gros_fichiers.json NON créé" -ForegroundColor Red
    Write-Host "Vérifiez les messages/erreurs ci-dessus" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Appuyez sur Entrée pour quitter..."
pause