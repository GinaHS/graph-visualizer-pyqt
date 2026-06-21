import sys
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
    QTextEdit, QPushButton, QComboBox, QLabel, QMessageBox, QSplitter
)
from PyQt6.QtCore import Qt


class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Diseñador de Grafos Bidireccional")
        self.setGeometry(100, 100, 1000, 700)

        # Guardaremos el grafo actual como un atributo de la clase
        self.G = nx.Graph()

        # Widget y Layout principal
        widget_central = QWidget()
        self.setCentralWidget(widget_central)
        layout_principal = QHBoxLayout(widget_central)

        # --- PANEL IZQUIERDO: Entrada de datos ---
        panel_izquierdo = QVBoxLayout()

        panel_izquierdo.addWidget(QLabel("<b>ENTRADA DE DATOS</b>"))
        self.combo_entrada = QComboBox()
        self.combo_entrada.addItems(["Matriz de Adyacencia", "Lista de Adyacencia"])
        panel_izquierdo.addWidget(self.combo_entrada)

        self.txt_entrada = QTextEdit()
        self.txt_entrada.setPlaceholderText("Introduce los datos aquí...")
        self.txt_entrada.setText("A B C\nB D\nC\nD 1 2\n1\n2")  
        self.combo_entrada.setCurrentIndex(1)
        panel_izquierdo.addWidget(self.txt_entrada)

        self.btn_generar = QPushButton("Generar y Visualizar Grafo")
        self.btn_generar.clicked.connect(self.procesar_entrada)
        panel_izquierdo.addWidget(self.btn_generar)
        
        # --- PANEL CENTRAL/DERECHO: Visualización y Salida ---
        contenedor_derecho = QSplitter(Qt.Orientation.Vertical)

        # Parte superior: El lienzo del Grafo
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.fig)
        contenedor_derecho.addWidget(self.canvas)

        # Parte inferior: Resultados generados (Matriz y Lista)
        panel_resultados = QWidget()
        layout_resultados = QHBoxLayout(panel_resultados)

        # Sub-panel Matriz Generada
        col_matriz = QVBoxLayout()
        col_matriz.addWidget(QLabel("<b>Matriz de Adyacencia Generada:</b>"))
        self.txt_matriz_salida = QTextEdit()
        self.txt_matriz_salida.setReadOnly(True)
        # ✅ Tipografía monoespaciada forzada para alinear los caracteres
        self.txt_matriz_salida.setStyleSheet("font-family: Consolas, 'Courier New', monospace; font-size: 14px;")
        col_matriz.addWidget(self.txt_matriz_salida)
        layout_resultados.addLayout(col_matriz)

        # Sub-panel Lista Generada
        col_lista = QVBoxLayout()
        col_lista.addWidget(QLabel("<b>Lista de Adyacencia Generada:</b>"))
        self.txt_lista_salida = QTextEdit()
        self.txt_lista_salida.setReadOnly(True)
        col_lista.addWidget(self.txt_lista_salida)
        layout_resultados.addLayout(col_lista)

        contenedor_derecho.addWidget(panel_resultados)

        # Unir todo en el layout principal
        layout_principal.addLayout(panel_izquierdo, stretch=1)
        layout_principal.addWidget(contenedor_derecho, stretch=3)

        # Generar el grafo inicial al abrir la app
        self.procesar_entrada()

    def procesar_entrada(self):
        tipo_entrada = self.combo_entrada.currentText()
        texto = self.txt_entrada.toPlainText().strip()

        if not texto:
            QMessageBox.warning(self, "Error", "El campo de entrada está vacío.")
            return

        try:
            # 1. Construir el grafo según la opción seleccionada
            if tipo_entrada == "Matriz de Adyacencia":
                self.G = self.construir_desde_matriz(texto)
            else:
                self.G = self.construir_desde_lista(texto)

            # 2. Dibujar el grafo
            self.ax.clear()
            pos = nx.spring_layout(self.G)
            
            etiquetas_grado = {
                 nodo: f"{nodo}\n(deg: {self.G.degree(nodo)})" 
                 for nodo in self.G.nodes()
             }

            nx.draw(
                self.G, pos, ax=self.ax, with_labels=True, labels=etiquetas_grado,
                node_color='lightgreen', edge_color='gray', 
                node_size=1000, font_size=8, font_weight='bold'
            )
            self.canvas.draw()

            # 3. Generar las salidas
            self.generar_salidas_desde_grafo()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al procesar: {str(e)}")

    def construir_desde_matriz(self, texto):
        lineas = [l.strip() for l in texto.split('\n') if l.strip()]
        matriz = [[int(x) for x in l.replace(',', ' ').split()] for l in lineas]
        G_temp = nx.from_numpy_array(np.array(matriz))
        
        mapping = {i: chr(65 + i) for i in range(len(G_temp.nodes()))}
        return nx.relabel_nodes(G_temp, mapping)

    def construir_desde_lista(self, texto):
        lineas = [l.strip() for l in texto.split('\n') if l.strip()]
        return nx.parse_adjlist(lineas, nodetype=str)

    def generar_salidas_desde_grafo(self):
        if self.G.number_of_nodes() == 0:
            return

        # --- Matriz de Adyacencia ---
        matriz_np = nx.to_numpy_array(self.G, dtype=int)
        nombres_str = [str(n) for n in self.G.nodes()]
        
        # ✅ Cálculo dinámico de ancho usando alineación derecha pura
        ancho_col = max([len(n) for n in nombres_str] + [1]) + 2 

        # 1. Esquina superior y encabezados
        esquina = " " * ancho_col
        encabezados = "".join([n.rjust(ancho_col) for n in nombres_str])
        texto_matriz = f"{esquina} |{encabezados}\n"
        
        # 2. Divisor calculado milimétricamente
        separador = "-" * (ancho_col + 1) + "+" + "-" * (ancho_col * len(nombres_str))
        texto_matriz += f"{separador}\n"
        
        # 3. Filas de datos
        for i, fila in enumerate(matriz_np):
            nombre_fila = nombres_str[i].rjust(ancho_col)
            valores = "".join([str(val).rjust(ancho_col) for val in fila])
            texto_matriz += f"{nombre_fila} |{valores}\n"

        self.txt_matriz_salida.setText(texto_matriz)

        # --- Lista de Adyacencia ---
        texto_lista = "\n".join(nx.generate_adjlist(self.G, delimiter=' '))
        self.txt_lista_salida.setText(texto_lista)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec())