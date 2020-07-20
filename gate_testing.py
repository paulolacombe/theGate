from gpiozero import MotionSensor
from gpiozero import Button
from gpiozero import Servo
import time
from datetime import date
from dbinterface import *


startTime = time.time()
today = date.today().strftime("%b-%d-%Y")
gateID = open('./id.txt', 'r').read()
occDoc, gateDoc, entrColl, transaction = db_init(today, gateID)


# Assign sensors and servo to GPIO pins on device
# entrTopSensor = MotionSensor(2, queue_len=10, threshold=0.5)  # not sure if these params are good, we can test
# exitTopSensor = MotionSensor(16, queue_len=10, threshold=0.5)
# entrSideSensor = MotionSensor(4, queue_len=50, threshold=0.5)
# exitSideSensor = MotionSensor(21, queue_len=50, threshold=0.5)
# openSwitch = Button(22, hold_time=5)
# servo = Servo(8)


# Define and assign methods to be performed when sensors detect motion
def entr_sensor_triggered():
    test_normal_entr_request()


def exit_sensor_triggered():
    test_normal_exit_request()


def emergency_button_held():
    test_emergency_open()


def entr_side_checker():
    entr_person_passed()


def exit_side_checker():
    exit_person_passed()


# entrTopSensor.when_motion = entr_sensor_triggered
# exitTopSensor.when_motion = exit_sensor_triggered
# openSwitch.when_held = emergency_button_held
forceOpen = False
sensorClear = False


# Define other methods
def open_gate(entering):  # to be completed
    # global servo
    # if entering:  # assumes that entering people need the servo to go to max
        # servo.max()
    # else:
        # servo.min()
    # entrTopSensor.when_motion = None
    # exitTopSensor.when_motion = None
    log_open(gateDoc)


def close_gate():  # to be completed
    # global servo
    # servo.mid()  # closes the gate
    # entrTopSensor.when_motion = entr_sensor_triggered
    # exitTopSensor.when_motion = exit_sensor_triggered
    log_close(gateDoc)


def test_normal_entr_request():
    print('Starting normal entr request:')
    if check_occupancy(transaction, occDoc):
        print('access granted')
        open_gate(True)
        time.sleep(2)
        entr_side_checker()
        time.sleep(3)
        close_gate()
        log_entrance(gateDoc, entrColl)
        clear_side_sensors()  # clean up the double entry checker
    else:
        print('access denied, full')
        # full_occupancy_notif()


def test_normal_exit_request():
    print('Starting normal exit request:')
    open_gate(False)
    time.sleep(2)
    exit_side_checker()
    time.sleep(3)
    close_gate()
    dec_occupancy(occDoc)
    log_exit(gateDoc, entrColl)
    clear_side_sensors()


def test_improper_entr_request():  # someone else begins entering before the first fully enters the store
    print('Starting improper entr request:')
    if check_occupancy(transaction, occDoc):
        print('access granted')
        open_gate(True)
        time.sleep(1)
        entr_side_checker()
        time.sleep(2)
        entr_side_checker()
        time.sleep(1)
        close_gate()
        log_entrance(gateDoc, entrColl)
        clear_side_sensors()  # clean up the double entry checker
    else:
        print('access denied, full')
        # full_occupancy_notif()


def test_improper_exit_request():  # someone else begins exiting before the first fully exits the store
    print('Starting improper exit request:')
    open_gate(False)
    time.sleep(2)
    exit_side_checker()
    time.sleep(2)
    exit_side_checker()
    close_gate()
    dec_occupancy(occDoc)
    log_exit(gateDoc, entrColl)
    clear_side_sensors()


def test_emergency_open():
    global forceOpen
    if forceOpen:
        close_gate()
        forceOpen = False
        # entrTopSensor.when_motion = entr_sensor_triggered
        # exitTopSensor.when_motion = exit_sensor_triggered
        log_emergency_open(gateDoc)
    else:
        open_gate(False)  # same direction as exiting
        forceOpen = True
        # entrTopSensor.when_motion = None
        # exitTopSensor.when_motion = None
        log_close(gateDoc)


def entr_person_passed():
    global sensorClear
    if not sensorClear:
        sensorClear = True
        # entrSideSensor.when_motion = entr_person_passed
    else:
        print('alarm')
        # double_entry_alarm()


def exit_person_passed():
    global sensorClear
    if not sensorClear:
        sensorClear = True
        # exitSideSensor.when_motion = exit_person_passed
    else:
        print('alarm')
        # double_entry_alarm()


def clear_side_sensors():
    global sensorClear
    sensorClear = False
    # entrSideSensor.when_no_motion = None
    # entrSideSensor.when_motion = None
    # exitSideSensor.when_no_motion = None
    # exitSideSensor.when_motion = None


# Thread to continuously update uptime
while True:
    log_time(gateDoc, time.time() - startTime)
    time.sleep(5)
    test_emergency_open()
    time.sleep(5)
    test_emergency_open()
    time.sleep(5)
    test_normal_entr_request()
    time.sleep(5)
    test_normal_entr_request()
    time.sleep(5)
    test_normal_exit_request()
    time.sleep(5)
    test_improper_entr_request()
    time.sleep(5)
    test_improper_exit_request()
    time.sleep(5)

