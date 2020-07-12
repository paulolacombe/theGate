from gpiozero import MotionSensor
from gpiozero import Button
from gpiozero import Servo
import time
from datetime import date
from dbinterface import *

startTime = time.time()
today = date.today().strftime("%b-%d-%Y")
gateID = open('./id.txt', 'r').read()
occDoc, gateDoc, transaction = db_init(today, gateID)


# Assign sensors and servo to GPIO pins on device
entrTopSensor = MotionSensor(2, queue_len=10, threshold=0.5)  # not sure if these params are good, we can test
exitTopSensor = MotionSensor(16, queue_len=10, threshold=0.5)
entrSideSensor = MotionSensor(4, queue_len=50, threshold=0.5)
exitSideSensor = MotionSensor(21, queue_len=50, threshold=0.5)
openSwitch = Button(22, hold_time=5)
servo = Servo(8)


# Define and assign methods to be performed when sensors detect motion
def entr_sensor_triggered():
    entr_request()


def exit_sensor_triggered():
    exit_request()


def emergency_button_held():
    emergency_open()


entrTopSensor.when_motion = entr_sensor_triggered
exitTopSensor.when_motion = exit_sensor_triggered
openSwitch.when_held = emergency_button_held
forceOpen = False


# Define other methods
def open_gate(entering):  # to be completed
    global servo
    if entering:  # assumes that entering people need the servo to go to max
        servo.max()
    else:
        servo.min()
    entrTopSensor.when_motion = None
    exitTopSensor.when_motion = None
    log_open(gateDoc)


def close_gate():  # to be completed
    global servo
    servo.mid()  # closes the gate
    entrTopSensor.when_motion = entr_sensor_triggered
    exitTopSensor.when_motion = exit_sensor_triggered
    log_close(gateDoc)


def entr_request():
    if check_occupancy(transaction, occDoc):  # this also increments the occupancy if it allows the person in
        print('access granted')
        open_gate(True)
        exitSideSensor.wait_for_motion(7)  # they have 7 seconds to activate the side sensor on the exit side
        if not exitSideSensor.motion_detected:  # if the wait has timed out, i.e. they didn't enter
            close_gate()
            dec_occupancy(occDoc)
            dec_total(occDoc)  # also need to decrease the TotalIn field
        else:  # if the person has begun passing through the gate
            exitSideSensor.wait_for_no_motion()  # no timeout because we don't want to close while someone is in the way
            close_gate()
            log_entrance(gateDoc)
    else:
        print('access denied, full')
        # handle sending data to screen


def exit_request():
    open_gate(False)
    entrSideSensor.wait_for_motion(7)  # they have 7 seconds to activate the side sensor on the entrance side
    if not entrSideSensor.motion_detected:
        close_gate()
    else:
        entrSideSensor.wait_for_no_motion()  # no timeout because we don't want to close while someone is in the way
        close_gate()
        dec_occupancy(occDoc)  # we wait to decrement until we're sure it was a real exit
        log_exit(gateDoc)


def emergency_open():
    global forceOpen
    if forceOpen:
        close_gate()
        forceOpen = False
        entrTopSensor.when_motion = entr_sensor_triggered
        exitTopSensor.when_motion = exit_sensor_triggered
        log_emergency_open(gateDoc)
    else:
        open_gate(False)  # same direction as exiting
        forceOpen = True
        entrTopSensor.when_motion = None
        exitTopSensor.when_motion = None
        log_close(gateDoc)


# Thread to continuously update uptime
while True:
    log_time(gateDoc, time.time() - startTime)
    time.sleep(5)
