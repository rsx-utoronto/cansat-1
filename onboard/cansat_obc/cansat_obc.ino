#include<Wire.h>
#include "Barometer.h"

int flight_state = 1;

// sensors
const int MPU = 0x68; // I2C address of the MPU-6050
float gyx, gyy, gyz;  // gyroscope xyz
float acx, acy, acz;  // accelerometer xyz
int hr, mn, sc;       // hour, minute, second

Barometer barometer;
float kpa, alt, tp1, atm;  // pressure, altitude, internal temperature, atmosphere

int baud_rate = 9600;

// buzzer
int buzzer_pin = 3;
int length = 15; // the number of notes
char notes[] = "ccggaagffeeddc "; // a space represents a rest
int beats[] = { 
  1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 2, 4 };
int tempo = 300;

// buzzer functions

void playTone(int tone, int duration) {
  for (long i = 0; i < duration * 1000L; i += tone * 2) {
    digitalWrite(buzzer_pin, HIGH);
    delayMicroseconds(tone);
    digitalWrite(buzzer_pin, LOW);
    delayMicroseconds(tone);
  }
}

void playNote(char note, int duration) {
  char names[] = { 
    'c', 'd', 'e', 'f', 'g', 'a', 'b', 'C'         };
  int tones[] = { 
    1915, 1700, 1519, 1432, 1275, 1136, 1014, 956         };
  for (int i = 0; i < 8; i++) {
    if (names[i] == note) {
      playTone(tones[i], duration);
    }
  }
}

void beep(int count) {

  for (int i = 0; i < count; i += 1) {
    for (long i = 0; i < 50 * 1000L; i += 100 * 2) {
      digitalWrite(buzzer_pin, HIGH);
      delayMicroseconds(100);
      digitalWrite(buzzer_pin, LOW);
      delayMicroseconds(100);
    } 
    delay(100);
  }
}

void readMPU() {
  Wire.beginTransmission(MPU);
  Wire.write(0x3B);  // starting with register 0x3B (ACCEL_XOUT_H)
  Wire.endTransmission(false);
  Wire.requestFrom(MPU,14,true);  // request a total of 14 registers
  acx = Wire.read()<<8|Wire.read();  // 0x3B (ACCEL_XOUT_H) & 0x3C (ACCEL_XOUT_L)     
  acy = Wire.read()<<8|Wire.read();  // 0x3D (ACCEL_YOUT_H) & 0x3E (ACCEL_YOUT_L)
  acz = Wire.read()<<8|Wire.read();  // 0x3F (ACCEL_ZOUT_H) & 0x40 (ACCEL_ZOUT_L)
  tp1 = Wire.read()<<8|Wire.read();  // 0x41 (TEMP_OUT_H) & 0x42 (TEMP_OUT_L)
  gyx = Wire.read()<<8|Wire.read();  // 0x43 (GYRO_XOUT_H) & 0x44 (GYRO_XOUT_L)
  gyy = Wire.read()<<8|Wire.read();  // 0x45 (GYRO_YOUT_H) & 0x46 (GYRO_YOUT_L)
  gyz = Wire.read()<<8|Wire.read();  // 0x47 (GYRO_ZOUT_H) & 0x48 (GYRO_ZOUT_L) 
}

void readBMP() {
  tp1 = barometer.bmp085GetTemperature(barometer.bmp085ReadUT());  // get the temperature
  kpa = barometer.bmp085GetPressure(barometer.bmp085ReadUP());     // get the pressure
  alt = barometer.calcAltitude(kpa);                               // uncompensated caculation - in meters
  atm = kpa / 101325;  
}

void setup() {

  // MPU6050
  Wire.begin();
  Wire.beginTransmission(MPU);
  Wire.write(0x6B);
  Wire.write(0);     // set to zero (wakes up the MPU-6050)
  Wire.endTransmission(true);
  Serial.begin(9600);

  // BMP180
  barometer.init();

  pinMode(buzzer_pin, OUTPUT);

}

void loop() {

  switch (flight_state) {

  case 1:
  
    beep(1);
    delay(30000);

    break;
    
  case 2:
  
    beep(2);
    delay(30000);

    break;  
    
  case 3:

    readMPU();
    readBMP();

    Serial.print(acx);
    Serial.print(",");
    Serial.print(acy);
    Serial.print(","); 
    Serial.print(acz);
    Serial.print(",");   
    Serial.print(gyx);
    Serial.print(",");
    Serial.print(gyy);
    Serial.print(","); 
    Serial.print(gyz);
    Serial.print(",");   
    Serial.print(tp1);
    Serial.print(",");
    Serial.print(alt);
    Serial.print(","); 
    Serial.println(kpa);

    delay(1000);

    break;

  case 4:
  
    beep(4);
    delay(30000);

    break;  
    
  case 5:

    for (int i = 0; i < length; i++) {
      if (notes[i] == ' ') {
        delay(beats[i] * tempo);
      } 
      else {
        playNote(notes[i], beats[i] * tempo);
      }

      // pause between notes
      delay(tempo / 2); 
    }

    break;

  default:
    break;

  }

}


