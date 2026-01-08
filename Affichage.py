import sys
import json
from PyQt5.QtWidgets import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

class App(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Résultat gros fichiers")
        self.resize(900,600)

        with open("report.json") as f:
            self.data = json.load(f)

        self.selected = []

        layout = QVBoxLayout()

        # Camembert
        self.fig = Figure()
        self.canvas = FigureCanvasQTAgg(self.fig)
        self.draw_pie()
        layout.addWidget(self.canvas)

        # Onglets
        self.tabs = QTabWidget()
        self.create_tabs()
        layout.addWidget(self.tabs)

        # Bouton
        btn = QPushButton("Générer script PowerShell")
        btn.clicked.connect(self.generate_ps)
        layout.addWidget(btn)

        self.setLayout(layout)

    def draw_pie(self):
        ax = self.fig.add_subplot(111)
        sizes = [x[1] for x in self.data]
        labels = [x[0].split("\\")[-1] for x in self.data]
        ax.pie(sizes)
        self.canvas.draw()

    def create_tabs(self):
        pages = [self.data[i:i+25] for i in range(0, len(self.data), 25)]

        for i,page in enumerate(pages):
            tab = QWidget()
            vbox = QVBoxLayout()

            for path,size in page:
                cb = QCheckBox(f"{path}  -> {size/1024/1024:.2f} Mo")
                cb.stateChanged.connect(self.toggle)
                vbox.addWidget(cb)

            tab.setLayout(vbox)
            self.tabs.addTab(tab,f"Légendes {i+1}")

    def toggle(self):
        self.selected=[]
        for i in range(self.tabs.count()):
            tab=self.tabs.widget(i)
            for cb in tab.findChildren(QCheckBox):
                if cb.isChecked():
                    self.selected.append(cb.text().split("  ->")[0])

    def generate_ps(self):
        with open("delete.ps1","w") as f:
            for file in self.selected:
                f.write(f'Remove-Item "{file}"\n')

        QMessageBox.information(self,"OK","delete.ps1 généré")

if __name__=="__main__":
    app=QApplication(sys.argv)
    w=App()
    w.show()
    sys.exit(app.exec())