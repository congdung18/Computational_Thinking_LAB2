import os
import firebase_admin
from firebase_admin import credentials, firestore
from core import config


def init_firestore():
    cred_path = config.FIREBASE_SERVICE_ACCOUNT_KEY_PATH
    if not cred_path or not os.path.exists(cred_path):
        print("WARNING: FIREBASE_SERVICE_ACCOUNT_KEY_PATH not set or file not found. Auth will fail.")
        return None

    try:
        try:
            firebase_admin.get_app()
        except ValueError:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)

        db = firestore.client()
        print("Firebase Admin and Firestore initialized successfully.")
        return db
    except Exception as exc:
        print(f"Failed to initialize Firebase Admin: {exc}")
        return None
