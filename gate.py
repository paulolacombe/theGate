from gpiozero import MotionSensor
from gpiozero import Button
from gpiozero import Servo
from google.cloud import firestore
from google.oauth2 import service_account
import time


startTime = time.time()

# Set up firebase interaction
cred = service_account.Credentials.from_service_account_file('./key.json')
db = firestore.Client(u'thegate-608c2', cred)
increment = firestore.Increment(1)
decrement = firestore.Increment(-1)
occDoc = db.collection(u'Counting').document(u'Occupancy')
gateID = open('./id.txt','r').read()
gateDoc = db.collection(u'Gates').document(u'Gate-'+gateID)
if not gateDoc.get().exists:
    gateDoc.set({
        u'CountIn': 0,
        u'CountOut': 0,
        u'Status': u'Null',
        u'Uptime': time.time() - startTime
    })

# Assign sensors and servo to GPIO pins on device
pin = 1  # PLACEHOLDER, need to put in actual pin numbers once they're known
entrTopSensor = MotionSensor(pin, queue_len=10, threshold=0.5)  # not sure if these params are good, we can test
exitTopSensor = MotionSensor(pin)
entrSideSensor = MotionSensor(pin)
exitSideSensor = MotionSensor(pin)
openSwitch = Button(hold_time=5)
servo = Servo( )

# Set up transaction in the check_occupancy method
transaction = db.transaction()
@firestore.transactional
def check_occupancy(transaction):  # returns true if access is allowed and occupancy is increased, false otherwise
    snapshot = occDoc.get(transaction=transaction)
    if snapshot.get(u'curr') < snapshot.get(u'max'):
        transaction.update(occDoc, {
            u'curr': snapshot.get(u'curr') + 1
        })
        return True
    else:
        return False


# Define and assign methods to be performed when sensors detect motion
def null_trigger():
    pass


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
def open_gate():  # to be completed
    global servo
    servo.max()  # opens the gate
    entrTopSensor.when_motion = null_trigger
    exitTopSensor.when_motion = null_trigger


def close_gate():  # to be completed
    global servo
    servo.min()  # closes the gate
    entrTopSensor.when_motion = entr_sensor_triggered
    exitTopSensor.when_motion = exit_sensor_triggered


def entr_request():
    if check_occupancy(transaction):  # this also increments the occupancy if it allows the person in
        print('access granted')
        open_gate()
        exitSideSensor.wait_for_motion(7)  # they have 7 seconds to activate the side sensor on the exit side
        if not exitSideSensor.motion_detected:  # if the wait has timed out, i.e. they didn't enter
            close_gate()
            occDoc.update({
                u'curr': decrement
            })
        else:  # if the person has begun passing through the gate
            exitSideSensor.wait_for_no_motion()  # no timeout because we don't want to close while someone is in the way
            close_gate()
            log_entrance()

    else:
        print('access denied, full')
        # handle sending data to screen


def exit_request():
    open_gate()
    entrSideSensor.wait_for_motion(7)  # they have 7 seconds to activate the side sensor on the entrance side
    if not entrSideSensor.motion_detected:
        close_gate()
    else:
        entrSideSensor.wait_for_no_motion()  # no timeout because we don't want to close while someone is in the way
        close_gate()
        occDoc.update({  # we wait to decrement until we're sure it was a real exit
            u'curr': decrement
        })
        log_exit()


def emergency_open():
    global forceOpen
    if forceOpen:
        close_gate()
        forceOpen = False
        entrTopSensor.when_motion = entr_sensor_triggered
        exitTopSensor.when_motion = exit_sensor_triggered
    else:
        open_gate()
        forceOpen = True
        entrTopSensor.when_motion = null_trigger
        exitTopSensor.when_motion = null_trigger


def log_entrance():
    gateDoc.update({
        u'CountIn': increment
    })


def log_exit():
    gateDoc.update({
        u'CountIn': decrement
    })


# Script body
while True:
    pass