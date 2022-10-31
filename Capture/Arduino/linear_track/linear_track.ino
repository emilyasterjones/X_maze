/*
 * Linear track
 * If the mouse pokes at a poke that wasn't the last poke it poked at,
 * send a TTL pulse, write to Serial, and open the solenoid
 */

// Input & output pins
const int n_pokes = 2;
//order: left, right
const int IR_PINS[n_pokes] = {2,3};
const int SOLENOID_PINS[n_pokes] = {8,9};
const int TTL_PINS = A0;

// State variables
int LAST_PORT = -1; //-1 to start, 0 for left, 1 for right
int TRIAL = 1;

// Other constants
const int REW_VOL = 10; //reward, in uL
const int MS_PER_UL[n_pokes] = {20,12}; //microseconds to release 1uL of soy milk //7,8
const int OPEN_SOLENOID = 1;
const int CLOSE_SOLENOID = 0;
const int START_TTL = 1;
const int END_TTL = 0;

void setup() {
  // initialize the data stream
  Serial.begin(9600); //or 115200

  // set pin modes as input or output
  for (int poke=0; poke<n_pokes; poke++){
    pinMode(IR_PINS[poke],INPUT);
    pinMode(SOLENOID_PINS[poke],OUTPUT);

    //prime the pokes
    digitalWrite(SOLENOID_PINS[poke],OPEN_SOLENOID);
    delay(REW_VOL * MS_PER_UL[poke]);
    digitalWrite(SOLENOID_PINS[poke],CLOSE_SOLENOID);
  }

  //initial TTL
  pinMode(TTL_PINS,OUTPUT);
  //digitalWrite(TTL_PINS,START_TTL);

  //display column names for output
  char buffer[50];
  sprintf(buffer, "Trial,Time");
  Serial.println(buffer);

  //end TTL
  //digitalWrite(TTL_PINS,END_TTL);
  delay(50);
}

void loop() {
  for (int poke=0; poke<n_pokes; poke++){
    //if poke detected and it's a different port
    if (digitalRead(IR_PINS[poke])==HIGH && poke!=LAST_PORT){

      //output TTL pulse
      digitalWrite(TTL_PINS,START_TTL);

      //print trial time & number to screen
      char buffer[50];
      sprintf(buffer, "%d,%lu",TRIAL,millis());
      Serial.println(buffer);

      // open & close solenoid
      digitalWrite(SOLENOID_PINS[poke],OPEN_SOLENOID);
      delay(REW_VOL * MS_PER_UL[poke]);
      digitalWrite(SOLENOID_PINS[poke],CLOSE_SOLENOID);

      // end TTL
      digitalWrite(TTL_PINS,END_TTL);

      // advance values for next trial
      TRIAL++;
      LAST_PORT = poke;
    }
  }
}
