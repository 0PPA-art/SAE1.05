# interface.py
import sys
import json
import random
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QCheckBox, QPushButton, QTextEdit, QGraphicsView, QGraphicsScene,
    QDialog
)
from PyQt5.QtChart import QChart, QChartView, QPieSeries, QPieSlice
from PyQt5.QtGui import QColor, QFont, QBrush, QPen
from PyQt5.QtCore import Qt, pyqtSlot

NB_FICHIERS_MAX = 100
NB_PAR_PAGE = 25
NB_PAGES = (NB_FICHIERS_MAX + NB_PAR_PAGE - 1) // NB_PAR_PAGE  # 4 pages


class FenetrePrincipale(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Résultat – Recherche des gros fichiers")
        self.resize(1100, 750)

        self.fichiers = []  # [[chemin, taille], ...]
        self.couleurs = []  # liste de QColor
        self.checkboxes = [[] for _ in range(NB_PAGES)]  # par page

        self.charger_donnees()
        self.generer_couleurs()

        self.init_ui()

    def charger_donnees(self):
        try:
            with open("gros_fichiers.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                # On remet les chemins corrects (Windows)
                self.fichiers = [[p.replace("\\\\", "\\"), t] for p, t in data]
        except Exception as e:
            print("Erreur lecture JSON :", e)
            self.fichiers = []

    def generer_couleurs(self):
        random.seed(42)  # reproductible
        self.couleurs = []
        for _ in range(len(self.fichiers)):
            r = random.randint(60, 240)
            g = random.randint(60, 240)
            b = random.randint(60, 240)
            self.couleurs.append(QColor(r, g, b))

    def init_ui(self):
        onglets = QTabWidget()
        self.setCentralWidget(onglets)

        # Onglet 1 : Camembert
        page_cam = QWidget()
        layout_cam = QVBoxLayout(page_cam)

        chart = self.creer_camembert()
        view = QChartView(chart)
        view.setRenderHint(0x1)  # Antialiasing
        layout_cam.addWidget(view)

        label_info = QLabel(f"{len(self.fichiers)} plus gros fichiers trouvés")
        label_info.setAlignment(Qt.AlignCenter)
        layout_cam.addWidget(label_info)

        onglets.addTab(page_cam, "Camembert")

        # Onglets 2 à 5 : listes avec cases
        for num_page in range(NB_PAGES):
            page = self.creer_page_legendes(num_page)
            onglets.addTab(page, f"Page {num_page + 1}")

        # Onglet final : suppression
        page_suppr = QWidget()
        lay_suppr = QVBoxLayout(page_suppr)

        self.zone_chemin = QTextEdit()
        self.zone_chemin.setReadOnly(True)
        self.zone_chemin.setPlainText(str(Path.cwd().resolve()))  # dossier de base
        lay_suppr.addWidget(QLabel("Répertoire de base :"))
        lay_suppr.addWidget(self.zone_chemin)

        btn_suppr = QPushButton("Générer script PowerShell de suppression")
        btn_suppr.clicked.connect(self.generer_script_suppression)
        lay_suppr.addWidget(btn_suppr)

        onglets.addTab(page_suppr, "Suppression")

    def creer_camembert(self) -> QChart:
        series = QPieSeries()
        total = sum(t for _, t in self.fichiers)

        for i, (chemin, taille) in enumerate(self.fichiers):
            pourcent = (taille / total * 100) if total > 0 else 0
            etiquette = f"{Path(chemin).name[:30]}... ({pourcent:.1f}%)"
            slice_ = QPieSlice(etiquette, taille)
            slice_.setBrush(QBrush(self.couleurs[i]))
            slice_.setLabelVisible(pourcent > 2.5)  # on affiche que les gros morceaux
            slice_.setLabelFont(QFont("Arial", 10))
            series.append(slice_)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Répartition des plus gros fichiers")
        chart.legend().setAlignment(Qt.AlignRight)
        chart.setAnimationOptions(QChart.SeriesAnimations)
        return chart

    def creer_page_legendes(self, num_page: int) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignTop)

        debut = num_page * NB_PAR_PAGE
        fin = min(debut + NB_PAR_PAGE, len(self.fichiers))

        for i in range(debut, fin):
            idx_global = i
            chemin, taille_mb = self.fichiers[idx_global]
            taille_mb = taille_mb / (1024 * 1024)

            ligne = QHBoxLayout()

            cb = QCheckBox()
            cb.setChecked(False)
            self.checkboxes[num_page].append(cb)

            rect = QLabel("■")
            rect.setStyleSheet(f"color: {self.couleurs[idx_global].name()}; font-size: 20px;")

            lbl = QLabel(f"{Path(chemin).name}  –  {taille_mb:>8.1f} MiB")
            lbl.setMinimumWidth(500)

            ligne.addWidget(cb)
            ligne.addWidget(rect)
            ligne.addWidget(lbl)
            ligne.addStretch()

            layout.addLayout(ligne)

        layout.addStretch()
        return widget

    @pyqtSlot()
    def generer_script_suppression(self):
        to_delete = []
        for page in self.checkboxes:
            for cb in page:
                if cb.isChecked():
                    # On retrouve l'index global (pas très propre mais ça marche)
                    # Mieux serait de stocker les index dans une liste parallèle
                    # Pour simplifier ici on refait le calcul
                    pass  # ← À compléter (voir version avancée ci-dessous)

        # Version simplifiée – à améliorer
        print("Génération du script... (à compléter avec les chemins cochés)")

        # Exemple de contenu
        with open("suppression.ps1", "w", encoding="utf-8") as f:
            f.write('# Script de suppression généré\n')
            f.write('$confirm = Read-Host "Confirmer la suppression ? (OUI)"\n')
            f.write('if ($confirm -eq "OUI") {\n')
            f.write('    Write-Host "Suppression en cours..."\n')
            # f.write('    Remove-Item -Path "chemin1", "chemin2" -Force\n')
            f.write('} else {\n')
            f.write('    Write-Host "Annulé."\n')
            f.write('}\n')

        print("Fichier suppression.ps1 créé !")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = FenetrePrincipale()
    win.show()
    sys.exit(app.exec_())