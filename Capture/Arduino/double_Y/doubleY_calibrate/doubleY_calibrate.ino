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
const int SOLENOID_PINS[n_pokes] = {8,9,12,13};

// Other constants
const int REW_VOL = 25; //reward, in uL
const int MS_PER_UL[n_pokes] = {14,10,16,9}; //microseconds to release 1uL of soy milk
const int OPEN_SOLENOID = 1;
const int CLOSE_SOLENOID = 0;

void setup() {
  for (int i=0; i<20; i++){
    // set pin modes as input or output
    for (int poke=0; poke<n_pokes; poke++){
      pinMode(SOLENOID_PINS[poke],OUTPUT);
      digitalWrite(SOLENOID_PINS[poke],OPEN_SOLENOID);
      delay(REW_VOL * MS_PER_UL[poke]);
      digitalWrite(SOLENOID_PINS[poke],CLOSE_SOLENOID);
    }
  }
}

void loop() {
  
}
