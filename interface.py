# interface.py
# Version adaptée pour utiliser les 4 modules fournis (Creation_*)
# SAE 1.05 – janvier 2026

import sys
import json
import random
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtGui import QColor

# Import des 4 classes fournies
from Creation_Onglets import Onglets
from Creation_Camembert import Camembert  # Attention : fichier peut s'appeler Creation_Camenbert.py
from Creation_Legendes import Legendes
from Creation_Boutons import Boutons

# Constantes
NB_FICHIERS_MAX = 100
NB_LEGENDES_PAR_PAGE = 25
FICHIER_JSON = "gros_fichiers.json"


def generer_couleurs(nb: int) -> list[QColor]:
    """ Génère une liste de couleurs aléatoires reproductibles """
    random.seed(42)  # pour que les couleurs soient toujours les mêmes lors des tests
    couleurs = []
    for _ in range(nb):
        r = random.randint(60, 240)
        g = random.randint(60, 240)
        b = random.randint(60, 240)
        couleurs.append(QColor(r, g, b))
    return couleurs


def charger_donnees_json() -> list[list]:
    """ Charge [[chemin, taille], ...] depuis gros_fichiers.json """
    try:
        with open(FICHIER_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Corrige les doubles backslashes Windows
        return [[chemin.replace("\\\\", "\\"), taille] for chemin, taille in data]
    except Exception as e:
        print(f"Erreur lecture {FICHIER_JSON} : {e}")
        return []


class Application(QApplication):
    def __init__(self, argv):
        super().__init__(argv)

        self.fichiers = charger_donnees_json()
        if not self.fichiers:
            QMessageBox.critical(None, "Erreur", f"Aucun fichier trouvé dans {FICHIER_JSON}")
            sys.exit(1)

        self.couleurs = generer_couleurs(len(self.fichiers))
        self.pages_legendes = []  # pour récupérer les états des cases plus tard

        self.fenetre = Onglets()
        self.construire_interface()
        self.fenetre.show()

    def construire_interface(self):
        # Onglet Camembert
        cam = Camembert(self.fichiers, self.couleurs)
        self.fenetre.add_onglet("Camembert", cam.dessine_camembert())

        # Onglets Légendes (25 par page)
        nb_pages = (len(self.fichiers) + NB_LEGENDES_PAR_PAGE - 1) // NB_LEGENDES_PAR_PAGE

        for num_page in range(nb_pages):
            debut = num_page * NB_LEGENDES_PAR_PAGE
            leg = Legendes(
                liste_fichiers=self.fichiers,
                liste_couleurs=self.couleurs,
                num_legende_start=debut,
                nb_legende_par_page=NB_LEGENDES_PAR_PAGE
            )
            widget_leg = leg.dessine_legendes()
            titre = f"Légende {num_page + 1}"
            self.fenetre.add_onglet(titre, widget_leg)
            self.pages_legendes.append(leg)

        # Onglet Suppression / Bouton
        repertoire_base = str(Path.cwd().resolve())  # À adapter si besoin (dossier scanné)

        def callback_generation():
            self.generer_script_suppression()

        boutons = Boutons(repertoire_base, callback_generation)
        widget_boutons = boutons.dessine_boutons()
        self.fenetre.add_onglet("Suppression", widget_boutons)

    def generer_script_suppression(self):
        """ Récupère les fichiers cochés et crée le script .ps1 """
        selectionnes = []

        for leg in self.pages_legendes:
            etats = leg.recupere_etats_cases_a_cocher()
            for i, coche in enumerate(etats):
                if coche:
                    idx = leg.num_legende_start + i
                    if idx < len(self.fichiers):
                        chemin = self.fichiers[idx][0]
                        selectionnes.append(chemin)

        if not selectionnes:
            QMessageBox.information(self.fenetre, "Information", "Aucun fichier sélectionné.")
            return

        # Confirmation utilisateur
        msg = f"Supprimer {len(selectionnes)} fichier(s) ?\n\nContinuer ?"
        reponse = QMessageBox.question(self.fenetre, "Confirmation", msg,
                                       QMessageBox.Yes | QMessageBox.No)

        if reponse != QMessageBox.Yes:
            return

        # Création du script PowerShell
        fichier_ps1 = "supprimer_fichiers.ps1"
        with open(fichier_ps1, "w", encoding="utf-8") as f:
            f.write("# Script généré automatiquement - SAE 1.05\n\n")
            f.write('$confirm = Read-Host "Confirmer la suppression ? (OUI)"\n')
            f.write('if ($confirm -eq "OUI") {\n')
            f.write('    Write-Host "Suppression en cours..."\n')
            f.write('    Remove-Item -Path `\n')
            for chemin in selectionnes:
                # Échappe les backslashes pour PowerShell
                chemin_esc = chemin.replace("\\", "\\\\").replace('"', '\\"')
                f.write(f'        "{chemin_esc}", `\n')
            f.write('        -Force -ErrorAction SilentlyContinue\n')
            f.write('    Write-Host "Opération terminée."\n')
            f.write('} else {\n')
            f.write('    Write-Host "Opération annulée."\n')
            f.write('}\n')

        QMessageBox.information(self.fenetre, "Succès",
                                f"Script créé : {fichier_ps1}\n\nExécutez-le avec PowerShell.")


if __name__ == "__main__":
    app = Application(sys.argv)
    sys.exit(app.exec_())