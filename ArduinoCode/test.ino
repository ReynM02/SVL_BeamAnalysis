void setup() {
  Serial.begin(9600);
  Serial.println("Serial Started: Waiting for input");
}

/**FUNCTION PROTOTYPES**/
int contMode();
int overDrive();
int multiDrive();
int dubOverDrive();

char input = 0;

void loop() {
  if (Serial.available() > 0){
    input = Serial.read();
    if(input != '\n'){
        switch (input)
        {
        case 'C':
            Serial.println("Continuous");
            break;
        case 'O':
            Serial.println("OverDrive");
            break;
        case 'M':
            Serial.println("MultiDrive");
            break;
        case 'D':
            Serial.println("Double OverDrive");
            break;
        default:
            Serial.println("Invalid Entry");
            break;
        }
    }
  }
}


/**USER DEFINED FUNCTIONS**/
int contMode(){

}

int overDrive(){

}

int multiDrive(){

}

int dubOverDrive(){

}