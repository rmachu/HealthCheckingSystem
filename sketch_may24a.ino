//Include libraries
#include <Wire.h>
#include "Adafruit_TMP007.h"
#include "MAX30105.h"
#include "heartRate.h"
//Define pins
#define MQ2pin A0
#define buzzerPin 8
//Declare variables
MAX30105 particleSensor;
Adafruit_TMP007 tmp007;
const byte RATE_SIZE = 4;
byte rates[RATE_SIZE];
byte rateSpot = 0;
long lastBeat = 0;
float beatsPerMinute;
int beatAvg;
float sensorValue;
float objt;

void setup() {
  Serial.begin(115200);
  pinMode(buzzerPin, OUTPUT);
  
  // Initialize sensors
  if (!tmp007.begin()) 
  {
    Serial.println("TMP007 not found!");
    while (1);
  }

  //Setup Biometric Sensor
  if (!particleSensor.begin(Wire, I2C_SPEED_FAST)) 
  {
    Serial.println("MAX30105 was not found. Please check wiring/power.");
    while (1);
  }
  Serial.println("Place your index finger on the sensor with steady pressure.");

  particleSensor.setup();
  particleSensor.setPulseAmplitudeRed(0x0A);
  particleSensor.setPulseAmplitudeGreen(0);
}

void loop() {
  //Check for proper hardware connection 
    static unsigned long lastCheck = 0;
    const unsigned long checkInterval = 5000; // Check every 5 seconds

  if (millis() - lastCheck >= checkInterval) {
    lastCheck = millis();
    checkSensors();
  }
  
  if (Serial.available() > 0) {
    char command = Serial.read();
    //Switch case for each sensor
    switch (command) {
      case 'R':
        resetSensor();
        break;
      case 'P':
        heartrate();
        break;
      case 'T':
        temp();
        break;
      case 'G':
        gas();
        break;
      default:
        break;
    }
    }
}

//Method for measuring pulse
void heartrate() {
  
  long irValue = particleSensor.getIR();

  if (checkForBeat(irValue)) {
    long delta = millis() - lastBeat;
    lastBeat = millis();

    beatsPerMinute = 60 / (delta / 1000.0);

    if (beatsPerMinute < 255 && beatsPerMinute > 20) 
    {
      rates[rateSpot++] = (byte)beatsPerMinute;
      rateSpot %= RATE_SIZE;

      beatAvg = 0;
      for (byte x = 0; x < RATE_SIZE; x++) 
        beatAvg += rates[x];
      beatAvg /= RATE_SIZE;
    }
  }

  Serial.print("Avg BPM=");
  Serial.println(beatAvg);
  //If finger is not on the sensor, trigger buzzer
  if (irValue < 50000) {
    Serial.println("No finger?");
    buzz();
  }
}
//Read temperature method
void temp() {
  float objt = tmp007.readObjTempC();
  Serial.print("Temperature=");
  Serial.println(objt);
  delay(4000);
}
//Read gas method
void gas() {
  sensorValue = analogRead(MQ2pin);
  //If readings are invalid or there are issues with sensor
   if (sensorValue < 0 || sensorValue > 1023) {
    Serial.println("Gas sensor not found or reading invalid.");
  } else {
    Serial.print("Gas=");
    Serial.println(sensorValue);
  }
  delay(2000);

}
//Buzzer method
void buzz()
{
  digitalWrite(buzzerPin, HIGH);
  delay(1000);
  digitalWrite(buzzerPin, LOW);
}
//Reset sensor when restarting program 
void resetSensor() 
{
  particleSensor.shutDown(); // Power down the sensor
  delay(100); // Wait for the sensor to fully power down
  particleSensor.wakeUp(); // Power up the sensor
  particleSensor.setup(); // Reinitialize the sensor
  lastBeat = 0;
  rateSpot = 0;
  for (byte i = 0; i < 4; i++) rates[i] = 0;
  beatAvg = 0;
  sensorValue = 0;
  objt = 0;
}
//Check if sensors are correctly setup
void checkSensors() {
  // Check TMP007 sensor
  float temperature = tmp007.readObjTempC();
  if (isnan(temperature) || temperature < -40.0 || temperature > 150.0) {
    Serial.println("TMP007 not found!");
  }

  // Check MAX30105 sensor by reading a value
  if (!particleSensor.safeCheck(500)) {
    Serial.println("MAX30105 was not found. Please check wiring/power.");
  }
}
