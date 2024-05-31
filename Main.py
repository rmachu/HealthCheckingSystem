import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QDesktopWidget
from Login import LoginPage
from inputpage import InputPage
from healthmonitoring import HealthMonitorGUI
from summarypage import SummaryPage
#Main class to set all the classes up 
class MainApplication(QMainWindow):
    def __init__(self):
        super().__init__()
        self.login_page = LoginPage()
        self.setCentralWidget(self.login_page)
        self.login_page.setParent(self)
        self.setWindowTitle('Health Checking System')
        self.resize(400, 300)  # Resize window
        self.center_window()
        self.show()
    #Login to input 
    def login_successful(self):
        self.input_page = InputPage()
        self.setCentralWidget(self.input_page)
        self.input_page.setParent(self)
        self.input_page.show()
    #Health monitor
    def input_complete(self, weight, height):
        self.weight = weight
        self.height = height
        self.sensor_data = {}
        self.health_monitor_gui = HealthMonitorGUI()
        self.setCentralWidget(self.health_monitor_gui)
        self.health_monitor_gui.show()
    #Summary page
    def display_summary(self):
        self.summary_page = SummaryPage(self.weight, self.height, self.sensor_data)
        self.setCentralWidget(self.summary_page)
        self.summary_page.show()
    #Center window
    def center_window(self):
        frame_geo = self.frameGeometry()
        screen_center = QDesktopWidget().availableGeometry().center()
        frame_geo.moveCenter(screen_center)
        self.move(frame_geo.topLeft()) 

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_app = MainApplication()
    sys.exit(app.exec_())