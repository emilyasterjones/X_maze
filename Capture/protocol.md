## Overarching Protocol
### Housing
#### General
* Reverse light/dark cycle, ideally 1-2 weeks before pre-op training. 
* Add wheel to encourage running and wood block since chewing is reduced on food dep.

#### Food restriction
**Pre-op, on day....**
* 0. Remove hopper, change cage, add restriction card.
* 0-2. 1.5g/mouse plus a weigh boat with soy milk.
* 3+. Adjust by weight.

1 day before surgery, single house without wheel. Return to free feeding, staying with food on the floor. Add gel food & water (for easy access during recovery), sprinkles (to encourage foraging), and nestlet (for heat support).

**Post-op, on day....**
* 0-3. Ad lib food.
* 4-5. 2g/mouse plus soy milk.
* 6+. Adjust by weight. Note that mice remain underweight for some time postop, so don't go below their pre-op baseline (weight of implant = 4g ~= 15% of a 25g mouse's weight)

### Training order
**Pre-op, on day.....**
* 0. Set up cage and begin food restriction. Label tails with sharpies.
* 1 & 2. Open field (OF) for 30 minutes with running wheel and lots of toys. Handle mice.
* 3+. Linear track (LT) for 20-30 minutes. Start at 25uL reward, lowering gradually to 10uL over days so mice on average get <1.5mL during tracks runs so they don't get sated.
* n+. Once mice reach 2 trials/min for 2 days, X-maze double-forced for 20-30 minutes, with same reward progression. Continue until 4 trials/min for 2 days. Optional: switch to X-maze probe, continuing until 75% correct for 2 days. Can run 2 sessions per day to speed up learning if needed.

**Post-op, on day....**
* 1-3. Record 10-20 min in OF. 
* 4+. Record HC => LT => HC => OF, 20 minutes each, until 4 trial/min or 3 days, whichever comes last. Make each recording epoch a separate trigger on the SpikeGLX file. 10uL reward for all tracks.
* n+. Substitute LT for X-maze probe. Continue until until 75% correct or 10 days, then switch to X-maze reversal, also continuing until 75% correct or 10 days.

## Daily protocol
### Set up
#### Behavior
1. Fill syringe with milk. Release valve, let descend to poke, then close again.
1. Thread tubing into solenoid. Clean poke. Open syringe valve. Fill syringe to target volume.
1. Switch on track hardware.
1. Do a test run to make sure the hardware functions are nominal. Swap out any nonfunctional components.
1. Dim lights to 5 lux. Close curtains and door.
1. Open camera in Vimba to confirm network adapter is still running. Restart computer if it isn't.
1. Remove yesterday's SpikeGLX sessions from the local drive

### Recording
#### Between animals
1. **PuTTy**: load "Arduino" settings. Under "Logging", enter the file name & location.
1. **Spyder**: set filename.
1. Wipe down the track and wheel. Reload the syringes to 5mL.
1. Weigh the next animal.

#### SpikeGLX
1. Plug in mouse: headfix with 1 screw, remove tape, release flex cable from slot, put headstage holder into slot, re-attach tape, plug flex cable into headstage, turn on LEDs.
1. Start acquisition and examine for abnormalities. Set filename.
1. Put mouse on the track next to and facing first poke.
1. Press "Enable Recording".

#### Behavior
1. Press "Open" to restart the Arduino and save all the output to the designated file. _Note: you can't have more than 1 program using the same port at once, so you can't have the Arduino IDE and PuTTy open at the same time._
1. Confirm TTL pulses appear on SpikeGLX.

#### Camera
1. Start the camera.
1. Confirm TTL pulses appear on SpikeGLX.

#### End Epoch
1. Stop video, then behavior, then recording.

#### End Session
1. Stop acquisition.
1. Put mouse back on the ball and unplug. Retape the flex slot.
1. Untwist the data cable.

### Clean up
1. Feed the mice.
1. Switch off power to track hardware. _Note: leaving solenoids plugged in for too long can cause them to fry._
1. Release tubing from solenoid. Drain milk, then rinse with water. Pump air through with plunger to dry.
1. Wipe everything again.
1. _Once a week_: Fill with ethanol/bleach and close valve. Let sit overnight.

### Troubleshooting
* **Arduino**: Check that power strip and switches are turned on and syringe valves are open. Confirm you are on the correct port and that you switched all the wiring and tubing between tasks correctly. Check that all wiring is securely connected. Try adding debug statements to the code in Arduino IDE, uploading it, and testing the task manually.
* **SpikeGLX**: If probe fails, clean the gold pins with IPA and try again.
