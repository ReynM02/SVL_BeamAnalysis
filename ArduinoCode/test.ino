//#define DEBUG // Uncomment for debug outputs

#include <DFRobot_GP8403.h> // I2C DAC
#include <SoftwareI2C.h>    // Software I2C Bus
SoftwareI2C WireS1;         // USES THESE PINS; SDA: , SCL: 37
#include <Wire.h>           // Hardware I2C Bus
DFRobot_GP8403 dac(&WireS1,0x5F);

/****GLOBAL VARIABLES****/
int NPNPin = 13; // Pin used to trigger NPN
int camPin = 4; // Pin used to trigger Camera
int analog = 1; // To set analog value
int PNP = 0; // To set PNP trigger level
int onDelay = 200; // Time light is on before taking current measurment (ms)
byte digit[4]={0,0,0,0}; // Digits recieved from peek current meter
String peakCurrent = ""; // Assembled string of peek current
String input = ""; // Input string from PC (i.e. "C100" where c=mode & 100=expTime)
String outString = ""; // String sent back to PC
char mode = 0; // Mode of light, Selects measurment protocol
int expTime = 1; // Exposure time of camera; On time of light
/************************/

/***FUNCTION PROTOTYPES***/
// - Measurement Protocols
String contMode();     // Continuous Mode
String overDrive();    // OverDrive Mode
int multiDrive();   // MultiDrive Mode
int dubOverDrive(); // Double OverDrive Mode
// - Basic Functions
void triggerCam();
/***********************/

void setup() {
    Wire.begin(0x70); // Startup Hardware I2C as slave with addr 0x70
    Wire.onReceive(handler); // Set Handler for receiving I2C
    Wire.end();
    pinMode(NPNPin, OUTPUT);
    pinMode(camPin, OUTPUT);
    digitalWrite(camPin, HIGH);
    while(dac.begin()!=0){
        delay(1000);
        Serial.print("not init");
    }
    dac.setDACOutRange(dac.eOutputRange10V);
    Serial.begin(9600); // Set Baud Rate for Serial Communication
    Serial.println("Serial Started: Waiting for input");
}//end setup()

void loop() {
    if (Serial.available() > 0){
        input = Serial.readString();
        //Serial.println(input);
        mode = input.charAt(0);
        //Serial.println(mode);
        input.remove(0,1);
        //Serial.println(input);
        expTime = input.toInt();
        Serial.println(expTime);
        if(mode != '\n'){
            switch (mode)
            {
            case 'C': // Continuous Mode
                Serial.println("Continuous");
                outString = contMode();             // Calls Continuous Measurment Protocol, Returns all Peak Current Measurments
                break;
            case 'O': // OverDrive Mode
                Serial.println("OverDrive");
                outString = overDrive();            // Calls OverDrive Measurment Protocol, Returns all Peak Current Measurments
                break;
            case 'M': // MultiDrive Mode
                Serial.println("MultiDrive");
                outString = multiDrive();           // Calls MultiDrive Measurment Protocol, Returns all Peak Current Measurments
                break;
            case 'D': // Double OverDrive Mode
                Serial.println("Double OverDrive");
                outString = dubOverDrive();         // Calls Double Overdrive Measurment Protocol, Returns all Peak Current Measurments
                break;
            default:
                Serial.println("Invalid Entry");
                outString = "Invalid Entry: 0";
                break;
            }//end switch

            Serial.println(outString); // Send Data to PC
        }//end if
        Serial.flush();
        Serial.end();
        Serial.begin(9600);
    }//end if
}//end loop()

/**USER DEFINED FUNCTIONS**/
// - Basic Functions
void triggerCam(){
    digitalWrite(camPin, LOW);
    delay(expTime);
    digitalWrite(camPin, HIGH);
}//end triggerCam()

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
    //triggerCam(); // obtain image of light on
    digitalWrite(NPNPin, LOW); // turn off light
#ifdef DEBUG
    Serial.println("NPN OFF");
#endif
}

void trigPNP(){
    dac.setDACOutVoltage(5000, PNP); // light on PNP
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

// - Measurement Protocols
String contMode(){
    String currentStr = "";
    dac.setDACOutVoltage(5000, analog); // 10v analog
    delay(200);
    trigNPN();
    delay(100);
    currentStr += peakCurrent;
    currentStr += ",";
    delay(100);
    trigPNP();
    delay(100);
    currentStr += peakCurrent;
    currentStr += ",";
    delay(100);
    dac.setDACOutVoltage(2500, analog); // 5v analog
    delay(100);
    trigNPN();
    delay(100);
    currentStr += peakCurrent;
    currentStr += ",";
    delay(100);
    trigPNP();
    delay(100);
    currentStr += peakCurrent;
    dac.setDACOutVoltage(500, analog); // 1v analog
    return currentStr;
}//end contMode()

String overDrive(){
    String currentStr = "";
    dac.setDACOutVoltage(5000, analog);
    delay(100);
    trigNPN();
    currentStr += peakCurrent;
    currentStr += ",";
    dac.setDACOutVoltage(4000, analog);
    delay(100);
    trigNPN();
    currentStr += peakCurrent;
    currentStr += ",";
    dac.setDACOutVoltage(3000, analog);
    delay(100);
    trigNPN();
    currentStr += peakCurrent;
    currentStr += ",";
    dac.setDACOutVoltage(2000, analog);
    delay(100);
    trigNPN();
    currentStr += peakCurrent;
    currentStr += ",";
    dac.setDACOutVoltage(1000, analog);
    delay(100);
    trigNPN();
    currentStr += peakCurrent;
    currentStr += ",";
    dac.setDACOutVoltage(0, analog);
    delay(1000);
#ifdef DEBUG
    Serial.println("OD ON");
#endif
    delay(1000);
    //trigNPN();
    Wire.begin(0x70);
    for(int x = 0; x < 200; x++){
            digitalWrite(NPNPin, HIGH);
            delay(2);
            digitalWrite(NPNPin, LOW);
            delay(3);
            //readCurrent();
        }
    Wire.end();
    //readCurrent();
#ifdef DEBUG
    Serial.println("OD OFF");
#endif   
    currentStr += peakCurrent;
    dac.setDACOutVoltage(0, PNP);
    return currentStr;
}//end overDrive

int multiDrive(){
    return 12;
}//end multiDrive()

int dubOverDrive(){
    return 13;
}//end dubOverDrive()

// - I2C Interrupt Handler
void handler(int howMany){
   // Serial.print("Data Received: ");
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
    //delay(100);  
    digit[1] -= 0x80; // Remove colon on addition
#ifdef DEBUG
    for(int y = 0; y<4; y++){
        //Serial.println(digit[y],HEX);
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