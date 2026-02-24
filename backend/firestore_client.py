"""
WASTE IQ – Firestore Client (LOCAL VERSION)
Uses firebase_key.json directly.
"""

from typing import Any, Dict, List, Optional
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_query import FieldFilter

_app = None
_db = None


def _get_db():
    global _app, _db

    if _db is not None:
        return _db

    if not firebase_admin._apps:
        cred = credentials.Certificate("firebase_key.json")
        _app = firebase_admin.initialize_app(cred)
    else:
        _app = firebase_admin.get_app()

    _db = firestore.client()
    return _db


# ── Core Helpers ─────────────────────────────────────────────

def get_doc(collection: str, doc_id: str) -> Optional[Dict]:
    ref = _get_db().collection(collection).document(doc_id)
    snap = ref.get()
    if snap.exists:
        data = snap.to_dict()
        data["_id"] = snap.id
        return data
    return None


def set_doc(collection: str, doc_id: str, data: Dict) -> str:
    _get_db().collection(collection).document(doc_id).set(data)
    return doc_id


def add_doc(collection: str, data: Dict) -> str:
    ref = _get_db().collection(collection).add(data)
    return ref[1].id


def update_doc(collection: str, doc_id: str, data: Dict) -> None:
    _get_db().collection(collection).document(doc_id).update(data)


def delete_doc(collection: str, doc_id: str) -> None:
    _get_db().collection(collection).document(doc_id).delete()


def query_collection(
    collection: str,
    filters: Optional[List[tuple]] = None,
    order_by: Optional[str] = None,
    order_desc: bool = False,
    limit: Optional[int] = None,
) -> List[Dict]:
    ref = _get_db().collection(collection)

    if filters:
        for field, op, value in filters:
            ref = ref.where(filter=FieldFilter(field, op, value))

    if order_by:
        direction = (
            firestore.Query.DESCENDING
            if order_desc
            else firestore.Query.ASCENDING
        )
        ref = ref.order_by(order_by, direction=direction)

    if limit:
        ref = ref.limit(limit)

    docs = []
    for snap in ref.stream():
        d = snap.to_dict()
        d["_id"] = snap.id
        docs.append(d)

    return docs


def increment_field(collection: str, doc_id: str, field: str, amount: int = 1) -> None:
    _get_db().collection(collection).document(doc_id).update(
        {field: firestore.Increment(amount)}
    )


def server_timestamp():
    return firestore.SERVER_TIMESTAMP