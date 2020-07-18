import os
from google.cloud import firestore
import threading

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "thegate-608c2-firebase-adminsdk-jd5lx-832d92f71b.json"

db = firestore.Client()


def gate_dataImport(data_collection,data_document):
    return db.collection(data_collection).document(data_document).get().to_dict()
