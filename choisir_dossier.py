# choisir_dossier.py
from PyQt5.QtWidgets import QApplication, QFileDialog
import sys

app = QApplication(sys.argv)
folder = QFileDialog.getExistingDirectory(
    None,
    "Choisir le dossier à analyser",
    options=QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
)

if folder:
    print(folder.replace('\\', '/'))   # on normalise en slash pour plus de sécurité
else:
    print("")