//#define DEBUG // Uncomment for debug outputs

#include <DFRobot_GP8403.h> // I2C DAC
#include <SoftwareI2C.h>    // Software I2C Bus
SoftwareI2C WireS1;         // USES THESE PINS; SDA: 2, SCL: 3 
#include <Wire.h>           // Hardware I2C Bus
DFRobot_GP8403 dac(&WireS1,0x5F);

/****GLOBAL VARIABLES****/
int PNPPin = 4; // PNP strobe for trigger
int NPNPin = 5; // Pin used to trigger NPN
int camPin = 7; // Pin used to trigger Camera
int analog = 1; // To set analog value
int PNP = 0; // To set PNP trigger level
int dPNP = 4; // PNP strobe for trigger
int onDelay = 200; // Time light is on before taking current measurment (ms)
byte digit[4]={0,0,0,0}; // Digits recieved from peek current meter
String peakCurrent = ""; // Assembled string of peek current
String input = ""; // Input string from PC (i.e. "C100" where c=mode & 100=expTime)
String outString = ""; // String sent back to PC
char mode = 0; // Mode of light, Selects measurment protocol
int expTime = 1; // Exposure time of camera; On time of light
String EOL = "}";
/************************/

/***FUNCTION PROTOTYPES***/
// - Measurement Protocols
String contMode();     // Continuous Mode
String overDrive();    // OverDrive Mode
String multiDrive();   // MultiDrive Mode
String dubOverDrive(); // Double OverDrive Mode
bool triggerCam(char);     // Triggers Camera for optical tests
// - Basic Functions
void readCurrent();    // Reads Peak Current Measurment
void trigNPN();        // Triggers NPN
void trigPNP(int);        // Triggers PNP
void NPNStrobe();      // Strobes NPN (used in OverDrive and Double OverDrive)
void PNPStrobe(int);      // Strobes PNP (used in OverDrive and Double OverDrive)
/***********************/

void setup() {
    Wire.begin(0x70); // Startup Hardware I2C as slave with addr 0x70
    Wire.onReceive(handler); // Set Handler for receiving I2C
    Wire.end();
    pinMode(NPNPin, OUTPUT);
    pinMode(camPin, OUTPUT);
    pinMode(dPNP, OUTPUT);
    digitalWrite(camPin, LOW);
    while(dac.begin()!=0){
        delay(1000); 
    }
    dac.setDACOutRange(dac.eOutputRange10V);
    Serial.begin(19200); // Set Baud Rate for Serial Communication
    Serial.print("SLA"); // Prints ID message
}//end setup()

void loop() {
    if (Serial.available() > 0){
        input = Serial.readString();
        mode = input.charAt(0);
        input.remove(0,1);
        expTime = input.toInt();
        if(mode != '\n'){
            switch (mode)
            {
            case 'C': // Continuous Mode
                triggerCam(mode);
                outString = contMode();        // Calls Continuous Measurment Protocol, Returns all Peak Current Measurments
                break;
            case 'O': // OverDrive Mode
                triggerCam(mode);
                outString = overDrive();
                outString = overDrive();       // Calls OverDrive Measurment Protocol, Returns all Peak Current Measurments
                break;
            case 'M': // MultiDrive Mode;
                triggerCam(mode);
                outString = multiDrive();      // Calls MultiDrive Measurment Protocol, Returns all Peak Current Measurments
                break;
            case 'D': // Double OverDrive Mode
                triggerCam(mode);
                outString = dubOverDrive();    // Calls Double Overdrive Measurment Protocol, Returns all Peak Current Measurments
                break;
            default:
                outString = "F";
                break;
            }//end switch
            outString += EOL;
            Serial.print(outString); // Send Data to PC
        }//end if
        Serial.flush();
        Serial.end();
        Serial.begin(19200);
    }//end if
}//end loop()

/**USER DEFINED FUNCTIONS**/
// - Basic Functions
void readCurrent(){
    Wire.begin(0x70);
    delay(500);
    Wire.end();
}

void trigNPN(){
    digitalWrite(NPNPin, HIGH); // light on
#ifdef DEBUG
    Serial.println("NPN ON");
#endif
    delay(onDelay);
    readCurrent();
    digitalWrite(NPNPin, LOW); // turn off light
#ifdef DEBUG
    Serial.println("NPN OFF");
#endif
}

void trigPNP(int level){
    dac.setDACOutVoltage(level, PNP); // light on PNP
#ifdef DEBUG
    Serial.println("PNP ON");
#endif
    delay(onDelay);
    readCurrent();
    dac.setDACOutVoltage(0, PNP); // light off PNP
#ifdef DEBUG
    Serial.println("PNP OFF");
#endif
}

void NPNStrobe(){
    Wire.begin(0x70);
    for(int x = 0; x < 200; x++){
            digitalWrite(NPNPin, HIGH);
            delay(2);
            digitalWrite(NPNPin, LOW);
            delay(3);
        }
    Wire.end();
}

void PNPStrobe(int level){
    dac.setDACOutVoltage(level, PNP); // light on PNP
    delay(100);
    Wire.begin(0x70);
    for(int x = 0; x < 200; x++){
            digitalWrite(dPNP, HIGH);
            delay(2);
            digitalWrite(dPNP, LOW);
            delay(3);
        }
    Wire.end();
}

void serialHandshake(){
    String hs = "";
    int timeOut = 0;
    hs = Serial.readString();
    while(hs != "K")// && timeOut <= 10000)
    {
        hs = Serial.readString();
        //Serial.print(hs);
        timeOut++;
    }
}
// - Measurement Protocols
String contMode(){
    String currentStr = "";
    dac.setDACOutVoltage(5000, analog); // 10v analog
    delay(200);
    trigNPN(); // NPN Trigger
    delay(100);
    currentStr += peakCurrent;
    currentStr += ",";
    trigPNP(5000); // PNP Trigger (10V)
    delay(100);
    currentStr += peakCurrent;
    currentStr += ",";
    dac.setDACOutVoltage(2500, analog); // 5v analog
    delay(100);
    trigPNP(3000); // PNP Trigger (5v)
    delay(100);
    currentStr += peakCurrent;
    dac.setDACOutVoltage(500, analog); // 1v analog
    return currentStr;
}//end contMode()

String overDrive(){
    String currentStr = "";
    dac.setDACOutVoltage(5000, analog); // 10v analog
    delay(500);
    NPNStrobe(); // NPN Strobe
    delay(500);
    currentStr += peakCurrent;
    currentStr += ",";
    PNPStrobe(5000); // PNP Strobe 10v
    delay(500);
    currentStr += peakCurrent;
    currentStr += ",";
    dac.setDACOutVoltage(2500, analog); // 5v analog
    delay(500);
    PNPStrobe(3000); // PNP Strobe 5v
    delay(500);
    currentStr += peakCurrent;
    dac.setDACOutVoltage(500, analog); // 1v analog
    return currentStr;
}//end overDrive

String multiDrive(){
    String currentStr = "";
    dac.setDACOutVoltage(5000, analog); // 10v analog
    delay(100);
    trigNPN(); // NPN Trigger
    currentStr += peakCurrent;
    currentStr += ",";
    delay(100);
    trigPNP(5000); // PNP Trigger 10v
    currentStr += peakCurrent;
    currentStr += ",";
    dac.setDACOutVoltage(2500, analog); // 5v analog
    delay(100);
    trigPNP(3000); // PNP Trigger 5v
    currentStr += peakCurrent;
    currentStr += ",";
    dac.setDACOutVoltage(0, analog); // 0v analog
    delay(500);
#ifdef DEBUG
    Serial.println("OD ON");
#endif
    NPNStrobe();
    delay(100);
    currentStr += peakCurrent;
    currentStr += ",";
    PNPStrobe(5000);
    currentStr += peakCurrent;  
#ifdef DEBUG
    Serial.println("OD OFF");
#endif
    dac.setDACOutVoltage(500, analog); // 1v analog
    return currentStr;
}//end multiDrive()

String dubOverDrive(){
    String currentStr = "";
    dac.setDACOutVoltage(0, analog);
    PNPStrobe(5000);
    currentStr += peakCurrent;
    currentStr += ",";
    delay(100);
    NPNStrobe();
    currentStr += peakCurrent;
    currentStr += ",";
    PNPStrobe(3000);
    currentStr += peakCurrent;
    return currentStr;
}//end dubOverDrive()

bool triggerCam(char mode){
    // Background Image
    Serial.write("S");
    delay(200);
    digitalWrite(camPin, HIGH);
    delay(100);
    digitalWrite(camPin, LOW);
    serialHandshake();
    //Foreground Image
    dac.setDACOutVoltage(5000, analog); // 10v analog
    Serial.write("S");
    delay(200);
    digitalWrite(NPNPin, HIGH); // Light on with NPN
    digitalWrite(camPin, HIGH);  // Camera Pulse Started
    delay(expTime);             
    digitalWrite(camPin, LOW); // Camera Pulse ended
    digitalWrite(NPNPin, LOW);  // Light Off
    serialHandshake();          // Wait for image to be grabbed
}//end triggerCam()

// - I2C Interrupt Handler
void handler(int howMany){
   //Serial.print("Data Received: ");
    int x = 0;
    while(Wire.available()) {
        byte c = Wire.read();    // Receive a byte as character
        if(c != 0x00){
            digit[x] = c;
            x++;
        }else if(c == 0x00 && x == 0){
            digit[x] = 0x3F; // set first character to 0
            x++;
        }    
    }
    digit[1] -= 0x80; // Remove colon on addition
#ifdef DEBUG
    for(int y = 0; y<4; y++){
        Serial.println(digit[y],HEX);
    }
#endif
    peakCurrent = "";
    for(int k = 0; k < 4; k++){
        switch(digit[k]){
        case 0x3F:                //Digit 0
            peakCurrent += "0";
            break;
        case 0x06:                //Digit 1
            peakCurrent += "1";
            break;
        case 0x5B:                //Digit 2
            peakCurrent += "2";
            break;
        case 0x4F:                //Digit 3
            peakCurrent += "3";
            break;
        case 0x66:                //Digit 4
            peakCurrent += "4";
            break;
        case 0x6D:                //Digit 5
            peakCurrent += "5";
            break;
        case 0x7D:                //Digit 6
            peakCurrent += "6";
            break;
        case 0x07:                //Digit 7
            peakCurrent += "7";
            break;
        case 0x7F:                //Digit 8
            peakCurrent += "8";
            break;
        case 0x6F:                //Digit 9
            peakCurrent += "9";
            break;
        default:                  //Digit '-'
            peakCurrent += "-";
            break;
        }
    }
#ifdef DEBUG
        Serial.println(peakCurrent);
#endif 
}//end handler()