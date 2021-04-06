/*
Computer-aided switching of the Arduino 4-Relays Shield

It listens at the serial port for incoming bytes and checks 
whether any of them matches "0", "1", "2", "3", "4", "5", "6", "7", "8" or "9".

If byte "0" is detected, all relays close.
If byte "1" through "8" is detected, the according relay opens.
If byte "9" is detected, all relays open.

The board accessed may need to be changed depending on which board is actually used in the switchbox.
*/

// define variable 
int RELAY1 = 2;                       
int RELAY2 = 3;
int RELAY3 = 4;
int RELAY4 = 5;
int RELAY5 = 8;
int RELAY6 = 9;
int RELAY7 = 10;
int RELAY8 = 11;

void setup()
{    
// set Relays as Output
  pinMode(RELAY1, OUTPUT);    
  pinMode(RELAY2, OUTPUT);   
  pinMode(RELAY3, OUTPUT);   
  pinMode(RELAY4, OUTPUT);   
  pinMode(RELAY5, OUTPUT);  
  pinMode(RELAY6, OUTPUT);  
  pinMode(RELAY7, OUTPUT);  
  pinMode(RELAY8, OUTPUT);  

// Open serial communications and wait for port to open:
  Serial.begin(9600);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only
  }
  // send an intro:
  Serial.println("This is Uno. Ready to switch ...");
  Serial.println();
}

void loop()
{
  // get any incoming bytes:
  if (Serial.available() > 0) {
    char thisChar = Serial.read();
    
    // making sure the right byte has been received (for debugging):
    Serial.print("received: \'");
    Serial.print(thisChar);
    Serial.println("\'");

    // checking bytes with ASCII representations to open or close relays:
    if (thisChar == '1') {
      if (digitalRead(RELAY1)== 0) {
        digitalWrite(RELAY1, HIGH);  // Turns ON Relay1
        Serial.println("Switched on Relay 1");
      }
      else {
        digitalWrite(RELAY1, LOW);  // Turns OFF Relay1
        Serial.println("Switched off Relay 1");
      }
    }
    else if (thisChar == '2') {
      if (digitalRead(RELAY2)== 0) {
        digitalWrite(RELAY2, HIGH);  // Turns ON Relay1
        Serial.println("Switched on Relay 2");
      }
      else {
        digitalWrite(RELAY2, LOW);  // Turns OFF Relay1
        Serial.println("Switched off Relay 2");
      }
    }
    else if (thisChar == '3') {
      if (digitalRead(RELAY3)== 0) {
        digitalWrite(RELAY3, HIGH);  // Turns ON Relay1
        Serial.println("Switched on Relay 3");
      }
      else {
        digitalWrite(RELAY3, LOW);  // Turns OFF Relay1
        Serial.println("Switched off Relay 3");
      }
    }
    else if (thisChar == '4') {
      if (digitalRead(RELAY4)== 0) {
        digitalWrite(RELAY4, HIGH);  // Turns ON Relay1
        Serial.println("Switched on Relay 4");
      }
      else {
        digitalWrite(RELAY4, LOW);  // Turns OFF Relay1
        Serial.println("Switched off Relay 4");
      }
    }
    else if (thisChar == '5') {
      if (digitalRead(RELAY5)== 0) {
        digitalWrite(RELAY5, HIGH);  // Turns ON Relay1
        Serial.println("Switched on Relay 5");
      }
      else {
        digitalWrite(RELAY5, LOW);  // Turns OFF Relay1
        Serial.println("Switched off Relay 5");
      }
    }
    else if (thisChar == '6') {
      if (digitalRead(RELAY6)== 0) {
        digitalWrite(RELAY6, HIGH);  // Turns ON Relay1
        Serial.println("Switched on Relay 6");
      }
      else {
        digitalWrite(RELAY6, LOW);  // Turns OFF Relay1
        Serial.println("Switched off Relay 6");
      }
    }
    else if (thisChar == '7') {
      if (digitalRead(RELAY7)== 0) {
        digitalWrite(RELAY7, HIGH);  // Turns ON Relay1
        Serial.println("Switched on Relay 7");
      }
      else {
        digitalWrite(RELAY7, LOW);  // Turns OFF Relay1
        Serial.println("Switched off Relay 7");
      }
    }
    else if (thisChar == '8') {
      if (digitalRead(RELAY8)== 0) {
        digitalWrite(RELAY8, HIGH);  // Turns ON Relay1
        Serial.println("Switched on Relay 8");
      }
      else {
        digitalWrite(RELAY8, LOW);  // Turns OFF Relay1
        Serial.println("Switched off Relay 8");
      }
    }
    else if (thisChar == '9') {
      digitalWrite(RELAY1,HIGH);  // Turns ON Relay1
      digitalWrite(RELAY2,HIGH);  // Turns ON Relay2
      digitalWrite(RELAY3,HIGH);  // Turns ON Relay3
      digitalWrite(RELAY4,HIGH);  // Turns ON Relay4
      digitalWrite(RELAY5,HIGH);  // Turns ON Relay5
      digitalWrite(RELAY6,HIGH);  // Turns ON Relay6
      digitalWrite(RELAY7,HIGH);  // Turns ON Relay7
      digitalWrite(RELAY8,HIGH);  // Turns ON Relay8
      Serial.println("Switched on all Relays");
    }
    else if (thisChar == '0') {
      digitalWrite(RELAY1,LOW);  // Turns OFF Relay1
      digitalWrite(RELAY2,LOW);  // Turns OFF Relay2
      digitalWrite(RELAY3,LOW);  // Turns OFF Relay3
      digitalWrite(RELAY4,LOW);  // Turns OFF Relay4
      digitalWrite(RELAY5,LOW);  // Turns OFF Relay5
      digitalWrite(RELAY6,LOW);  // Turns OFF Relay6
      digitalWrite(RELAY7,LOW);  // Turns OFF Relay7
      digitalWrite(RELAY8,LOW);  // Turns OFF Relay8
      Serial.println("Switched off all Relays");
    }
  }
}
