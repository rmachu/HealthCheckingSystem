from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox,QSizePolicy,QApplication  
from PyQt5.QtCore import Qt
#Starting input page 
class InputPage(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.name = QLabel('Welcome, Rachel!', self)
        self.name.setAlignment(Qt.AlignCenter)  # Center align the text
        self.name.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)  # Ensure the label expands to fit content
        #Prompt user for weight and height 
        self.weight_label = QLabel('Weight (kg):', self)
        self.weight_input = QLineEdit(self)
        
        self.height_label = QLabel('Height (cm):', self)
        self.height_input = QLineEdit(self)
        #Submit
        self.submit_button = QPushButton('Submit', self)
        self.submit_button.clicked.connect(self.submit_data)
        
        layout = QVBoxLayout()
        weight_layout = QHBoxLayout()
        height_layout = QHBoxLayout()
        
        weight_layout.addWidget(self.weight_label)
        weight_layout.addWidget(self.weight_input)
        
        height_layout.addWidget(self.height_label)
        height_layout.addWidget(self.height_input)
        
        layout.addWidget(self.name)
        layout.addLayout(weight_layout)
        layout.addLayout(height_layout)
        layout.addWidget(self.submit_button)
        
        self.setLayout(layout)
        self.setWindowTitle('Enter Weight and Height')

    def submit_data(self):
        weight = self.weight_input.text()
        height = self.height_input.text()
        
        # Validate input data
        if not weight or not height:
            QMessageBox.warning(self, 'Error', 'Please enter both weight and height')
            return      
        try:
            weight = float(weight)
            height = float(height)
        except ValueError:
            QMessageBox.warning(self, 'Error', 'Please enter valid numbers for weight and height')
            return
        
        if weight <= 0 or height <= 0:
            QMessageBox.warning(self, 'Error', 'Please enter valid numbers for weight and height')
            return


        self.parent().input_complete(weight, height)
