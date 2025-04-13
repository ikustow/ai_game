import firebase_admin
from firebase_admin import credentials, firestore
import os
from datetime import datetime
from .config import FIREBASE_CREDENTIALS
from agents_core.models import GuardianOutput, OrcOutput, LeaderOutput
from typing import Optional

cred = credentials.Certificate(FIREBASE_CREDENTIALS)
firebase_admin.initialize_app(cred)
db = firestore.client()

def save_guardian_output(data: GuardianOutput, session_id: str) -> str:
    payload = data.model_dump()
    payload["session_id"] = session_id
    payload["timestamp"] = datetime.utcnow()
    doc_ref = db.collection("guardian_outputs").add(payload)
    return doc_ref[1].id


def save_orc_output(data: OrcOutput, session_id: str) -> str:
    payload = data.model_dump()
    payload["session_id"] = session_id
    payload["timestamp"] = datetime.utcnow()
    doc_ref = db.collection("orc_outputs").add(payload)
    return doc_ref[1].id


def save_leader_output(data: LeaderOutput, session_id: str) -> str:
    payload = data.model_dump()
    payload["session_id"] = session_id
    payload["timestamp"] = datetime.utcnow()
    doc_ref = db.collection("leader_outputs").add(payload)
    return doc_ref[1].id






