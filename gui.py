import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QFileDialog, 
                            QTextEdit, QSpinBox, QRadioButton, QButtonGroup,
                            QGroupBox, QScrollArea, QTableWidget, QTableWidgetItem,
                            QSizePolicy)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor, QFont
from tomasulo import Tomasulo

class TomasuloGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tomasulo Simulator")
        self.setMinimumSize(1200, 800)
        
        # Set application style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
            }
            QGroupBox {
                background-color: #363636;
                color: #ffffff;
                border: 2px solid #4a4a4a;
                border-radius: 6px;
                margin-top: 12px;
                font-weight: bold;
            }
            QGroupBox::title {
                color: #00b4d8;
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QLabel {
                color: #ffffff;
                font-size: 12px;
            }
            QPushButton {
                background-color: #00b4d8;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0096c7;
            }
            QPushButton:disabled {
                background-color: #666666;
            }
            QRadioButton {
                color: #ffffff;
                spacing: 8px;
            }
            QRadioButton::indicator {
                width: 16px;
                height: 16px;
            }
            QRadioButton::indicator:unchecked {
                border: 2px solid #00b4d8;
                border-radius: 8px;
            }
            QRadioButton::indicator:checked {
                background-color: #00b4d8;
                border: 2px solid #00b4d8;
                border-radius: 8px;
            }
            QSpinBox {
                background-color: #4a4a4a;
                color: white;
                border: 1px solid #666666;
                border-radius: 4px;
                padding: 4px;
            }
            QTextEdit {
                background-color: #1e1e1e;
                color: #00ff00;
                border: 2px solid #4a4a4a;
                border-radius: 6px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
            }
            QTableWidget {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 2px solid #4a4a4a;
                border-radius: 6px;
                gridline-color: #4a4a4a;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #363636;
                color: #00b4d8;
                padding: 5px;
                border: 1px solid #4a4a4a;
                font-weight: bold;
            }
        """)
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        self.layout = QVBoxLayout(main_widget)
        self.layout.setSpacing(20)
        self.layout.setContentsMargins(20, 20, 20, 20)
        
        # Create input section
        input_group = QGroupBox("Simulation Setup")
        input_layout = QVBoxLayout()
        input_layout.setSpacing(15)
        
        # File selection buttons
        file_layout = QHBoxLayout()
        self.inst_file_label = QLabel("Instructions File: Not selected")
        self.inst_file_btn = QPushButton("Select Instructions File")
        self.inst_file_btn.clicked.connect(self.select_inst_file)
        file_layout.addWidget(self.inst_file_label)
        file_layout.addWidget(self.inst_file_btn)
        input_layout.addLayout(file_layout)
        
        # Initial PC
        pc_layout = QHBoxLayout()
        pc_layout.addWidget(QLabel("Initial PC:"))
        self.pc_spin = QSpinBox()
        self.pc_spin.setRange(0, 9999)
        pc_layout.addWidget(self.pc_spin)
        input_layout.addLayout(pc_layout)
        
        # Hardware selection
        hw_layout = QHBoxLayout()
        hw_layout.addWidget(QLabel("Hardware:"))
        self.default_hw_radio = QRadioButton("Default")
        self.custom_hw_radio = QRadioButton("Custom")
        self.default_hw_radio.setChecked(True)
        hw_layout.addWidget(self.default_hw_radio)
        hw_layout.addWidget(self.custom_hw_radio)
        self.hw_file_btn = QPushButton("Select Hardware File")
        self.hw_file_btn.clicked.connect(self.select_hw_file)
        self.hw_file_btn.setEnabled(False)
        self.custom_hw_radio.toggled.connect(self.hw_file_btn.setEnabled)
        hw_layout.addWidget(self.hw_file_btn)
        input_layout.addLayout(hw_layout)
        
        # Memory initialization
        mem_layout = QHBoxLayout()
        mem_layout.addWidget(QLabel("Memory:"))
        self.no_mem_radio = QRadioButton("No Initialization")
        self.mem_init_radio = QRadioButton("Initialize")
        self.no_mem_radio.setChecked(True)
        mem_layout.addWidget(self.no_mem_radio)
        mem_layout.addWidget(self.mem_init_radio)
        self.mem_file_btn = QPushButton("Select Memory File")
        self.mem_file_btn.clicked.connect(self.select_mem_file)
        self.mem_file_btn.setEnabled(False)
        self.mem_init_radio.toggled.connect(self.mem_file_btn.setEnabled)
        mem_layout.addWidget(self.mem_file_btn)
        input_layout.addLayout(mem_layout)
        
        # Run button
        self.run_btn = QPushButton("Run Simulation")
        self.run_btn.setMinimumHeight(40)
        self.run_btn.clicked.connect(self.run_simulation)
        input_layout.addWidget(self.run_btn)
        
        input_group.setLayout(input_layout)
        self.layout.addWidget(input_group)
        
        # Create instruction table
        self.inst_table = QTableWidget()
        self.inst_table.setColumnCount(5)
        self.inst_table.setHorizontalHeaderLabels(["Instruction", "Issue", "Exec Start", "Exec End", "Write Back"])
        self.inst_table.horizontalHeader().setStretchLastSection(True)
        self.inst_table.setVisible(False)  # Initially hidden
        self.inst_table.setFixedHeight(250)  # Set a smaller fixed height
        self.layout.addWidget(self.inst_table)
        
        # Add misprediction rate label
        self.misprediction_label = QLabel()
        self.misprediction_label.setStyleSheet("color: #00ff00; font-size: 14px;")
        self.misprediction_label.setVisible(False)  # Initially hidden
        self.layout.addWidget(self.misprediction_label)
        
        # Create reservation stations table
        self.setupReservationStations()
        
        # Output section
        output_group = QGroupBox("Simulation Output")
        output_layout = QVBoxLayout()
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setStyleSheet("background-color: #1e1e1e; color: #ffffff;")
        output_layout.addWidget(self.output_text)
        output_group.setLayout(output_layout)
        self.layout.addWidget(output_group)
        
        # Initialize file paths
        self.inst_file = ""
        self.hw_file = ""
        self.mem_file = ""
        self.simulator = None
        
        # Redirect stdout to our text widget
        sys.stdout = self
        
    def write(self, text):
        self.output_text.append(text.rstrip())
        
    def flush(self):
        pass
        
    def select_inst_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Instructions File", "", "Text Files (*.txt)")
        if file_name:
            self.inst_file = file_name
            self.inst_file_label.setText(f"Instructions File: {file_name}")
            
    def select_hw_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Hardware File", "", "Text Files (*.txt)")
        if file_name:
            self.hw_file = file_name
            
    def select_mem_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Memory File", "", "Text Files (*.txt)")
        if file_name:
            self.mem_file = file_name
            
    def update_instruction_table(self):
        if not self.simulator:
            return
            
        self.inst_table.setRowCount(len(self.simulator.program))
        for i, inst in enumerate(self.simulator.program):
            self.inst_table.setItem(i, 0, QTableWidgetItem(inst.inst))
            self.inst_table.setItem(i, 1, QTableWidgetItem(str(inst.issue)))
            self.inst_table.setItem(i, 2, QTableWidgetItem(str(inst.execSt)))
            self.inst_table.setItem(i, 3, QTableWidgetItem(str(inst.execEnd)))
            self.inst_table.setItem(i, 4, QTableWidgetItem(str(inst.write)))
            
        # Update misprediction rate
        misprediction_rate = self.simulator.misprediction / self.simulator.numBne if self.simulator.numBne else 0
        self.misprediction_label.setText(
            f"Branch Instructions: {self.simulator.numBne}\n"
            f"Mispredictions: {self.simulator.misprediction}\n"
            f"Misprediction Rate: {misprediction_rate:.2%}"
        )
        self.misprediction_label.setVisible(True)
            
    def run_simulation(self):
        if not self.inst_file:
            self.output_text.append("Error: Please select an instructions file")
            return
            
        try:
            # Create simulator instance
            self.simulator = Tomasulo(
                self.inst_file,
                self.default_hw_radio.isChecked(),
                self.hw_file,
                self.pc_spin.value()
            )
            
            # Initialize memory if requested
            if self.mem_init_radio.isChecked() and self.mem_file:
                self.simulator.readMem(self.mem_file)
                
            # Show instruction table
            self.inst_table.setVisible(True)
            self.misprediction_label.setVisible(True)
            
            # Run simulation
            self.simulator.initiateRunning()
            
            # Update displays
            self.update_instruction_table()
            self.updateReservationStations()
            
        except Exception as e:
            self.output_text.append(f"Error: {str(e)}")

    def setupReservationStations(self):
        # Create table for reservation stations
        self.rsTable = QTableWidget()
        self.rsTable.setColumnCount(8)
        self.rsTable.setHorizontalHeaderLabels(["Name", "Busy", "Op", "Vj", "Vk", "Qj", "Qk", "Addr"])
        self.rsTable.horizontalHeader().setStretchLastSection(True)
        self.rsTable.setVisible(False)  # Initially hidden
        self.rsTable.setFixedHeight(250)  # Set a smaller fixed height
        self.layout.addWidget(self.rsTable)

    def updateReservationStations(self):
        if not self.simulator:
            return
            
        # Clear existing items
        self.rsTable.setRowCount(0)
        
        # Add new items from simulator
        row = 0
        for stationType in range(self.simulator.nStationTypes):
            for i in range(self.simulator.stations[stationType]):
                station = self.simulator.reservationStations[stationType][i]
                self.rsTable.insertRow(row)
                self.rsTable.setItem(row, 0, QTableWidgetItem(station.name))
                self.rsTable.setItem(row, 1, QTableWidgetItem(str(station.busy)))
                self.rsTable.setItem(row, 2, QTableWidgetItem(station.op_str if station.op else ""))
                self.rsTable.setItem(row, 3, QTableWidgetItem(str(station.vj)))
                self.rsTable.setItem(row, 4, QTableWidgetItem(str(station.vk)))
                self.rsTable.setItem(row, 5, QTableWidgetItem(str(station.qj)))
                self.rsTable.setItem(row, 6, QTableWidgetItem(str(station.qk)))
                self.rsTable.setItem(row, 7, QTableWidgetItem(str(station.addr)))
                row += 1

def main():
    app = QApplication(sys.argv)
    window = TomasuloGUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 