from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QApplication
from datetime import datetime
import time
#Summary page 
class SummaryPage(QWidget):
    def __init__(self, weight, height, sensor_data):
        super().__init__()
        self.weight = weight
        self.height = height
        self.sensor_data = sensor_data
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        #Show data collected
        current_datetime = time.strftime("%Y-%m-%d %H:%M:%S")
        date_label = QLabel(f"Date and Time: {current_datetime}", self)

        weight_label = QLabel(f"Weight: {self.weight} kg", self)
        height_label = QLabel(f"Height: {self.height} cm", self)

        pulse_label = QLabel(f"Average Pulse: {self.sensor_data.get('pulse', 'N/A')} BPM", self)
        temp_label = QLabel(f"Average Temperature: {self.sensor_data.get('temperature', 'N/A')} °C", self)
        gas_label = QLabel(f"Average Gas Level: {self.sensor_data.get('gas', 'N/A')}", self)
        #Close button
        finish_button = QPushButton('Finish', self)
        finish_button.clicked.connect(self.close_program)
        
        layout.addWidget(date_label) 
        layout.addWidget(weight_label)
        layout.addWidget(height_label)
        layout.addWidget(pulse_label)
        layout.addWidget(temp_label)
        layout.addWidget(gas_label)
        layout.addWidget(finish_button)

        self.setLayout(layout)
        self.setWindowTitle('Summary Page')
        
    def close_program(self):
        QApplication.instance().quit()

        
