import sys
import socket
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QSpacerItem, QSizePolicy
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt

class BalancaMockup(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('VBI - Visualizador Balança Integradora')
        self.resize(600, 500)
        
        # Background color to match image (grey solid)
        self.setStyleSheet("background-color: #888888; color: black;")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Top Bar
        top_bar = QWidget()
        top_bar.setStyleSheet("background-color: #0000FF; color: white;")
        top_bar.setFixedHeight(40)
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(10, 0, 10, 0)
        
        lbl_operacao = QLabel("Operação")
        lbl_operacao.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        top_layout.addWidget(lbl_operacao)
        
        top_layout.addStretch()
        layout.addWidget(top_bar)

        # Connection Bar (IP/Port)
        conn_bar = QWidget()
        conn_bar.setStyleSheet("background-color: #AAAAAA; color: black; border-bottom: 1px solid #555;")
        conn_bar.setFixedHeight(45)
        conn_layout = QHBoxLayout(conn_bar)
        conn_layout.setContentsMargins(10, 5, 10, 5)
        conn_layout.setSpacing(10)

        # Default IP
        try:
            default_ip = socket.gethostbyname(socket.gethostname())
        except:
            default_ip = "192.168.0.100"

        lbl_ip = QLabel("IP:")
        lbl_ip.setStyleSheet("border: none;")
        txt_ip = QLineEdit(default_ip)
        txt_ip.setStyleSheet("background-color: white; border: 1px solid black;")
        txt_ip.setFixedWidth(120)

        lbl_port = QLabel("Porta:")
        lbl_port.setStyleSheet("border: none;")
        txt_port = QLineEdit("502")
        txt_port.setStyleSheet("background-color: white; border: 1px solid black;")
        txt_port.setFixedWidth(50)

        btn_connect = QPushButton("Conectar")
        btn_connect.setStyleSheet("background-color: #E0E0E0; border: 1px solid black; padding: 5px;")
        
        btn_sobre = QPushButton("Sobre")
        btn_sobre.setStyleSheet("background-color: #E0E0E0; border: 1px solid black; padding: 5px;")

        conn_layout.addWidget(lbl_ip)
        conn_layout.addWidget(txt_ip)
        conn_layout.addWidget(lbl_port)
        conn_layout.addWidget(txt_port)
        conn_layout.addWidget(btn_connect)
        conn_layout.addStretch()
        conn_layout.addWidget(btn_sobre)

        layout.addWidget(conn_bar)
        
        # Main Body
        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        body_layout.setSpacing(10)
        
        # Title "Esteira"
        lbl_esteira = QLabel("Esteira")
        lbl_esteira.setFont(QFont("Arial", 20))
        lbl_esteira.setAlignment(Qt.AlignmentFlag.AlignCenter)
        body_layout.addWidget(lbl_esteira)
        body_layout.addSpacing(10)
        
        # Helper to create data fields
        def create_field(label_text, value_text, unit_text, value_color):
            container = QWidget()
            lo = QVBoxLayout(container)
            lo.setContentsMargins(0, 0, 0, 0)
            lo.setSpacing(2)
            
            lbl = QLabel(label_text)
            lbl.setFont(QFont("Arial", 12))
            
            val_container = QWidget()
            val_lo = QHBoxLayout(val_container)
            val_lo.setContentsMargins(0, 0, 0, 0)
            val_lo.setSpacing(5)
            
            val_lbl = QLabel(value_text)
            val_lbl.setFont(QFont("Arial", 28, QFont.Weight.Bold))
            val_lbl.setStyleSheet(f"background-color: black; color: {value_color}; padding: 2px;")
            val_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            val_lbl.setMinimumWidth(250)
            
            unit_lbl = QLabel(unit_text)
            unit_lbl.setFont(QFont("Arial", 12))
            
            val_lo.addWidget(val_lbl)
            val_lo.addWidget(unit_lbl)
            
            lo.addWidget(lbl)
            lo.addWidget(val_container)
            return container

        # Vazao
        f_vazao = create_field("Vazão", "0099.999", "t/h", "white")
        body_layout.addWidget(f_vazao)
        
        # Executando tag
        lbl_exec = QLabel("Executando")
        lbl_exec.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        lbl_exec.setStyleSheet("background-color: #666666; color: lime; border: 1px solid white; padding: 5px;")
        lbl_exec.setFixedWidth(200)
        lbl_exec.setAlignment(Qt.AlignmentFlag.AlignCenter)
        exec_container = QWidget()
        exec_lo = QHBoxLayout(exec_container)
        exec_lo.setContentsMargins(0,0,0,0)
        exec_lo.addWidget(lbl_exec, alignment=Qt.AlignmentFlag.AlignLeft)
        body_layout.addWidget(exec_container)
        body_layout.addSpacing(10)
        
        # Totalizador Parcial
        f_parcial = create_field("Totalizador Parcial", "- 9999.999", "t", "#00FF00")
        body_layout.addWidget(f_parcial)
        body_layout.addSpacing(10)
        
        # Totalizador Geral
        f_geral = create_field("Totalizador Geral", " 1234.567", "t", "yellow")
        body_layout.addWidget(f_geral)
        body_layout.addSpacing(10)
        
        # Velocidade
        f_vel = create_field("Velocidade", " -10.95", "m/seg", "cyan")
        # Resize val_lbl for velocity
        f_vel.layout().itemAt(1).widget().layout().itemAt(0).widget().setMinimumWidth(150)
        body_layout.addWidget(f_vel)
        
        layout.addWidget(body)
        self.setLayout(layout)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = BalancaMockup()
    pixmap = ex.grab()
    pixmap.save("mockup_v2.jpg", "JPG")
    app.quit()
