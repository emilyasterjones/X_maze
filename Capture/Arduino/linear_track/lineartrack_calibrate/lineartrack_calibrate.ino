#include <Servo.h>

// Input & output pins
const int n_pokes = 2;
//order: left, right
const int SOLENOID_PINS[n_pokes] = {8,9};

// Other constants
const int REW_VOL = 10; //reward, in uL
const int MS_PER_UL[n_pokes] = {20,12}; //microseconds to release 1uL of soy milk
const int OPEN_SOLENOID = 1;
const int CLOSE_SOLENOID = 0;

void setup() {
  for (int i=0; i<50; i++){
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
