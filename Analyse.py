import os
import json
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton,
    QLabel, QFileDialog, QVBoxLayout, QMessageBox
)

class App(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Analyse gros fichiers")
        self.resize(400, 200)

        self.label = QLabel("Aucun dossier sélectionné")
        self.btn_select = QPushButton("Choisir un dossier")
        self.btn_analyse = QPushButton("Lancer l'analyse")

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.btn_select)
        layout.addWidget(self.btn_analyse)
        self.setLayout(layout)

        self.btn_select.clicked.connect(self.select_folder)
        self.btn_analyse.clicked.connect(self.analyse)

        self.folder = None

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Sélectionnez un dossier"
        )
        if folder:
            self.folder = folder
            self.label.setText(folder)

    def analyse(self):
        if not self.folder:
            QMessageBox.warning(self, "Erreur", "Choisissez un dossier")
            return

        result = []

        for root, dirs, files in os.walk(self.folder):
            for file in files:
                path = os.path.join(root, file)
                try:
                    size = os.path.getsize(path)
                    result.append([path, size])
                except:
                    pass

        result_sorted = sorted(result, key=lambda x: x[1], reverse=True)
        top100 = result_sorted[:100]

        with open("report.json", "w", encoding="utf-8") as f:
            json.dump(top100, f, indent=4)

        QMessageBox.information(
            self,
            "Succès",
            "Analyse terminée !\nFichier report.json créé."
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec())