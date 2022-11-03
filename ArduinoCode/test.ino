void setup() {
  Serial.begin(9600); // Set Baud Rate for Serial Communication
  Serial.println("Serial Started: Waiting for input");
}//end setup()

/**FUNCTION PROTOTYPES - Measurement Protocols**/
int contMode();     // Continuous Mode
int overDrive();    // OverDrive Mode
int multiDrive();   // MultiDrive Mode
int dubOverDrive(); // Double OverDrive Mode

char input = 0;
String outString = "";

void loop() {
  if (Serial.available() > 0){
    input = Serial.read();
    if(input != '\n'){
        switch (input)
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


/**USER DEFINED FUNCTIONS - Measurement Protocols**/
int contMode(){
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