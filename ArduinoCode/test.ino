int NPNPin = 7; // Pin used to trigger NPN
int camPin = 4; 
int expTime = 1; // Exposure time of camera; On time of light

void setup() {
    pinMode(NPNPin, OUTPUT);
    pinMode(camPin, OUTPUT);
    digitalWrite(camPin, HIGH);
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
  if (Serial.available() > 0){
    input = Serial.readString();
    //Serial.println(input);
    mode = input.charAt(0);
    //Serial.println(mode);
    input.remove(0,1);
    //Serial.println(input);
    expTime = input.toInt();
    //Serial.println(expTime);
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
    digitalWrite(NPNPin, HIGH);
    //delay(10);
    triggerCam();
    //delay(1);
    digitalWrite(NPNPin, LOW);
    return 10;
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