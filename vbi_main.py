import sys
import socket
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, 
    QLineEdit, QPushButton, QMessageBox, QSpacerItem, QSizePolicy, QStatusBar
)
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt, QSettings, QTimer, QThread, pyqtSignal, QSharedMemory
from pymodbus.client import ModbusTcpClient

class PollWorker(QThread):
    data_signal = pyqtSignal(list)
    error_signal = pyqtSignal(str)
    
    def __init__(self, client, start_addr=0, qty=9):
        super().__init__()
        self.client = client
        self.start_addr = start_addr
        self.qty = qty

    def run(self):
        try:
            import inspect
            sig = inspect.signature(self.client.read_holding_registers)
            kwargs = {'count': self.qty}
            if 'slave' in sig.parameters: kwargs['slave'] = 1
            elif 'device_id' in sig.parameters: kwargs['device_id'] = 1
            else: kwargs['unit'] = 1
            result = self.client.read_holding_registers(address=self.start_addr, **kwargs)
            if not result.isError():
                self.data_signal.emit(result.registers)
            else:
                self.error_signal.emit(f"Erro na Leitura Modbus: {result}")
        except Exception as e:
            self.error_signal.emit(f"Falha de Conexão: {str(e)}")

class VBIMainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('VBI - Visualizador Balança Integradora')
        self.resize(600, 500)
        
        import os
        from PyQt6.QtGui import QIcon
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        self.client = None
        self.is_connected = False
        self.poll_timer = QTimer(self)
        self.poll_timer.timeout.connect(self.poll_data)
        
        self.initUI()
        self.load_settings()
        
    def initUI(self):
        # Background
        main_widget = QWidget()
        main_widget.setStyleSheet("background-color: #888888; color: black;")
        self.setCentralWidget(main_widget)
        
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("background-color: #DDDDDD; color: black;")
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Desconectado")
        
        layout = QVBoxLayout(main_widget)
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

        self.lbl_ip = QLabel("IP:")
        self.lbl_ip.setStyleSheet("border: none;")
        self.txt_ip = QLineEdit()
        self.txt_ip.setStyleSheet("background-color: white; border: 1px solid black;")
        self.txt_ip.setFixedWidth(120)

        self.lbl_port = QLabel("Porta:")
        self.lbl_port.setStyleSheet("border: none;")
        self.txt_port = QLineEdit("502")
        self.txt_port.setStyleSheet("background-color: white; border: 1px solid black;")
        self.txt_port.setFixedWidth(50)

        self.btn_connect = QPushButton("Conectar")
        self.btn_connect.setStyleSheet("background-color: #E0E0E0; border: 1px solid black; padding: 5px;")
        self.btn_connect.clicked.connect(self.toggle_connection)
        
        self.btn_sobre = QPushButton("Sobre")
        self.btn_sobre.setStyleSheet("background-color: #E0E0E0; border: 1px solid black; padding: 5px;")
        self.btn_sobre.clicked.connect(self.show_about)

        conn_layout.addWidget(self.lbl_ip)
        conn_layout.addWidget(self.txt_ip)
        conn_layout.addWidget(self.lbl_port)
        conn_layout.addWidget(self.txt_port)
        conn_layout.addWidget(self.btn_connect)
        conn_layout.addStretch()
        conn_layout.addWidget(self.btn_sobre)

        layout.addWidget(conn_bar)
        
        # Main Body
        body = QWidget()
        self.body_layout = QVBoxLayout(body)
        self.body_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        self.body_layout.setSpacing(10)
        
        # Title "Esteira"
        lbl_esteira = QLabel("Esteira")
        lbl_esteira.setFont(QFont("Arial", 20))
        lbl_esteira.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.body_layout.addWidget(lbl_esteira)
        self.body_layout.addSpacing(10)
        
        # Fields creation helper
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
            return container, val_lbl

        # Vazao
        f_vazao, self.lbl_vazao = create_field("Vazão", "0", "t/h", "white")
        self.body_layout.addWidget(f_vazao)
        
        # Executando tag
        self.lbl_exec = QLabel("Parada")
        self.lbl_exec.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.lbl_exec.setStyleSheet("background-color: #666666; color: red; border: 1px solid white; padding: 5px;")
        self.lbl_exec.setFixedWidth(200)
        self.lbl_exec.setAlignment(Qt.AlignmentFlag.AlignCenter)
        exec_container = QWidget()
        exec_lo = QHBoxLayout(exec_container)
        exec_lo.setContentsMargins(0,0,0,0)
        exec_lo.addWidget(self.lbl_exec, alignment=Qt.AlignmentFlag.AlignLeft)
        self.body_layout.addWidget(exec_container)
        self.body_layout.addSpacing(10)
        
        # Totalizador Parcial
        f_parcial, self.lbl_parcial = create_field("Totalizador Parcial", "0", "t", "#00FF00")
        self.body_layout.addWidget(f_parcial)
        self.body_layout.addSpacing(10)
        
        # Totalizador Geral
        f_geral, self.lbl_geral = create_field("Totalizador Geral", "0", "t", "yellow")
        self.body_layout.addWidget(f_geral)
        self.body_layout.addSpacing(10)
        
        # Velocidade
        f_vel, self.lbl_velocidade = create_field("Velocidade", "0.00", "m/seg", "cyan")
        f_vel.layout().itemAt(1).widget().layout().itemAt(0).widget().setMinimumWidth(150)
        self.body_layout.addWidget(f_vel)
        
        layout.addWidget(body)

    def load_settings(self):
        settings = QSettings("FabioPiuma", "VBI")
        try:
            default_ip = socket.gethostbyname(socket.gethostname())
        except:
            default_ip = "192.168.0.100"
        self.txt_ip.setText(str(settings.value("ip", default_ip)))
        self.txt_port.setText(str(settings.value("tcp_port", "502")))
        
    def save_settings(self):
        settings = QSettings("FabioPiuma", "VBI")
        settings.setValue("ip", self.txt_ip.text())
        settings.setValue("tcp_port", self.txt_port.text())

    def closeEvent(self, event):
        self.save_settings()
        if self.is_connected:
            self.toggle_connection()
        event.accept()

    def format_value(self, low_word, high_word, decimal_places):
        # Convert to 32 bit signed
        val = (high_word << 16) | low_word
        if val >= 0x80000000:
            val -= 0x100000000
        
        val_str = str(val)
        is_negative = val < 0
        if is_negative:
            val_str = val_str[1:] # Remove minus sign
        
        if decimal_places > 0:
            val_str = val_str.zfill(decimal_places + 1) # Ensure we have enough length
            formatted = val_str[:-decimal_places] + "." + val_str[-decimal_places:]
        else:
            formatted = val_str
            
        return f"- {formatted}" if is_negative else formatted

    def show_about(self):
        QMessageBox.about(
            self, 
            "Sobre", 
            "<h3>VBI - Visualizador Balança Integradora</h3>"
            "<p><b>Versão 1.0.0</b></p>"
            "<p>Monitoração Remota Modbus TCP para Balanças Integradoras.</p>"
            "<p><b>Copyright © 2026 Vekten</b>.</p>"
        )

    def toggle_connection(self):
        if not self.is_connected:
            ip = self.txt_ip.text()
            port = int(self.txt_port.text())
            self.status_bar.showMessage(f"Tentando conectar a {ip}:{port}...")
            # Força o refresco da interface
            QApplication.processEvents()
            try:
                self.client = ModbusTcpClient(host=ip, port=port, timeout=2)
                if self.client.connect():
                    self.is_connected = True
                    self.btn_connect.setText("Desconectar")
                    self.txt_ip.setEnabled(False)
                    self.txt_port.setEnabled(False)
                    self.status_bar.showMessage(f"Conectado a {ip}:{port}. Iniciando leituras...")
                    self.poll_timer.start(500) # Poll every 500ms
                else:
                    self.status_bar.showMessage(f"Falha de conexão com {ip}:{port}")
                    QMessageBox.warning(self, "Erro", f"Não foi possível conectar a {ip}:{port}")
            except Exception as e:
                self.status_bar.showMessage(f"Erro Modbus: {str(e)}")
                QMessageBox.warning(self, "Erro", f"Falha na conexão: {str(e)}")
        else:
            self.poll_timer.stop()
            if self.client:
                self.client.close()
            self.is_connected = False
            self.btn_connect.setText("Conectar")
            self.txt_ip.setEnabled(True)
            self.txt_port.setEnabled(True)
            self.status_bar.showMessage("Desconectado")

    def poll_data(self):
        if not self.is_connected or not self.client:
            return
            
        if hasattr(self, "active_worker") and self.active_worker.isRunning():
            return
            
        self.active_worker = PollWorker(self.client)
        self.active_worker.data_signal.connect(self.update_ui_values)
        self.active_worker.error_signal.connect(self.handle_error)
        self.active_worker.start()

    def handle_error(self, err_msg):
        # We can silently ignore polling drops or show an indicator
        self.status_bar.showMessage(err_msg)
        self.lbl_exec.setText("Erro Modbus")
        self.lbl_exec.setStyleSheet("background-color: #666666; color: orange; border: 1px solid white; padding: 5px;")

    def update_ui_values(self, registers):
        if not registers or len(registers) < 9: return
        self.status_bar.showMessage("Recebendo dados...")
        
        # Ponto Decimais fixado em 2 para Vazão, Totalizadores e Velocidade
        decimals = 2
        
        # Vazão (Registers 0,1)
        val_vazao = self.format_value(registers[0], registers[1], decimals)
        self.lbl_vazao.setText(val_vazao)
        
        # Totalizador Parcial (Registers 4,5)
        val_parcial = self.format_value(registers[4], registers[5], decimals)
        self.lbl_parcial.setText(val_parcial)
        
        # Totalizador Geral (Registers 6,7)
        val_geral = self.format_value(registers[6], registers[7], decimals)
        self.lbl_geral.setText(val_geral)
        
        # Velocidade (Registers 2,3 - Fixado em 2 casas)
        val_vel = self.format_value(registers[2], registers[3], 2)
        self.lbl_velocidade.setText(val_vel)
        
        # Status Execucao (Hreg[8] bit 0)
        status_word = registers[8]
        is_executing = (status_word & 1) != 0
        if is_executing:
            self.lbl_exec.setText("Executando")
            self.lbl_exec.setStyleSheet("background-color: #666666; color: lime; border: 1px solid white; padding: 5px;")
        else:
            self.lbl_exec.setText("Parada")
            self.lbl_exec.setStyleSheet("background-color: #666666; color: red; border: 1px solid white; padding: 5px;")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    app.setQuitOnLastWindowClosed(False)
    shared_mem = QSharedMemory("VBI_UniqueInstanceID")
    while not shared_mem.create(1):
        shared_mem.attach()
        shared_mem.detach()
        if shared_mem.create(1):
            break
        resposta = QMessageBox.warning(
            None, 
            "VBI já está em execução", 
            "O aplicativo já está aberto.\n\nFeche a outra janela primeiro e tente novamente.",
            QMessageBox.StandardButton.Retry | QMessageBox.StandardButton.Cancel
        )
        if resposta != QMessageBox.StandardButton.Retry:
            sys.exit(0)
            
    app.setQuitOnLastWindowClosed(True)
    window = VBIMainApp()
    window.show()
    sys.exit(app.exec())
