/*
 * DoubleY maze, training
 * Mouse starts on the left and goes to the right, has to take either the bottom 
 * or the top trajectory.
 * Ports are TL (top left), BL, TR, BR.
 * 
 * init new session: open all doors, randomly close TL+TR or BL+BR door 
 * (then experimenter puts mouse in front of left port with open door, then starts a 
 * session with the variable of which door was open)
 * 
 * loop: for each trial, wait for mouse poke at left port => reward 
 * & set right doors => wait for mouse poke at R port => reward & set  
 * randomly selected left doors
 * 
 * output:
 * trial: counting up from 1
 * time: ms since script began
 * trajectory: 0=top, 1=bottom
 * initialized: 0=poking at left (start trial), 1=poking at right (end trial)
 */
#include <Servo.h>

// Input & output pins
const int n_pokes = 4;
//order: TL (top left), BL, TR, BR
const int IR_PINS[n_pokes] = {2,3,4,7};
const int SOLENOID_PINS[n_pokes] = {8,9,12,13};
const int SERVO_PINS[n_pokes] = {5,6,10,11};
const int TTL_PINS = A0;
Servo doors[n_pokes];

// State variables
int CORRECT_ARM; //0 for top, 1 for bottom
int TRIAL = 1;
int TRIAL_INITIATED = 0;

// Other constants
const int REW_VOL = 10; //reward, in uL
const int MS_PER_UL[n_pokes] = {7/2,10/2,7*2,6*2}; //microseconds to release 1uL of soy milk //14/2,10/2,16*2,9*2 //14/2,20/2,13*2,11*2
const int OPEN_SOLENOID = 1;
const int CLOSE_SOLENOID = 0;
const int OPEN_DOOR[n_pokes] = {90,0,0,90};
const int CLOSE_DOOR[n_pokes] = {0,90,90,0};
const int START_TTL = 1;
const int END_TTL = 0;

void setup() {
  // initialize the data stream
  Serial.begin(9600); //or 115200

  // set pin modes as input or output
  for (int poke=0; poke<n_pokes; poke++){
    pinMode(IR_PINS[poke],INPUT);

    //close all solenoids
    pinMode(SOLENOID_PINS[poke],OUTPUT);
    //digitalWrite(SOLENOID_PINS[poke],CLOSE_SOLENOID);

    //open all doors
    doors[poke].attach(SERVO_PINS[poke]); //servo version of pinMode(SERVO_PINS[poke],OUTPUT);
    doors[poke].write(OPEN_DOOR[poke]); //servo version of digitalWrite(SERVO_PINS[poke],OPEN_DOOR);
  }

  CORRECT_ARM = 1;
  //randomly close top or bottom left door (incorrect arm)
  //randomSeed(analogRead(1)); //randomize the random generator
  //CORRECT_ARM = random(2);
  doors[!CORRECT_ARM].write(CLOSE_DOOR[!CORRECT_ARM]);
  doors[!CORRECT_ARM+2].write(CLOSE_DOOR[!CORRECT_ARM+2]);

  //prime correct first poke
  digitalWrite(SOLENOID_PINS[CORRECT_ARM],OPEN_SOLENOID);
  delay(REW_VOL * MS_PER_UL[CORRECT_ARM]);
  digitalWrite(SOLENOID_PINS[CORRECT_ARM],CLOSE_SOLENOID);

  //initial TTL
  pinMode(TTL_PINS,OUTPUT);
  //digitalWrite(TTL_PINS,START_TTL);

  //display column names for output
  char buffer[50];
  sprintf(buffer, "Trial,Time,Trajectory,Initiated");
  Serial.println(buffer);

  //end TTL
  //digitalWrite(TTL_PINS,END_TTL);
  delay(50); //delay so priming doesn't trigger poke
}

void loop() {
  char buffer[50];
  
  //when trial initiated by poking at open door left port
  if (digitalRead(IR_PINS[CORRECT_ARM])==HIGH && TRIAL_INITIATED==0){
    //output TTL pulse
    digitalWrite(TTL_PINS,START_TTL);

    //print trial time & number to screen
    TRIAL_INITIATED=1;
    sprintf(buffer, "%d,%lu,%d,%d",TRIAL,millis(),CORRECT_ARM,TRIAL_INITIATED);
    Serial.println(buffer);

    // deliver reward
    digitalWrite(SOLENOID_PINS[CORRECT_ARM],OPEN_SOLENOID);
    delay(REW_VOL * MS_PER_UL[CORRECT_ARM]);
    digitalWrite(SOLENOID_PINS[CORRECT_ARM],CLOSE_SOLENOID);

    //close currently open door on the right
    doors[2].write(CLOSE_DOOR[2]);
    doors[3].write(CLOSE_DOOR[3]);
    delay(500);

    //open top or bottom right door (correct arm)
    doors[CORRECT_ARM+2].write(OPEN_DOOR[CORRECT_ARM+2]);

    // end TTL
    digitalWrite(TTL_PINS,END_TTL);
  }
  
  //when mouse pokes at right side port after trial initiated
  if (digitalRead(IR_PINS[CORRECT_ARM+2])==HIGH && TRIAL_INITIATED==1){
    //output TTL pulse
    digitalWrite(TTL_PINS,START_TTL);
    TRIAL_INITIATED=0;

    //print trial time & number to screen
    sprintf(buffer, "%d,%lu,%d,%d",TRIAL,millis(),CORRECT_ARM,TRIAL_INITIATED);

    // deliver reward
    digitalWrite(SOLENOID_PINS[CORRECT_ARM+2],OPEN_SOLENOID);
    delay(REW_VOL * MS_PER_UL[CORRECT_ARM+2]);
    digitalWrite(SOLENOID_PINS[CORRECT_ARM+2],CLOSE_SOLENOID);

    Serial.println(buffer);
    
    //close currently open door on the left
    doors[CORRECT_ARM].write(CLOSE_DOOR[CORRECT_ARM]);
    delay(500);

    //randomly open top or bottom left door (correct arm)
    //randomSeed(analogRead(1)); //randomize the random generator
    //CORRECT_ARM = random(2);

     //open bottom or top trajectory, alternating every 10 trials
    if (TRIAL%10 == 0) {
      CORRECT_ARM = !CORRECT_ARM;
    }
    doors[CORRECT_ARM].write(OPEN_DOOR[CORRECT_ARM]);

    // end TTL
    digitalWrite(TTL_PINS,END_TTL);

    TRIAL++;
  }
}
