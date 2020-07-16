from google.cloud import firestore
from google.oauth2 import service_account


# Initialize firebase interaction
def db_init(day, gate):
    cred = service_account.Credentials.from_service_account_file('./key.json')
    db = firestore.Client(u'thegate-608c2', cred)
    occDoc = db.collection(u'Counting').document(u'Occupancy-'+day)
    if not occDoc.get().exists:
        occDoc.set({
            u'Current': 0,
            u'CurrentWait': 0,
            u'MaxOccupancy': db.collection(u'Parameters').document(u'Occupancy').get().get(u'Max'),
            u'TotalIn': 0
        })
    gateDoc = db.collection(u'Gates').document(u'Gate-'+gate)
    if not gateDoc.get().exists:
        gateDoc.set({
            u'Count': 0,
            u'Status': u'Closed',
            u'Uptime': 0
        })
    transaction = db.transaction()
    return occDoc, gateDoc, transaction


# Set up transaction in the check_occupancy method
@firestore.transactional
def check_occupancy(transaction, doc):  # returns true if access is allowed and occupancy is increased, false otherwise
    snapshot = doc.get(transaction=transaction)
    if snapshot.get(u'Current') < snapshot.get(u'MaxOccupancy'):
        transaction.update(doc, {
            u'Current': snapshot.get(u'Current') + 1,
            u'TotalIn': snapshot.get(u'TotalIn') + 1
        })
        return True
    else:
        return False


def dec_occupancy(doc):
    doc.update({
        u'Current': firestore.Increment(-1)
    })


def dec_total(doc):
    doc.update({
        u'TotalIn': firestore.Increment(-1)
    })


def log_entrance(doc):
    doc.update({
        u'Count': firestore.Increment(1)
    })


def log_exit(doc):
    doc.update({
        u'Count': firestore.Increment(-1)
    })


def log_open(doc):
    doc.update({
        u'Status': u'Open'
    })


def log_close(doc):
    doc.update({
        u'Status': u'Closed'
    })


def log_emergency_open(doc):
    doc.update({
        u'Status': u'Emergency Mode'
    })


def log_time(doc, time):
    doc.update({
        u'Uptime': time
    })


# full_occupancy_notif()
# double_entry_alarm()
