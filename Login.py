from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
#Login page
class LoginPage(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self): #Ask for username and password
        self.username_label = QLabel('Username', self)
        self.username_input = QLineEdit(self)
        
        self.password_label = QLabel('Password', self)
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)
        
        self.login_button = QPushButton('Login', self)
        self.login_button.clicked.connect(self.check_login)
        
        layout = QVBoxLayout()
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)
        
        self.setLayout(layout)
        self.setWindowTitle('Login Page')
        
    def check_login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        #set up user name and password and validate
        if username == 'user' and password == 'pass':
            self.parent().login_successful()
        else:
            QMessageBox.warning(self, 'Error', 'Incorrect username or password')
