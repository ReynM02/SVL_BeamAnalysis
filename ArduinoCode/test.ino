#include <DFRobot_GP8403.h>
DFRobot_GP8403 dac(&Wire,0x5F);
int NPNPin = 7; // Pin used to trigger NPN
int camPin = 4; // Pin used to trigger Camera
int expTime = 1; // Exposure time of camera; On time of light
int analog = 1; // To set analog value
int PNP = 0; // To set PNP trigger level

void setup() {
    pinMode(NPNPin, OUTPUT);
    pinMode(camPin, OUTPUT);
    digitalWrite(camPin, HIGH);
    while(dac.begin()!=0){
        delay(1000);
    }
    dac.setDACOutRange(dac.eOutputRange10V);
    //dac.outputSquare(0, 100, 0, 100, 2);
    Serial.begin(9600); // Set Baud Rate for Serial Communication
    Serial.println("Serial Started: Waiting for input");

}//end setup()

/**FUNCTION PROTOTYPES**/
// - Measurement Protocols
int contMode();     // Continuous Mode
int overDrive();    // OverDrive Mode
int multiDrive();   // MultiDrive Mode
int dubOverDrive(); // Double OverDrive Mode
// - Basic Functions
void triggerCam();


String input = "";
String outString = "";
char mode = 0;

void loop() {
  //dac.outputSquare(5000, 1, 5000, 100, 2);
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
}
// - Measurement Protocols
int contMode(){
    dac.setDACOutVoltage(5000, analog); // 10v analog
    delay(100);
    digitalWrite(NPNPin, HIGH); // light on
    Serial.println("NPN ON");
    delay(100);
    // read current at 10v on analog
    //triggerCam(); // obtain image of light on
    digitalWrite(NPNPin, LOW); // turn off light
    Serial.println("NPN OFF");
    delay(100);
    dac.setDACOutVoltage(5000, PNP); // light on PNP
    Serial.println("PNP ON");
    delay(100); // read current on PNP trigger
    dac.setDACOutVoltage(0, PNP); // light off PNP
    Serial.println("PNP OFF");
    delay(100);
    dac.setDACOutVoltage(2500, analog); // 5v analog
    digitalWrite(NPNPin, HIGH);
    Serial.println("NPN ON");
    delay(100);
    digitalWrite(NPNPin, LOW);
    Serial.println("NPN OFF");
    delay(100);
    dac.setDACOutVoltage(5000, PNP); // light on PNP
    Serial.println("PNP ON");
    delay(100); // read current on PNP trigger
    dac.setDACOutVoltage(0, PNP); // light off PNP
    Serial.println("PNP OFF");
    //delay(100);
    dac.setDACOutVoltage(500, analog); // 1v analog
    return expTime;
}//end contMode()

int overDrive(){
    return 11;
}//end overDrive

int multiDrive(){
    return 12;
}//end multiDrive()

int dubOverDrive(){
    return 13;
}//end dubOverDrive()