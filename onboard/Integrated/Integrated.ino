// Sensor Board Integrated
// RSX - CanSat

//Libraries
#include <I2Cdev.h>
#include <MPU6050_6Axis_MotionApps20.h>
#include <SFE_BMP180.h>
#include<LiquidCrystal.h>
#include <Wire.h>


//I2C setup
MPU6050 mpu;
SFE_BMP180 pressure;

//pin Assignment
//MPU SDA = A4
//MPU SCL = A5
//MPU interupt = 2
#define thermister1 A0
#define thermister2 A1
#define motorPin 3
#define motor1 6
#define motor2 7
#define encoder 8
const int MPU=0x68; //I2C address of MPU


///////////////////////////////////////////////// Variables //////////////////////////////////////////////////////////////////
// MPU control/status vars
bool dmpReady = false;  // set true if DMP init was successful
uint8_t mpuIntStatus;   // holds actual interrupt status byte from MPU
uint8_t devStatus;      // return status after each device operation (0 = success, !0 = error)
uint16_t packetSize;    // expected DMP packet size (default is 42 bytes)
uint16_t fifoCount;     // count of all bytes currently in FIFO
uint8_t fifoBuffer[64]; // FIFO storage buffer

// orientation/motion vars
Quaternion q;           // [w, x, y, z]         quaternion container
VectorInt16 aa;         // [x, y, z]            accel sensor measurements
VectorInt16 aaReal;     // [x, y, z]            gravity-free accel sensor measurements
VectorInt16 aaWorld;    // [x, y, z]            world-frame accel sensor measurements
VectorFloat gravity;    // [x, y, z]            gravity vector
float euler[3];         // [psi, theta, phi]    Euler angle container
float ypr[3];           // [yaw, pitch, roll]   yaw/pitch/roll container and gravity vector

// Interupt Detection Routine
volatile bool mpuInterrupt = false;     // indicates whether MPU interrupt pin has gone high
void dmpDataReady() {
    mpuInterrupt = true;
}

//BPM ////////////////////////////
#define ALTITUDE 1655.0 // Altitude of SparkFun's HQ in Boulder, CO. in meters
double baseline; // baseline pressure
double altitude,pressure_reading;

//Thermister/////////////////////
int thermister_raw1;
int thermister_raw2;
int temp1;
int temp2;

////Stabilization System //////////////////
////Gyro Parameters
//int GyX,GyY,GyZ;
//float v_pitch;
//
////Control Parameters
//static float K = 0.1;
//static float TI = 0.2;
//static float Td = 0.1;
//static float pertubation = 0;
//
////Controls Variables 
//float controller;
//float error = 0.0;
//float error_prev = 0.0;
//float error_sum = 0.0; 
//float error_rate = 0.0;
//
////Encoder Parameters
//int val_new;
//int val_old;
//int clicks = 0;
//float rpm = 0.0;
//float timeold = 0.0;
//float timeold, timenew, timediff;


float time;

////////////////////////////////////////////// SETUP ////////////////////////////////////////////////////////////////
void setup() {
  
/////////////MPU 6050//////////////
   // join I2C bus (I2Cdev library doesn't do this automatically)
  #if I2CDEV_IMPLEMENTATION == I2CDEV_ARDUINO_WIRE
      Wire.begin();
      TWBR = 24; // 400kHz I2C clock (200kHz if CPU is 8MHz)
  #elif I2CDEV_IMPLEMENTATION == I2CDEV_BUILTIN_FASTWIRE
      Fastwire::setup(400, true);
  #endif

  // initialize serial communication
  Serial.begin(9600);
  while (!Serial); // wait for Leonardo enumeration, others continue immediately

  // initialize device
  Serial.println(F("Initializing I2C devices..."));
  mpu.initialize();

  // verify connection
  Serial.println(F("Testing device connections..."));
  Serial.println(mpu.testConnection() ? F("MPU6050 connection successful") : F("MPU6050 connection failed"));

 // load and configure the DMP
  Serial.println(F("Initializing DMP..."));
  devStatus = mpu.dmpInitialize();
  
  // supply your own gyro offsets here, scaled for min sensitivity
  mpu.setXGyroOffset(220);
  mpu.setYGyroOffset(76);
  mpu.setZGyroOffset(-85);
  mpu.setZAccelOffset(1688); // 1688 factory default for my test chip

  // make sure it worked (returns 0 if so)
  if (devStatus == 0) {
      // turn on the DMP, now that it's ready
      Serial.println(F("Enabling DMP..."));
      mpu.setDMPEnabled(true);

      // enable Arduino interrupt detection
      Serial.println(F("Enabling interrupt detection (Arduino external interrupt 0)..."));
      attachInterrupt(0, dmpDataReady, RISING);
      mpuIntStatus = mpu.getIntStatus();

      // set our DMP Ready flag so the main loop() function knows it's okay to use it
      Serial.println(F("DMP ready! Waiting for first interrupt..."));
      dmpReady = true;

      // get expected DMP packet size for later comparison
      packetSize = mpu.dmpGetFIFOPacketSize();
  } else {
      // ERROR!
      // 1 = initial memory load failed
      // 2 = DMP configuration updates failed
      // (if it's going to break, usually the code will be 1)
      Serial.print(F("DMP Initialization failed (code "));
      Serial.print(devStatus);
      Serial.println(F(")"));
  }
  
  ///////// BPM Set up ///////////////////
  if (pressure.begin())
    Serial.println("BMP180 init success");
  else
  {
    // Oops, something went wrong, this is usually a connection problem,
    // see the comments at the top of this sketch for the proper connections.

    Serial.println("BMP180 init fail\n\n");
    while(1); // Pause forever.
  }
  baseline = getPressure();
  
  ////////// Thermister Setup///////////////
  pinMode(thermister1,INPUT);
  pinMode(thermister2,INPUT);
  
  
//  ///////// Stabilization Setup ///////////////
//    //Wire the MPU6050 buffer
//  Wire.begin();
//  Wire.beginTransmission(MPU);
//  Wire.write(0x6B); //power management register 1
//  Wire.write(0);
//  Wire.endTransmission(true);
//  
//  //Motor Setup
//  pinMode(motorPin, OUTPUT);
//  pinMode(motor1,OUTPUT);
//  pinMode(motor2,OUTPUT);
//  digitalWrite(motor1,LOW);
//  digitalWrite(motor2,LOW); 
//  
//  //Encoder Setup
//  pinMode(encoder, INPUT);
//  val_new = digitalRead(encoder);
//  val_old = val_new;
//  timeold = millis();

  time = millis();
  
}


void loop() {
  
  /////////////MPU 6050//////////////
    // if programming failed, don't try to do anything
    if (!dmpReady){
     Serial.println("DMP not ready or did not initialize");
     return;
    }
    
    //I2C Loaded
    if (mpuInterrupt || fifoCount >= packetSize){
          // reset interrupt flag and get INT_STATUS byte
      mpuInterrupt = false;
      mpuIntStatus = mpu.getIntStatus();

      // get current FIFO count
      fifoCount = mpu.getFIFOCount();

      // check for overflow (this should never happen unless our code is too inefficient)
      if ((mpuIntStatus & 0x10) || fifoCount == 1024) {
          // reset so we can continue cleanly
          mpu.resetFIFO();
          //Serial.println("OverFlow");
          
      // otherwise, check for DMP data ready interrupt (this should happen frequently)
      } else if (mpuIntStatus & 0x02) {
          // wait for correct available data length, should be a VERY short wait
          while (fifoCount < packetSize) fifoCount = mpu.getFIFOCount();

          // read a packet from FIFO
          mpu.getFIFOBytes(fifoBuffer, packetSize);
          
          // track FIFO count here in case there is > 1 packet available
          // (this lets us immediately read more without waiting for an interrupt)
          fifoCount -= packetSize;

          // display Euler angles in degrees
          mpu.dmpGetQuaternion(&q, fifoBuffer);
          mpu.dmpGetGravity(&gravity, &q);
          mpu.dmpGetYawPitchRoll(ypr, &q, &gravity);
          
          mpu.dmpGetAccel(&aa, fifoBuffer);
          mpu.dmpGetLinearAccel(&aaReal, &aa, &gravity);
  
      }
      
      
      
    }
   
 ///////////// BPM Pressure & Altitude ///////////////////////
 // Get a new pressure reading:
 pressure_reading = getPressure();
 altitude = pressure.altitude(pressure_reading,baseline);
 
 //////////// Thermister //////////////////////////////
 thermister_raw1 = analogRead(thermister1);
 thermister_raw2 = analogRead(thermister2);
 temp1 = Thermister(thermister_raw1);
 temp2 = Thermister(thermister_raw2);

if (millis()-time >= 1000){
////// Print ////////////////////
//Accel/Gyro
  Serial.print(aaReal.x);
  Serial.print(",");
  Serial.print(aaReal.y);
  Serial.print(",");
  Serial.print(aaReal.z);
  Serial.print(",");
  Serial.print(ypr[0] * 180/M_PI);
  Serial.print(",");
  Serial.print(ypr[1] * 180/M_PI);
  Serial.print(",");
  Serial.print(ypr[2] * 180/M_PI);
  Serial.print(",");
  
//Time
  Serial.print(time);
  Serial.print(",");
  
//Pressure 
  Serial.print(pressure_reading);
  Serial.print(",");
    
//Temperature
  Serial.print(temp1);
  Serial.print(",");
  Serial.print(temp2);
  Serial.print(",");
  
//Altitude
  Serial.println(altitude);
  
  time = millis();
}
  
  
  
//  ////////////////Stability System/////////////////////////////////
//    //Request MPU reading
//  Wire.beginTransmission(MPU); 
//  Wire.write(0x43); //starts with MPU register 43(GYRO_XOUT_H) 
//  Wire.endTransmission(false); 
//  Wire.requestFrom(MPU,6,true); //requests 6 registers 
//  GyX=Wire.read()<<8|Wire.read(); 
//  GyY=Wire.read()<<8|Wire.read();
//  GyZ=Wire.read()<<8|Wire.read(); 
//  
//  // Obtain Gyro Reading (deg/s)
//  v_pitch=(GyX/25); 
//  if(v_pitch==-1){
//      v_pitch=0;
//  } 
//
//  //Obtain Encoder Reading (deg/s)
//  val_new = digitalRead(encoder);
//  if(val_new != val_old) {
//        if(clicks == 8) {            //Update every 4 clicks - 48 clicks is one revolution in this case
//            clicks = 1;
//            timeold =(float) (millis()-timeold);
//            rpm = (166.666666666666666666/timeold)*360; 
//            timeold = millis();
//
//            //Obtain Error
//            error = abs(v_pitch) - rpm;
//            error_sum += error;
//            error_rate = (error-error_prev)/(millis()-time);
//  
//            error_prev = error;  
//            time = millis();   
//  
//       }
//       else clicks++;   
//       val_old = val_new;
//  }
//  else error_sum = 0;
//
//  //Controls
//  controller = K*(abs(v_pitch)+TI*error_sum+Td*error_rate);
//  Serial.println(controller);
//  
//  //Obtain Direction (ignore small pertubations
//  if(v_pitch > pertubation){
//      digitalWrite(motor1,LOW);
//      digitalWrite(motor2,HIGH);
//  }
//  else if(v_pitch < -pertubation){
//      digitalWrite(motor1,HIGH);
//      digitalWrite(motor2,LOW);
//  }
//  else{
//      digitalWrite(motor1,LOW);
//      digitalWrite(motor2,LOW);
//  }
//  
//  analogWrite(motorPin,abs(controller));

 
}

double getPressure()
{
  char status;
  double T,P,p0,a;

  // You must first get a temperature measurement to perform a pressure reading.
  
  // Start a temperature measurement:
  // If request is successful, the number of ms to wait is returned.
  // If request is unsuccessful, 0 is returned.

  status = pressure.startTemperature();
  if (status != 0)
  {
    // Wait for the measurement to complete:

    delay(status);

    // Retrieve the completed temperature measurement:
    // Note that the measurement is stored in the variable T.
    // Use '&T' to provide the address of T to the function.
    // Function returns 1 if successful, 0 if failure.

    status = pressure.getTemperature(T);
    if (status != 0)
    {
      // Start a pressure measurement:
      // The parameter is the oversampling setting, from 0 to 3 (highest res, longest wait).
      // If request is successful, the number of ms to wait is returned.
      // If request is unsuccessful, 0 is returned.

      status = pressure.startPressure(3);
      if (status != 0)
      {
        // Wait for the measurement to complete:
        delay(status);

        // Retrieve the completed pressure measurement:
        // Note that the measurement is stored in the variable P.
        // Use '&P' to provide the address of P.
        // Note also that the function requires the previous temperature measurement (T).
        // (If temperature is stable, you can do one temperature measurement for a number of pressure measurements.)
        // Function returns 1 if successful, 0 if failure.

        status = pressure.getPressure(P,T);
        if (status != 0)
        {
          return(P);
        }
        else Serial.println("error retrieving pressure measurement\n");
      }
      else Serial.println("error starting pressure measurement\n");
    }
    else Serial.println("error retrieving temperature measurement\n");
  }
  else Serial.println("error starting temperature measurement\n");
}

double Thermister(int RawADC) {
  double Temp;
  // See http://en.wikipedia.org/wiki/Thermistor for explanation of formula
  Temp = log(((10240000/RawADC) - 10000));
  Temp = 1 / (0.001129148 + (0.000234125 * Temp) + (0.0000000876741 * Temp * Temp * Temp));
  Temp = Temp - 273.15;           // Convert Kelvin to Celcius
  return Temp;
}

