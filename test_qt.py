# analyse_fichiers.py
import sys
import json
from pathlib import Path
from typing import List, Tuple

def scan_gros_fichiers(racine: Path, max_count: int = 100, min_size_mb: float = 10.0) -> List[Tuple[str, int]]:
    min_size = int(min_size_mb * 1024 * 1024)
    fichiers: List[Tuple[str, int]] = []

    print(f"Scan récursif de : {racine}")
    print("Cela peut prendre plusieurs minutes sur un gros disque...")

    for item in racine.rglob("*"):
        if item.is_file():
            try:
                size = item.stat().st_size
                if size >= min_size:
                    fichiers.append((str(item), size))
            except (PermissionError, FileNotFoundError, OSError):
                pass  # on ignore les erreurs d'accès

    # Tri décroissant par taille
    fichiers.sort(key=lambda x: x[1], reverse=True)
    return fichiers[:max_count]


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python analyse_fichiers.py <chemin_du_dossier>")
        sys.exit(1)

    dossier = Path(sys.argv[1]).resolve()
    if not dossier.is_dir():
        print(f"Erreur : {dossier} n'est pas un dossier valide")
        sys.exit(1)

    top_fichiers = scan_gros_fichiers(dossier)

    # Préparation pour JSON : on double les backslashes sous Windows
    data = [[chemin.replace("\\", "\\\\"), taille] for chemin, taille in top_fichiers]

    with open("gros_fichiers.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n{len(top_fichiers)} gros fichiers trouvés.")
    print("Fichier 'gros_fichiers.json' créé.")