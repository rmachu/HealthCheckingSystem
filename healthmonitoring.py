import sys
import serial
import time
import threading
import requests
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QMessageBox
from PyQt5.QtCore import QTimer

# Configure the serial connection to the Arduino
ser = serial.Serial('/dev/ttyACM0', 115200)  # Adjust the serial port as needed
time.sleep(2)  # Wait for the serial connection to initialize
IFTTT_KEY = 'diV95Kkwlv38KjPMKlUS4T'
IFTTT_EVENT_NAME = 'sensor_trigger'
IFTTT_URL = f"https://maker.ifttt.com/trigger/{IFTTT_EVENT_NAME}/with/key/{IFTTT_KEY}"

# Thresholds for notifications
TEMP_THRESHOLD_HIGH = 39.0
TEMP_THRESHOLD_LOW = 26.0
HEART_RATE_THRESHOLD_HIGH = 185
GAS_THRESHOLD = 400

class SensorError(Exception):
    pass
#Send IFTTT notification
def send_ifttt_notification(value1):
    payload = {"value1": value1}
    response = requests.post(IFTTT_URL, json=payload)
    if response.status_code == 200:
        print("IFTTT notification sent successfully")
    else:
        print("Error sending IFTTT notification")
#read data received from the arduino
def read_sensor_data(command, duration=30, interval=1):
    readings = []
    start_time = time.time()
    ser.write('R'.encode())
    time.sleep(1)
    
    while time.time() - start_time < duration:
        ser.write(command.encode())
        line = ser.readline().decode('utf-8').strip()
        print(line)  # Debug: Print the raw data received
        try:
            if 'TMP007 not found!' in line:
                raise SensorError("TMP007 sensor not found. Please check the connection.")
            elif 'MAX30105 was not found' in line:
                raise SensorError("MAX30105 sensor not found. Please check the connection.")
            elif 'Gas sensor not found' in line:
                raise SensorError("Gas sensor not found. Please check the connection")
            elif '=' in line:
                label, value_str = line.split('=')
                reading = float(value_str)
                last_valid_reading = reading   # Append the reading to the list
            else:
                print("Error in reading")  # Debug: Indicate if '=' is missing
        except SensorError as e:
            return str(e)
        except (ValueError, IndexError) as e:
            print(f"Error processing line: {line} ({e})")  # Debug: Print errors in processing
            continue
    #if reading crosses threshold, send notification
    if last_valid_reading is not None:
        if command == 'T' and (last_valid_reading > TEMP_THRESHOLD_HIGH or average < TEMP_THRESHOLD_LOW):
            send_ifttt_notification(f"Temperature alert: {last_valid_reading:.2f} °C")
        elif command == 'P' and last_valid_reading > HEART_RATE_THRESHOLD_HIGH:
            send_ifttt_notification(f"Heart rate alert: {last_valid_reading:.2f} BPM")
        elif command == 'G' and last_valid_reading > GAS_THRESHOLD:
            send_ifttt_notification(f"Gas level alert: {last_valid_reading:.2f}")
        return last_valid_reading
    else:
        return None
#Main window for GUI
class HealthMonitorGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Health Monitoring System")
        self.setGeometry(100, 100, 400, 300)

        self.label_pulse = QLabel("Average Pulse: N/A", self)
        self.label_temp = QLabel("Average Body Temperature: N/A", self)
        self.label_gas = QLabel("Average Gas Level: N/A", self)

        self.button_pulse = QPushButton("Measure Pulse", self)
        self.button_temp = QPushButton("Measure Body Temperature", self)
        self.button_gas = QPushButton("Measure Gas Levels", self)
        self.button_finish = QPushButton("Finish", self)

        self.button_pulse.clicked.connect(self.measure_pulse)
        self.button_temp.clicked.connect(self.measure_temp)
        self.button_gas.clicked.connect(self.measure_gas)
        self.button_finish.clicked.connect(self.finish)

        layout = QVBoxLayout()
        layout.addWidget(self.label_pulse)
        layout.addWidget(self.button_pulse)
        layout.addWidget(self.label_temp)
        layout.addWidget(self.button_temp)
        layout.addWidget(self.label_gas)
        layout.addWidget(self.button_gas)
        layout.addWidget(self.button_finish)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        #Varibales for if each reading is completed
        self.pulse_reading_done = False
        self.temp_reading_done = False
        self.gas_reading_done = False
        
    #Set threading to ensure proper running of each method of the sensors
    def measure_pulse(self):
        threading.Thread(target=self._measure_pulse).start() 
    #Start measuring pulse
    def measure_pulse(self):
        pulse_avg = read_sensor_data('P', duration=30) #measure for 30 seconds
        if isinstance(pulse_avg, str): #If issues with system, show error 
            self.show_error(pulse_avg, self.measure_temp)
        elif pulse_avg is not None and pulse_avg != 0: 
            self.label_pulse.setText(f"Average Pulse: {pulse_avg:.2f} BPM") #Display final reading
            self.pulse_reading_done = True
        else:
           self.show_error("Pulse data could not be collected. Do you want to retry?") #IF error, ask user if retry
        self.parent().sensor_data['pulse'] = pulse_avg 
        
    def measure_temp(self):
        threading.Thread(target=self._measure_temp).start() 
    #Measure temperature 
    def measure_temp(self):
        temp_avg = read_sensor_data('T')
        if isinstance(temp_avg, str):
            self.show_error(temp_avg, self.measure_temp)
        elif temp_avg is not None and temp_avg != 0:
            self.label_temp.setText(f"Average Body Temperature: {temp_avg:.2f} °C")
            self.temp_reading_done = True     
        else:
            self.label_temp.setText("Failed to read temperature data.")
        self.parent().sensor_data['temperature'] = temp_avg

    def measure_gas(self):
        threading.Thread(target=self._measure_gas).start() 
    #Measure gas 
    def measure_gas(self):
        gas_avg = read_sensor_data('G')
        if isinstance(gas_avg, str):
            self.show_error(gas_avg, self.measure_temp)
        if gas_avg is not None and gas_avg != 0:
            self.label_gas.setText(f"Average Gas Level: {gas_avg:.2f}")
            self.gas_reading_done = True
        else:
            self.label_gas.setText("Failed to read gas data.")
        self.parent().sensor_data['gas'] = gas_avg
    #Method to show error box 
    def show_error(self, message, retry_function):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(message)
        msg.setWindowTitle("Error")
        msg.setStandardButtons(QMessageBox.Retry | QMessageBox.Close)
        ret = msg.exec_()
        if ret == QMessageBox.Retry: #Prompt user if they want to retry or quit
            retry_function()
        elif ret == QMessageBox.Close:
            QApplication.quit()
            
    #Finish to go to next page 
    def finish(self):
        if self.pulse_reading_done and self.temp_reading_done and self.gas_reading_done:
            self.parent().display_summary()
        else: #If all sensors are not read, show warning 
            QMessageBox.warning(self, "Incomplete Readings", "Please complete all readings before finishing.")
       

