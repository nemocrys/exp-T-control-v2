/*
  Kaspars Dadzis, Berlin, 2022
  Program to emulate an Eurotherm PID controller using arduino
  ---------- CHANGES:
*/
// --------------------------------------------------------------------------------
// ----------------------------------------- Variablen deklarieren:----------------
// - Vincent Funke - 1.2.22 - Beginn
String eingabe = "";
String code = "";

// Steuerzeichen:
const char STX = 2;
const char ETX = 3;
const char EOT = 4;
const char ENQ = 5;
const char ACK = 6;

// Boolsche Variablen:
bool schreiben;
bool lesen;
bool einlesen;
bool befehl_fertig;
// - Vincent Funke - 1.2.22 - Ende
// --------------------------------------------------------------------------------

// --------------------------------------------------------------------------------
// ---------------------------------------- Pins on Arduino
// --------------------------------------------------------------------------------

const int pinMAX31865_CS = 10;
const int pinMAX31865_DI = 11;
const int pinMAX31865_DO = 12;
const int pinMAX31865_CLK = 9;
const int pinMAX31865_CS_2 = 7;

const int RelayPin = 23;
const int DACVoltagePin = A1;

// --------------------------------------------------------------------------------
// ---------------------------------------- Misc libraries
// --------------------------------------------------------------------------------

#include <SPI.h>
#include "TimerOne.h"
#include <Wire.h>

// --------------------------------------------------------------------------------
// ---------------------------------------- Adafruit
// --------------------------------------------------------------------------------

#include "Adafruit_MAX31865.h"

// The value of the Rref resistor. Use 430.0 for PT100 and 4300.0 for PT1000
#define DDRREF      431.0
// The 'nominal' 0-degrees-C resistance of the sensor
// 100.0 for PT100, 1000.0 for PT1000
#define DDRNOMINAL  100.0

// Use software SPI: CS, DI, DO, CLK
Adafruit_MAX31865 oMAX31865 = Adafruit_MAX31865(pinMAX31865_CS, pinMAX31865_DI, pinMAX31865_DO, pinMAX31865_CLK);

// --------------------------------------------------------------------------------

float MAX31865_get()
{
  if (oMAX31865.readFault()) {
    oMAX31865.clearFault();  // possible problem
  }
  if (!oMAX31865.readFault())
  {
    return oMAX31865.temperature(DDRNOMINAL, DDRREF); //uses 79 ms time
  }
  else return -99.0;
}

// --------------------------------------------------------------------------------
// ---------------------------------------- DAC
// --------------------------------------------------------------------------------

#define DDPIDLimitMinDAC     0
#define DDPIDLimitMaxDAC     0.8

float PIDOutputDACvolts = 0;
float PIDOutputDACvoltsCheck = 0;
int PIDOutputDACbits = 0;
const int PIDOutputDACbitsMax = trunc(DDPIDLimitMaxDAC*4095.0/5.0);

#include "MCP4725.h"

MCP4725 dac(0x62);

// --------------------------------------------------------------------------------
// ---------------------------------------- PID
// --------------------------------------------------------------------------------

// Define Heating on/off vs. Pin level
#define DDHeatingOFF LOW
#define DDHeatingON  HIGH

#define DDPIDSetpointMIN 0
#define DDPIDSetpointMAX 400
#define DDPIDInputMIN 0
#define DDPIDInputMAX 400

#define DDPIDWindowSize 20000
// Zurzeit noch nicht veränderbar über Befehle
#define DDPIDLimitMin   0   //1000
#define DDPIDLimitMax   100 //10000
#define DDPIDLimitMinRelay   1000
#define DDPIDLimitMaxRelay   10000

#define DDPIDSampleRate 200
#define DDPIDSampleRateMicro 200000
#define DDPIDSampleRateOutMicro 20000

int PIDWindowSize;
unsigned long PIDwindowStartTime;
float PIDInputAVRfilt = 0.1; // avr = coef*val + (1-coef)*avr

double PIDSetpoint = 20, PIDInput = 20, PIDOutput = 0;
double PIDInputAVR = 0, PIDInputACT = 0;

// --------------------------------------------------------------------------------

// Slight modifications of:
// https://github.com/br3ttb/Arduino-PID-Library
#include "PID_v2.h"

//PID myPID(&Input, &Output, &Setpoint, Kp, Ki, Kd, DIRECT);
PID myPID(&PIDInput, &PIDOutput, &PIDSetpoint, 200, 0.3, 0, DIRECT);

// --------------------------------------------------------------------------------

void DriveOutput()
{

  // Works as slow PWM: output between 0 and Window size

  unsigned long now = millis();
  if (now - PIDwindowStartTime > PIDWindowSize)
  { //time to shift the Relay Window
    PIDwindowStartTime += PIDWindowSize;
  }

  // Pulses under 1000 ms are ignored!
  // This should coincide with the lower limit of the PID!

  float PIDOutputRelay = PIDOutput/100.0*PIDWindowSize;

  if (PIDOutputRelay > DDPIDLimitMinRelay && (PIDOutputRelay > now - PIDwindowStartTime) ) digitalWrite(RelayPin, DDHeatingON);
  else digitalWrite(RelayPin, DDHeatingOFF);

}

// --------------------------------------------------------------------------------

// Timer Interrupt Handler DDPIDSampleRateOutMicro = 20 ms
void TimerInterruptRelay()
{

  //if ( PIDInput < DDPIDInputMIN || PIDInput > DDPIDInputMAX )
  //{
  //  digitalWrite(RelayPin, DDHeatingOFF);  // make sure relay is off
  //}
  //else
  //{
  DriveOutput();
  //}

}

// --------------------------------------------------------------------------------
// ---------------------------------------- *** SETUP ***
// --------------------------------------------------------------------------------

// - Vincent Funke - 1.2.22 - Beginn
// Berechnung von BCC:
char BCC (String befehl, String wert)
{
  int bcc = 0;
  // Mnemonic in BCC
  int st_length = befehl.length();
  for (int i = 0; i < st_length; i += 1)
  {
    char n = befehl[i];
    bcc = bcc ^ n;
  }
  // Wert in BCC
  int st_length1 = wert.length();
  for (int i = 0; i < st_length1; i += 1)
  {
    char n = wert[i];
    bcc = bcc ^ n;
  }
  //Steuerzeichen in BCC
  char ETX = 3; //nimmt es als DEC
  bcc = bcc ^ ETX;
  return char(bcc); //Antwort als DEC
} // Char BCC

// Ausführung Befehl Lesen und Schreiben:
void Eurotherm(String befehl, String value, bool solllesen, bool sollschreiben)
{
  String antwort;

  if (solllesen) // Lesen:
  {
    if (befehl == "PV")
    {
      float val = MAX31865_get();
      String ans = String(val, 1);
      char bcc = BCC(befehl, ans);
      Serial.write(STX);
      antwort = "PV" + ans + ETX + bcc;
      Serial.print(antwort);
    } // if PV

    if (befehl == "II")
    {
      String ans = ">9050"; 
      char bcc = BCC(befehl, ans);
      Serial.write(STX);
      antwort = "II" + ans + ETX + bcc;
      Serial.print(antwort);
    } // if II

    if (befehl == "EE")
    {
      String ans = ">0000"; 
      char bcc = BCC(befehl, ans);
      Serial.write(STX);
      Serial.write("\x45\x45");
      antwort = ans + ETX + bcc; // EE wurde als \xee interpretiert! Darum das \x45\x45!
      Serial.print(antwort);
    } // if EE

    if (befehl == "V0")
    {
      String ans = ">0271"; 
      char bcc = BCC(befehl, ans);
      Serial.write(STX);
      antwort = "V0" + ans + ETX + bcc;
      Serial.print(antwort);
    } // if V0

    if (befehl == "HS")
    {
      String ans = String(DDPIDSetpointMAX);
      char bcc = BCC(befehl, ans);
      Serial.write(STX);
      antwort = "HS" + ans + ETX + bcc;
      Serial.print(antwort);
    } // if HS

    if (befehl == "LS")
    {
      String ans = String(DDPIDSetpointMIN);
      char bcc = BCC(befehl, ans);
      Serial.write(STX);
      antwort = "LS" + ans + ETX + bcc;
      Serial.print(antwort);
    } // if LS

    if (befehl == "11H")
    {
      String ans = String(DDPIDInputMAX);
      char bcc = BCC(befehl, ans);
      Serial.write(STX);
      antwort = "11H" + ans + ETX + bcc;
      Serial.print(antwort);
    } // if 11H

    if (befehl == "11L")
    {
      String ans = String(DDPIDInputMIN);
      char bcc = BCC(befehl, ans);
      Serial.write(STX);
      antwort = "11L" + ans + ETX + bcc;
      Serial.print(antwort);
    } // if 11L

    if (befehl == "XP")
    {
      float kp = myPID.GetKp();
      String ans = String(kp, 1);
      char bcc = BCC(befehl, ans);
      Serial.write(STX);
      antwort = "XP" + ans + ETX + bcc;
      Serial.print(antwort);
    } // if XP

    if (befehl == "TI")
    {
      float ki = myPID.GetKi();
      String ans = String(ki, 1);
      char bcc = BCC(befehl, ans);
      Serial.write(STX);
      antwort = "TI" + ans + ETX + bcc;
      Serial.print(antwort);
    } // if TI

    if (befehl == "TD")
    {
      float kd = myPID.GetKd();
      String ans = String(kd, 1);
      char bcc = BCC(befehl, ans);
      Serial.write(STX);
      antwort = "TD" + ans + ETX + bcc;
      Serial.print(antwort);
    } // if TD

    if (befehl == "SL")
    {
      float Sollwert = PIDSetpoint;
      String ans = String(Sollwert, 0);
      char bcc = BCC(befehl, ans);
      Serial.write(STX);
      antwort = "SL" + ans + ETX + bcc;
      Serial.print(antwort);
    } // if SL

    if (befehl == "OP")
    {
      float Leistung = 0;
      if (PIDOutput > DDPIDLimitMin){Leistung = PIDOutput/DDPIDWindowSize * 100;}
      String ans = String(Leistung, 1);
      char bcc = BCC(befehl, ans);
      Serial.write(STX);
      antwort = "O1" + ans + ETX + bcc;
      Serial.print(antwort);
    } // if OP

    if (befehl == "HO")
    {
      float OP_Max = DDPIDLimitMax/DDPIDWindowSize * 100;
      String ans = String(OP_Max, 0);
      char bcc = BCC(befehl, ans);
      Serial.write(STX);
      antwort = "HO" + ans + ETX + bcc;
      Serial.print(antwort);
    } // if HO
  } // if

  if (sollschreiben)     // Schreiben:
  {
    if (befehl == "SL")
    {
      Serial2.println("Vorher: " + String(PIDSetpoint, 0));
      PIDSetpoint = value.toFloat();
      Serial2.println("Nachher: " + String(PIDSetpoint, 0));
      if ( PIDSetpoint < DDPIDSetpointMIN ) PIDSetpoint = DDPIDSetpointMIN;
      if ( PIDSetpoint > DDPIDSetpointMAX ) PIDSetpoint = DDPIDSetpointMAX;
      Serial.write(ACK);
    } // if SL

    if (befehl == "XP")
    {
      float val = value.toFloat();
      
      float kp = myPID.GetKp();
      float ki = myPID.GetKi();
      float kd = myPID.GetKd();
      
      if (val >= 0 && val <= 1e4) {kp = val; Serial2.println("  p = " + String(kp)); }
      myPID.SetTunings(kp, ki, kd);
      Serial.write(ACK);
    } // if XP

    if (befehl == "TI")
    {
      float val = value.toFloat();
      
      float kp = myPID.GetKp();
      float ki = myPID.GetKi();
      float kd = myPID.GetKd();
      
      if (val >= 0 && val <= 1e4) {ki = val; Serial2.println("  i = " + String(ki)); }
      myPID.SetTunings(kp, ki, kd);
      Serial.write(ACK);
    } // if TI

    if (befehl == "TD")
    {
      float val = value.toFloat();
      
      float kp = myPID.GetKp();
      float ki = myPID.GetKi();
      float kd = myPID.GetKd();
      
      if (val >= 0 && val <= 1e4) {kd = val; Serial2.println("  d = " + String(kd)); }
      myPID.SetTunings(kp, ki, kd);
      Serial.write(ACK);
    } // if TD

    if (befehl == "OP") // OP ist nur unter bestimmten Bedingung in Eurotherm schreibbar - der Befehl dient hier zur zusammenarbeit zwische Arduino und Eurotherm
    {
      float val = value.toFloat();
      PIDOutput = val/100 * DDPIDWindowSize;
      if (PIDOutput > DDPIDLimitMax) {PIDOutput = DDPIDLimitMax;}
      Serial2.println("Ausgangsleistung = " + String(PIDOutput));
    }// if OP
    
    /*
    if (befehl == "HO")
    {
      float val = value.toFloat();
      DDPIDLimitMax = val/100 * DDPIDWindowSize;
      Serial2.println("Maximale Ausgangsleistung = " + String(DDPIDLimitMax));
    } // if HO
    */
  } // if (sollschreiben)
} // void Eurotherm
// - Vincent Funke - 1.2.22 - Ende

void setup() {


  Serial.begin(19200, SERIAL_8N1);
  Serial2.begin(9600);

  // ---

  oMAX31865.begin(MAX31865_4WIRE);

  // ---

  dac.begin();

  // ---

  pinMode(RelayPin, OUTPUT);
  digitalWrite(RelayPin, DDHeatingOFF);

  Timer1.initialize(DDPIDSampleRateOutMicro);
  Timer1.attachInterrupt(TimerInterruptRelay);

  PIDWindowSize = DDPIDWindowSize;
  PIDwindowStartTime = millis();

  myPID.SetOutputLimits(DDPIDLimitMin, DDPIDLimitMax);
  myPID.SetSampleTime(DDPIDSampleRate);
  myPID.SetMode(MANUAL); //AUTOMATIC or MANUAL

  PIDInput = MAX31865_get();

  // - Vincent Funke - 1.2.22 - Beginn
  // --- 
  pinMode(7, OUTPUT);  // LED Test

  // ---
  // Variablen belegen:
  schreiben = false;
  lesen = false;
  einlesen = true;
  befehl_fertig = false;
  // - Vincent Funke - 1.2.22 - Ende
}

// --------------------------------------------------------------------------------
// ---------------------------------------- *** LOOP ***
// --------------------------------------------------------------------------------

void loop() {

  //Serial2.println("Hello!");   // Testzeile für die zweite Schnittstelle
  

  // ---------------------------------------- Serial input/output
  // - Vincent Funke - 1.2.22 - Beginn
  // Lesebefehle:
  // EOT UID UID GID GID Befehl ENQ - ans Gerät
  // STX Befehl Wert ETX BCC        - Antwort vom Gerät
  // Schreibbefehl:
  // EOT UID UID GID GID STX Befehl Wert ETX BCC  - ans Gerät
  // NAK oder ACK                                 - Antwort vom Gerät

  // Befehl auslesen und zusammen setzten:
  if (Serial.available() > 0 || befehl_fertig)   
  {
    char inp = Serial.read();

    if (inp>31) Serial2.println(inp); else Serial2.println(inp, DEC); 

    if (!einlesen)
    {
      // Test/Debug mit einer zweiten Schnittstelle:
      // Kaspars Dadzis, Berlin, 2022
      Serial2.print("Befehl = ");
      char buff[code.length() + 1];
      code.toCharArray(buff, code.length() + 1);
  
      for (int i=0; i<code.length(); i++)
        {
        if (buff[i]>31) Serial2.print(buff[i]); else Serial2.print(buff[i], DEC); 
        }
      Serial2.println("\n");
      // Kaspars Dadzis, Berlin, 2022
      
      Eurotherm(code, eingabe, lesen, schreiben);
      // Werte zurücksetzten für nächsten Befehl
      schreiben = false;
      lesen = false;
      einlesen = true;
      befehl_fertig = false;
      eingabe = "";
      code = "";
      digitalWrite(7, HIGH); 
      delay(100); 
      digitalWrite(7, LOW); 
      delay(100); 

      // Überprüfung der Spannungs Werte:
      // - Vincent Funke - 1.2.22 - Beginn
      // Wenn man es hier printet, gehören diese Werte nicht zu der Darüberliegenden Ausgaangsleistung, sondern zur nächsten!!! 
      Serial2.println("PIDOutputDACvolts      = " + String(PIDOutputDACvolts));
      Serial2.println("PIDOutputDACbits       = " + String(PIDOutputDACbits));
      Serial2.println("PIDOutputDACvoltsCheck = " + String(PIDOutputDACvoltsCheck));
      Serial2.println("DDPIDLimitMaxDAC       = " + String(DDPIDLimitMaxDAC));
      // Vincent Funke - 1.2.22 - Ende
    } // if
    else // einlesen = true
    {
      switch (inp) {
        case 2: // STX
          schreiben = true;
          break;
        case 3: //ETX
          einlesen = false; // Alles wichtige wurde bearbeitet! Stoppe einlesen der Daten!
          digitalWrite(7, HIGH); 
          delay(100); 
          digitalWrite(7, LOW); 
          delay(100); 
          break;
        case 4: //EOT
          break;
        case 5: //ENQ
          lesen = true;
          einlesen = false; // Alles wichtige wurde bearbeitet! Stoppe einlesen der Daten!
          befehl_fertig = true; 
          digitalWrite(7, HIGH); 
          delay(100); 
          digitalWrite(7, LOW); 
          delay(100);
          break;
        case 46:
          eingabe += '.'; break;
        case 48:
          eingabe += '0'; break;
        case 49:
          eingabe += '1'; break;
        case 50:
          eingabe += '2'; break;
        case 51:
          eingabe += '3'; break;
        case 52:
          eingabe += '4'; break;
        case 53:
          eingabe += '5'; break;
        case 54:
          eingabe += '6'; break;
        case 55:
          eingabe += '7'; break;
        case 56:
          eingabe += '8'; break;
        case 57:
          eingabe += '9'; break;
        case 68:
          eingabe += 'D'; break;
        case 69:
          eingabe += 'E'; break;
        case 72:
          eingabe += 'H'; break;
        case 73:
          eingabe += 'I'; break;
        case 76:
          eingabe += 'L'; break;
        case 79:
          eingabe += 'O'; break;
        case 80:
          eingabe += 'P'; break;
        case 83:
          eingabe += 'S'; break;
        case 84:
          eingabe += 'T'; break;
        case 86:
          eingabe += 'V'; break;
        case 88:
          eingabe += 'X'; break;
        default: // alle anderen Zeichen werden ignoriert (BCC - Zeichen), sollte BCC einem Zeichen von Oben entsprechen, so wird es durch einlesen = false verhindert
          break;
      } // switch
      if (eingabe == "0033") {eingabe = "";} // Nur Adresse 03 Möglich     
      if (eingabe == "PV") {code = "PV"; eingabe = ""; }
      if (eingabe == "EE") {code = "EE"; eingabe = ""; }
      if (eingabe == "II") {code = "II"; eingabe = ""; }
      if (eingabe == "V0") {code = "V0"; eingabe = ""; }
      if (eingabe == "11H") {code = "11H"; eingabe = ""; }
      if (eingabe == "11L") {code = "11L"; eingabe = ""; }
      if (eingabe == "HS") {code = "HS"; eingabe = ""; }
      if (eingabe == "LS") {code = "LS"; eingabe = ""; }
      if (eingabe == "XP") {code = "XP"; eingabe = ""; }
      if (eingabe == "TI") {code = "TI"; eingabe = ""; }
      if (eingabe == "TD") {code = "TD"; eingabe = ""; }
      if (eingabe == "SL") {code = "SL"; eingabe = ""; }
      if (eingabe == "OP") {code = "OP"; eingabe = ""; }
      if (eingabe == "HO") {code = "HO"; eingabe = ""; }
    }// else
  } // if Serial.available
  // - Vincent Funke - 1.2.22 - Ende
  // ---------------------------------------- PID update

  if ( PIDSetpoint < DDPIDSetpointMIN ) PIDSetpoint = DDPIDSetpointMIN;
  if ( PIDSetpoint > DDPIDSetpointMAX ) PIDSetpoint = DDPIDSetpointMAX;

  // if not true, PIDInputACT, PIDInput, PIDInputAVR, PIDOutput remain constant!
  bool PIDrealc = myPID.Compute();

  if (PIDrealc) //i.e. Compute above uses the previous PIDInput value!
  {
    PIDInputACT = MAX31865_get();

    //skip PID if sensors are out of range
    if ( PIDInputACT > DDPIDInputMIN || PIDInputACT < DDPIDInputMAX )
    {
      //filter digitally using a low pass filter
      PIDInputAVR = PIDInputAVRfilt * PIDInputACT + (1 - PIDInputAVRfilt) * PIDInputAVR;

      PIDInput = PIDInputAVR;
    } //if
  } // if (PIDrealc)
  // Set DAC output


  //DDPIDLimitMin=0...DDPIDLimitMax=100 -> 0...5V
  //float PIDOutputDAC = (PIDOutput-DDPIDLimitMin)/(DDPIDLimitMax-DDPIDLimitMin);
  
  //DDPIDLimitMin=0...DDPIDLimitMax=100 -> 0...5V (max. power = 10V)
  PIDOutputDACvolts = 5.0*(PIDOutput-DDPIDLimitMin)/(DDPIDLimitMax-DDPIDLimitMin);
  if (PIDOutputDACvolts<0) PIDOutputDACvolts = 0;
  if (PIDOutputDACvolts>DDPIDLimitMaxDAC) PIDOutputDACvolts = DDPIDLimitMaxDAC; //Software limit

  // 0...5V -> 0...4095 bits
  PIDOutputDACbits = trunc(PIDOutputDACvolts*4095.0/5.0);
  dac.setValue(PIDOutputDACbits); 

  // Check for hardware voltage limit using diode
  PIDOutputDACvoltsCheck = analogRead(DACVoltagePin)*(5.0/1023.0);
  if ( PIDOutputDACvoltsCheck > DDPIDLimitMaxDAC )  dac.setValue(PIDOutputDACbitsMax);

} // loop

// --------------------------------------------------------------------------------
