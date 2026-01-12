# suppression_fichiers.ps1 (généré)
$reponse = Read-Host "Vraiment supprimer les fichiers cochés ? (OUI)"
if ($reponse -eq "OUI") {
    Remove-Item -Path `
        "C:\Users\Lommé\Videos\Film.mkv",`
        "C:\jeux\Steam\..." `
        -Force
    Write-Host "Suppression terminée."
} else {
    Write-Host "Annulé."
}