from PyQt5.QtWidgets import QApplication, QFileDialog
import sys

app = QApplication(sys.argv)

folder = QFileDialog.getExistingDirectory(
    None,
    "Sélectionne un dossier"
)

if folder:
    print(folder)  # envoyé au PowerShell

sys.exit()